import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Union

class PathManager:
    """Handles the physical organization of the ETL filesystem."""
    
    def __init__(self, base_dir: Union[str, Path], strict: bool = False):
        # Ensure base_dir is a resolved Path object
        self.base_dir = Path(base_dir).resolve()
        # Side-effect allowed here to ensure the root exists
        if strict:
            # Checks that directory exists before allowing construction of class
            self._ensure_base_exists()

    def _ensure_base_exists(self):
        """Ensures the root path is valid and writable."""
        # Check exists
        if not self.base_dir.exists():
            raise NotADirectoryError(f"Base directory {self.base_dir} does NOT exist!")
        # Check Access
        if not os.access(self.base_dir, os.W_OK):
            raise PermissionError(f"Base directory {self.base_dir} is not writable.")

    # --- Resolution Methods (No Side Effects) ---

    def resolve_timestamped_dir(self) -> Path:
        """Returns the expected path based on current date: base/YYYY/MM/"""
        now = datetime.now()
        return self.base_dir / now.strftime("%Y") / now.strftime("%m")

    def resolve_full_path(self, filename: str, category: str = "downloads") -> Path:
        """Returns the full path for a file: base/YYYY/MM/filename.ext"""
        return self.resolve_timestamped_dir() / filename

    # --- Action Methods (With Side Effects) ---

    def create_timestamped_dir(self) -> Path:
        """Calculates the timestamped directory and physically creates it."""
        self._ensure_base_exists()
        path = self.resolve_timestamped_dir()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def validate_space(self, required_bytes: Optional[int]):
        """Standard check for Linux disk availability."""
        self._ensure_base_exists()
        if not required_bytes:
            return
        _, _, free = shutil.disk_usage(self.base_dir)
        if free < (required_bytes * 1.1):  # 10% safety buffer
            raise IOError(f"Insufficient disk space on {self.base_dir}")

    # --- Diagnostic Methods ---

    def where(self) -> Dict:
        """Returns a diagnostic map of current resolution logic without creating dirs."""
        return {
            "base_root": str(self.base_dir),
            "exists": self.base_dir.exists(),
            "writable": os.access(self.base_dir, os.W_OK) if self.base_dir.exists() else False,
            "resolved_dir": str(self.resolve_timestamped_dir()),
            "disk_free_gb": f"{shutil.disk_usage(self.base_dir).free / (1024**3):.2f} GB" if self.base_dir.exists() else None
        }

    def tree(self, depth: int = 2):
        """Visual representation of the Linux filesystem structure."""
        if not self.base_dir.exists():
            print(f"Directory {self.base_dir} does not exist.")
            return
        print(f"📂 {self.base_dir}")
        self._build_tree(self.base_dir, "", depth)

    def _build_tree(self, path: Path, prefix: str, depth: int):
        if depth < 0 or not path.exists():
            return
        
        try:
            items = sorted(list(path.iterdir()))
        except PermissionError:
            print(f"{prefix}└── [Permission Denied]")
            return

        for i, item in enumerate(items):
            connector = "└── " if i == len(items) - 1 else "├── "
            print(f"{prefix}{connector}{item.name}")
            if item.is_dir():
                new_prefix = prefix + ("    " if i == len(items) - 1 else "│   ")
                self._build_tree(item, new_prefix, depth - 1)