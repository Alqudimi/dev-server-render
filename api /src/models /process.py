from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class ProcessInfo(BaseModel):
    pid: int
    command: str
    working_dir: str
    status: str  # running, stopped, finished, failed
    start_time: datetime
    end_time: Optional[datetime] = None
    return_code: Optional[int] = None
    output: Optional[str] = None
    error: Optional[str] = None
