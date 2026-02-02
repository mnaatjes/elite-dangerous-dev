import os
from .ETLConfig import ETLConfig
from .Headers import Headers
from .Endpoint import Endpoint
from etl.common import load_json
"""Loads Configuration file and creates ETLConfig Object

Keyword arguments:
argument -- filepath str
Return: ETLConfig Object
"""
def load_config(filepath):
    if not os.path.exists(filepath):
        # Validation Error Exception
        raise FileNotFoundError(f"Configuration file etl.config.json not found!\n Please ensure: {config_fp} exists!")
    
    # Capture dict data of configuration / validate
    config_data = load_json(filepath)
    if not isinstance(config_data, dict):
        raise TypeError(f"Configuration file reading error! Expects {filepath} data to be a Dict!")
    
    # Transmute into Config object
    return ETLConfig(
        name=config_data["name"],
        output_dir=config_data["output_dir"],
        download_dir=config_data["download_dir"],
        endpoints=[
            # Loop and Gather Endpoints with default values
            Endpoint(
                source_id=e.get("source_id", ""),
                url=e["url"],
                method=e.get("method", "GET"),
                headers=Headers(
                    **({"user_agent":config_data["name"]} | e.get("headers", {}))
                )
            ) for e in config_data.get("endpoints", [])
        ]
    )
