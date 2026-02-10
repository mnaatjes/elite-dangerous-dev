"""
    Configuration Singleton Class

"""
import os
import json
from pathlib import Path
from types import SimpleNamespace

class Config:
    # --- Properties
    _instance = None
    _initialized = False

    # Create Singleton
    def __new__(cls):
        # Check for Singleton
        if cls._instance is None:
            # Create Singleton
            cls._instance = super().__new__(cls)
            cls._instance._load()
            cls._instance.validate()
        # Return Singleton
        return cls._instance
    
    def _load(self):
        # Get ENV Variable | Default Value
        config_path = Path(os.getenv("ETL_CONFIG_PATH", "etl/etl.config.json"))
        if not config_path.exists():
            raise FileNotFoundError(f"Cannot find Configuration File at {config_path}")
        
        # Load Data and Apply Namespaces
        with open(config_path, "r") as f:
            #self.data = json.loads(f.read(), object_hook=lambda d: SimpleNamespace(**d))
            # Load dict
            raw_data = json.load(f)
            # Convert nested dicts to namespaces
            for key, val in raw_data.items():
                if isinstance(val, dict):
                    # Convert nested dict to namespaces
                    cleaned_val = json.loads(
                        json.dumps(val),
                        object_hook=lambda d: SimpleNamespace(**d)
                    )
                    setattr(self, key, cleaned_val)
                else:
                    setattr(self, key, val)

    def _validate_recursive(self, schema, data_node, path="conf"):
        # Convert SimpleNamespace to dict for key comparison
        data_keys = data_node.__dict__.keys() if hasattr(data_node, '__dict__') else {}
        
        # 1. Check for unexpected keys (The "Strict" part)
        for key in data_keys:
            if key not in schema:
                raise KeyError(f"Unexpected property found: {path}.{key}")

        # 2. Check for missing keys and types (The "Standard" part)
        for prop, expected in schema.items():
            val = getattr(data_node, prop, AttributeError)

            if val is AttributeError:
                raise KeyError(f"Missing required property: {path}.{prop}")

            # Recurse if nested
            if isinstance(expected, dict):
                self._validate_recursive(expected, val, f"{path}.{prop}")
            
            # Type check leaf nodes
            elif not isinstance(val, expected):
                raise TypeError(f"{path}.{prop} expected {expected.__name__}")
            


    def validate(self):
        """
            Validates that all expected paths provided exist and that all necessary namespaces/properties exist
        """
        # Schema for etl.config.json
        schema = {
            "version": str,
            "downloads": {
                "base_directory": str,
                "sources_filepath": str,
                "strategies": list,
                "max_chunk_size": int,
                "timestamp_format": str,
            },
            "environment": str
        }

        # Perform recursive validation
        self._validate_recursive(schema, self)

    def load_sources(self):
        # Access path
        sources_path = Path(self.downloads.sources_filepath)
        
        # Verify that sources file exists
        if not sources_path.exists():
            raise FileNotFoundError(f"Missing Sources File at {sources_path}")
        
        # Load and return
        with open(sources_path, 'r') as f:
            return json.loads(f.read(), object_hook=lambda d: SimpleNamespace(**d))

