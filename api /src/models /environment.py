from pydantic import BaseModel
from typing import Dict, Optional

class Environment(BaseModel):
    name: str
    path: str
    type: str  # python, nodejs, java, etc.
    config: Dict = {}
    active: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
