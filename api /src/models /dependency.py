from pydantic import BaseModel

class Dependency(BaseModel):
    name: str
    version: str
    language: str
    source: str  # pip, npm, maven, etc.
    installed: bool = True
