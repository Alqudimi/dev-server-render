import subprocess
import logging
from pathlib import Path
from typing import List, Dict
from models.dependency import Dependency

class DependencyManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def install_dependencies(self, project_path: str, language: str, dependencies: List[str] = None) -> List[Dependency]:
        """Install dependencies for a project"""
        project_path = Path(project_path)
        
        if language == "python":
            return self._install_python_deps(project_path, dependencies)
        elif language == "nodejs":
            return self._install_nodejs_deps(project_path, dependencies)
        # Add other languages...

    def _install_python_deps(self, project_path: Path, dependencies: List[str]) -> List[Dependency]:
        """Install Python dependencies"""
        requirements_file = project_path / "requirements.txt"
        
        if dependencies:
            with open(requirements_file, "a") as f:
                for dep in dependencies:
                    f.write(f"{dep}\n")

        try:
            result = subprocess.run(
                ["pip", "install", "-r", str(requirements_file)],
                cwd=str(project_path),
                capture_output=True,
                text=True
            )
            
            installed = []
            for line in result.stdout.splitlines():
                if "Successfully installed" in line:
                    packages = line.split(" ")[2:]
                    for pkg in packages:
                        name, version = pkg.split("-")[:2]
                        installed.append(Dependency(
                            name=name,
                            version=version,
                            language="python",
                            source="pip"
                        ))
            
            return installed

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install Python dependencies: {e.stderr}")
            raise

    def _install_nodejs_deps(self, project_path: Path, dependencies: List[str]) -> List[Dependency]:
        """Install Node.js dependencies"""
        try:
            cmd = ["npm", "install"]
            if dependencies:
                cmd.extend(dependencies)
            
            result = subprocess.run(
                cmd,
                cwd=str(project_path),
                capture_output=True,
                text=True
            )
            
            installed = []
            for line in result.stdout.splitlines():
                if "added" in line and "package" in line:
                    parts = line.split(" ")
                    count = int(parts[1])
                    for i in range(count):
                        name_version = parts[2 + i].split("@")
                        installed.append(Dependency(
                            name=name_version[0],
                            version=name_version[1] if len(name_version) > 1 else "latest",
                            language="nodejs",
                            source="npm"
                        ))
            
            return installed

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install Node.js dependencies: {e.stderr}")
            raise
