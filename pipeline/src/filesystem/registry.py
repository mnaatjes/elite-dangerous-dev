from pathlib import Path

class FilesystemRegistry:
    # For singleton behavior
    _instance = None

    def __new__(cls, **args):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
          
    def __init__(self, directory_map: dict):
        # Check for initialized instance
        if not hasattr(self, '_initialized'):
            # Validate directory_map has content
            # TODO: Ensure check for empty
            if not directory_map:
                raise ValueError("Registry must be initialized with a path map.")

            # Dir map from config dir:{downloads: /srv/...data/downloads, ...}
            self._paths = {key: Path(val) for key, val in directory_map.items()}
            
            # Set _initialized
            self._initialized = True

    def resolve(self, key) -> Path:
         # Throws KeyError if the key doesn't exist
        return self._paths[key]