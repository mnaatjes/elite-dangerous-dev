# Utility / Helper functions for ETL tests
import os
import json

def load_json(filepath):
    """
    Load a JSON file from the sample_data directory.

    Args:
        filepath (str): Path to json file. Must contain extension!

    Returns:
        dict: The loaded JSON data.
    """
    
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data