from pathlib import Path
from typing import List, Dict, Optional
from fastapi import HTTPException

class FileBrowser:
    def __init__(self, base_path: str = "/app/projects"):
        self.base_path = Path(base_path)

    def list_files(self, path: str = "") -> List[Dict]:
        """List files and directories in a path"""
        full_path = self.base_path / path
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if not full_path.is_dir():
            raise HTTPException(status_code=400, detail="Not a directory")
        
        items = []
        for item in full_path.iterdir():
            items.append({
                "name": item.name,
                "path": str(item.relative_to(self.base_path)),
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else 0,
                "modified": item.stat().st_mtime
            })
        
        return sorted(items, key=lambda x: (x["type"], x["name"]))

    def read_file(self, file_path: str) -> str:
        """Read contents of a file"""
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if full_path.is_dir():
            raise HTTPException(status_code=400, detail="Is a directory")
        
        try:
            with open(full_path, "r") as f:
                return f.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def write_file(self, file_path: str, content: str):
        """Write content to a file"""
        full_path = self.base_path / file_path
        
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def delete_path(self, path: str):
        """Delete a file or directory"""
        full_path = self.base_path / path
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        try:
            if full_path.is_dir():
                shutil.rmtree(full_path)
            else:
                full_path.unlink()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
