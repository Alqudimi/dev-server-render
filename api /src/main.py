
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import subprocess
import os
import logging
from pathlib import Path

app = FastAPI(
    title="Development Server API",
    description="API for managing development environments and projects",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)
start_monitoring()
asyncio.create_task(update_system_metrics())

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Models
class Project(BaseModel):
    name: str
    language: str
    dependencies: Optional[List[str]] = None

class Command(BaseModel):
    command: str
    working_dir: str

class Process(BaseModel):
    pid: int
    command: str
    status: str

# Helper functions
def authenticate_user(token: str = Depends(oauth2_scheme)):
    # Implement your authentication logic here
    pass

# API Endpoints
@app.post("/projects/", status_code=status.HTTP_201_CREATED)
async def create_project(project: Project, token: str = Depends(oauth2_scheme)):
    """Create a new project with specified language"""
    project_path = Path(f"/app/projects/{project.name}")
    try:
        project_path.mkdir(parents=True, exist_ok=False)
        logger.info(f"Created project: {project.name}")
        
        # Initialize project based on language
        if project.language == "python":
            (project_path / "requirements.txt").touch()
            (project_path / "main.py").touch()
        elif project.language == "nodejs":
            subprocess.run(["npm", "init", "-y"], cwd=str(project_path))
        
        return {"message": f"Project {project.name} created successfully"}
    except FileExistsError:
        raise HTTPException(
            status_code=400,
            detail="Project already exists"
        )

@app.post("/projects/{project_name}/execute")
async def execute_command(project_name: str, cmd: Command, token: str = Depends(oauth2_scheme)):
    """Execute a command in the project directory"""
    project_path = Path(f"/app/projects/{project_name}")
    if not project_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    
    try:
        result = subprocess.run(
            cmd.command.split(),
            cwd=str(project_path / cmd.working_dir),
            capture_output=True,
            text=True
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.websocket("/ws/terminal/{project_name}")
async def websocket_terminal(websocket: WebSocket, project_name: str):
    terminal = TerminalWebSocket(websocket)
    await terminal.connect()
    try:
        await asyncio.gather(
            terminal.receive_commands(),
            terminal.send_output()
        )
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await terminal.disconnect()
@app.get("/projects/{project_name}/dependencies")
async def get_dependencies(project_name: str, token: str = Depends(oauth2_scheme)):
    """Get project dependencies based on language"""
    project_path = Path(f"/app/projects/{project_name}")
    if not project_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    
    # Check for language specific dependency files
    if (project_path / "requirements.txt").exists():
        with open(project_path / "requirements.txt") as f:
            return {"language": "python", "dependencies": f.read().splitlines()}
    elif (project_path / "package.json").exists():
        with open(project_path / "package.json") as f:
            return {"language": "nodejs", "dependencies": f.read()}
    
    return {"message": "No dependencies file found"}

# 
