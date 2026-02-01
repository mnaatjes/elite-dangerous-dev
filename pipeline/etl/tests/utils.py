# Utility / Helper functions for ETL tests
import os
import json

def load_json(filename):
    """
    Load a JSON file from the sample_data directory.

    Args:
        filename (str): The name of the JSON file to load.

    Returns:
        dict: The loaded JSON data.
    """
    fp = os.path.join(os.path.dirname(__file__), 'sample_data', filename)
    print(f"Filepath: {fp}")
    with open(fp, 'r') as file:
        data = json.load(file)
    return data
