import os
import json
import shutil
from pathlib import Path
from typing import Dict, List
from models.environment import Environment

class EnvironmentManager:
    def __init__(self, base_path: str = "/app/environments"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def create_environment(self, env_name: str, env_type: str, config: Dict = None) -> Environment:
        """Create a new isolated environment"""
        env_path = self.base_path / env_name
        if env_path.exists():
            raise ValueError(f"Environment {env_name} already exists")

        env_path.mkdir()
        
        env = Environment(
            name=env_name,
            path=str(env_path),
            type=env_type,
            config=config or {}
        )

        # Initialize based on environment type
        if env_type == "python":
            self._setup_python_env(env)
        elif env_type == "nodejs":
            self._setup_nodejs_env(env)
        # Add other environment types...

        self._save_env_config(env)
        return env

    def _setup_python_env(self, env: Environment):
        """Setup Python virtual environment"""
        venv_path = Path(env.path) / "venv"
        os.system(f"python -m venv {venv_path}")
        env.config["venv_path"] = str(venv_path)
        env.config["activate_cmd"] = f"source {venv_path}/bin/activate"

    def _setup_nodejs_env(self, env: Environment):
        """Setup Node.js environment"""
        package_json = Path(env.path) / "package.json"
        if not package_json.exists():
            with open(package_json, "w") as f:
                json.dump({"name": env.name, "version": "1.0.0"}, f)
        env.config["package_manager"] = "npm"

    def _save_env_config(self, env):
        """Save environment configuration"""
        config_file = Path(env.path) / ".env_config.json"
        with open(config_file, "w") as f:
            json.dump(env.dict(), f)

    def delete_environment(self, env_name: str):
        """Delete an environment"""
        env_path = self.base_path / env_name
        if not env_path.exists():
            raise ValueError(f"Environment {env_name} does not exist")
        shutil.rmtree(env_path)

    def list_environments(self) -> List[Environment]:
        """List all available environments"""
        environments = []
        for env_dir in self.base_path.iterdir():
            if env_dir.is_dir():
                config_file = env_dir / ".env_config.json"
                if config_file.exists():
                    with open(config_file) as f:
                        env_data = json.load(f)
                        environments.append(Environment(**env_data))
        return environments
