import subprocess
import psutil
import logging
from typing import List, Dict, Optional
from threading import Lock
from models.process import ProcessInfo

class ProcessManager:
    def __init__(self):
        self.processes = {}
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)

    def start_process(self, command: str, working_dir: str, env_vars: Dict[str, str] = None) -> ProcessInfo:
        """Start a new process and track it"""
        try:
            env = None
            if env_vars:
                env = {**os.environ, **env_vars}

            process = subprocess.Popen(
                command,
                cwd=working_dir,
                shell=True,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            with self.lock:
                proc_info = ProcessInfo(
                    pid=process.pid,
                    command=command,
                    working_dir=working_dir,
                    status="running",
                    start_time=datetime.now()
                )
                self.processes[process.pid] = {
                    "process": process,
                    "info": proc_info
                }

            self.logger.info(f"Started process {process.pid}: {command}")
            return proc_info

        except Exception as e:
            self.logger.error(f"Failed to start process: {str(e)}")
            raise

    def stop_process(self, pid: int) -> bool:
        """Stop a running process"""
        with self.lock:
            if pid not in self.processes:
                return False

            proc_data = self.processes[pid]
            try:
                parent = psutil.Process(pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
                
                proc_data["info"].status = "stopped"
                proc_data["info"].end_time = datetime.now()
                self.logger.info(f"Stopped process {pid}")
                return True
            except Exception as e:
                self.logger.error(f"Error stopping process {pid}: {str(e)}")
                return False

    def list_processes(self) -> List[ProcessInfo]:
        """List all tracked processes"""
        with self.lock:
            return [data["info"] for data in self.processes.values()]

    def get_process(self, pid: int) -> Optional[ProcessInfo]:
        """Get details for a specific process"""
        with self.lock:
            if pid in self.processes:
                return self.processes[pid]["info"]
            return None

    def cleanup_processes(self):
        """Clean up finished processes"""
        with self.lock:
            to_remove = []
            for pid, data in self.processes.items():
                if data["process"].poll() is not None:  # Process finished
                    data["info"].status = "finished"
                    data["info"].end_time = datetime.now()
                    if data["process"].poll() != 0:
                        data["info"].status = "failed"
                    to_remove.append(pid)

            for pid in to_remove:
                del self.processes[pid]
