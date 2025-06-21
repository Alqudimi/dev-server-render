from pydantic import BaseModel
from datetime import datetime
from typing import Any, Dict, Optional

class Task(BaseModel):
    id: str
    type: str
    payload: Dict[str, Any]
    status: str  # queued, processing, completed, failed
    created_at: datetime
    updated_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Any] = None
