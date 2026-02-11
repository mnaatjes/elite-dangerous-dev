import os
import json
from pathlib import Path
from types import SimpleNamespace

class Config:
    """
    Singleton class to manage application configuration.

    This class loads configuration from a JSON file specified by the 'ETL_CONFIG_PATH'
    environment variable or defaults to 'etl/etl.config.json'. It ensures that
    only one instance of the configuration exists throughout the application lifecycle.
    The configuration data is loaded into `SimpleNamespace` objects for easy
    attribute access and is validated against a predefined schema.
    """
    _instance = None
    _initialized = False

    # Create Singleton
    def __new__(cls):
        """
        Implements the Singleton pattern for the Config class.

        Ensures that only one instance of the Config class is created and
        that subsequent calls return the same instance. It also triggers
        the loading and validation of the configuration upon the first
        instance creation.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
            cls._instance.validate()
        return cls._instance
    
    def _load(self):
        """
        Loads configuration data from a JSON file.

        The path to the configuration file is determined by the 'ETL_CONFIG_PATH'
        environment variable; if not set, it defaults to 'etl/etl.config.json'.
        The method reads the JSON file, and then iteratively converts nested
        dictionaries into `SimpleNamespace` objects, allowing configuration
        parameters to be accessed as attributes (e.g., `config.downloads.base_directory`).

        Raises:
            FileNotFoundError: If the specified configuration file does not exist.
        """
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
        """
        Recursively validates the configuration data against a predefined schema.

        This method checks for three main types of validation errors:
        1. Unexpected properties: Ensures that all properties in the `data_node`
           are defined in the `schema`.
        2. Missing required properties: Verifies that all properties specified
           in the `schema` are present in the `data_node`.
        3. Type mismatches: Checks if the value of each property in `data_node`
           matches the expected type defined in the `schema`.

        For nested configurations, it recursively calls itself to validate
        sub-schemas and their corresponding data nodes.

        Args:
            schema (dict): The part of the validation schema relevant to the current `data_node`.
                           Keys are property names, and values are either expected types (e.g., `str`, `int`, `list`)
                           or nested schema dictionaries.
            data_node (SimpleNamespace): The current configuration data object (or sub-object)
                                         being validated.
            path (str): A string representation of the current path in the configuration hierarchy,
                        used for generating informative error messages. Defaults to "conf".

        Raises:
            KeyError: If an unexpected property is found or a required property is missing.
            TypeError: If a property's value does not match its expected type.
        """
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
        Validates the entire loaded configuration against a predefined schema.

        This method defines the expected structure and types of the configuration
        parameters within 'etl.config.json'. It then initiates a recursive
        validation process via `_validate_recursive` to ensure that all required
        properties exist, are of the correct type, and that no unexpected
        properties are present in the loaded configuration.
        """
        # Schema for etl.config.json
        schema = {
            "version": str,
            "downloads": {
                "base_directory": str,
                "sources_filepath": str,
                "manifest_directory": str,
                "strategies": list,
                "max_chunk_size": int,
                "timestamp_format": str,
            },
            "environment": str
        }

        # Perform recursive validation
        self._validate_recursive(schema, self)

    def load_sources(self):
        """
        Loads and returns the sources configuration data.

        The method retrieves the file path from `self.downloads.sources_filepath`,
        verifies that the file exists, and then reads its content. The JSON
        content is parsed and returned, with nested dictionaries converted
        into `SimpleNamespace` objects for convenient attribute access.

        Returns:
            SimpleNamespace: An object containing the loaded sources configuration.

        Raises:
            FileNotFoundError: If the sources file specified in the configuration does not exist.
        """
        # Access path
        sources_path = Path(self.downloads.sources_filepath)
        
        # Verify that sources file exists
        if not sources_path.exists():
            raise FileNotFoundError(f"Missing Sources File at {sources_path}")
        
        # Load and return
        with open(sources_path, 'r') as f:
            return json.loads(f.read(), object_hook=lambda d: SimpleNamespace(**d))

