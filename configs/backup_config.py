from pydantic import BaseModel
from typing import Optional

class BackupConfig(BaseModel):
    local_storage_path: str = "/app/backups"
    retention_days: int = 7
    s3_enabled: bool = False
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = None
    db_host: str = "localhost"
    db_user: str = "user"
    db_password: str = "pass"
    db_name: str = "devserver"
