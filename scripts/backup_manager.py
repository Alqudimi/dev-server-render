import os
import tarfile
import datetime
import boto3
from typing import Optional
from pathlib import Path
import subprocess
import logging
from configs.backup_config import BackupConfig

class BackupManager:
    def __init__(self, config: BackupConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        if self.config.s3_enabled:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.config.s3_access_key,
                aws_secret_access_key=self.config.s3_secret_key,
                region_name=self.config.s3_region
            )

    def create_backup(self, backup_type: str = "full"):
        """Create a backup of specified type"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{backup_type}_{timestamp}.tar.gz"
        backup_path = Path(self.config.local_storage_path) / backup_name
        
        try:
            with tarfile.open(backup_path, "w:gz") as tar:
                # Backup projects
                if backup_type in ["full", "projects"]:
                    tar.add("/app/projects", arcname="projects")
                
                # Backup databases
                if backup_type in ["full", "database"]:
                    self._backup_database()
                    tar.add("/app/backups/db_dump.sql", arcname="database/db_dump.sql")
                
                # Backup configurations
                if backup_type in ["full", "configs"]:
                    tar.add("/app/configs", arcname="configs")
            
            self.logger.info(f"Created backup: {backup_path}")
            
            # Upload to S3 if enabled
            if self.config.s3_enabled:
                self._upload_to_s3(backup_path, backup_name)
            
            return backup_path
        
        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
            raise

    def _backup_database(self):
        """Create database dump"""
        dump_path = Path("/app/backups/db_dump.sql")
        dump_path.parent.mkdir(exist_ok=True)
        
        cmd = [
            "pg_dump",
            "-h", self.config.db_host,
            "-U", self.config.db_user,
            "-d", self.config.db_name,
            "-f", str(dump_path)
        ]
        
        env = {**os.environ, "PGPASSWORD": self.config.db_password}
        subprocess.run(cmd, env=env, check=True)

    def _upload_to_s3(self, backup_path: Path, backup_name: str):
        """Upload backup to S3"""
        try:
            self.s3_client.upload_file(
                str(backup_path),
                self.config.s3_bucket,
                f"backups/{backup_name}"
            )
            self.logger.info(f"Uploaded backup to S3: {backup_name}")
        except Exception as e:
            self.logger.error(f"S3 upload failed: {str(e)}")
            raise

    def restore_backup(self, backup_path: str):
        """Restore from a backup file"""
        try:
            with tarfile.open(backup_path, "r:gz") as tar:
                # Restore projects
                if any(name.startswith("projects/") for name in tar.getnames()):
                    shutil.rmtree("/app/projects")
                    tar.extractall("/app", members=[
                        m for m in tar.getmembers() 
                        if m.name.startswith("projects/")
                    ])
                
                # Restore database
                if any(name.startswith("database/") for name in tar.getnames()):
                    tar.extract("database/db_dump.sql", "/app/backups")
                    self._restore_database("/app/backups/db_dump.sql")
                
                # Restore configs
                if any(name.startswith("configs/") for name in tar.getnames()):
                    shutil.rmtree("/app/configs")
                    tar.extractall("/app", members=[
                        m for m in tar.getmembers() 
                        if m.name.startswith("configs/")
                    ])
            
            self.logger.info(f"Restored from backup: {backup_path}")
        
        except Exception as e:
            self.logger.error(f"Restore failed: {str(e)}")
            raise

    def _restore_database(self, dump_path: str):
        """Restore database from dump"""
        cmd = [
            "psql",
            "-h", self.config.db_host,
            "-U", self.config.db_user,
            "-d", self.config.db_name,
            "-f", dump_path
        ]
        
        env = {**os.environ, "PGPASSWORD": self.config.db_password}
        subprocess.run(cmd, env=env, check=True)
