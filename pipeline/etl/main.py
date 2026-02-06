"""Main Document Script for Running the ETL Pipeline
"""
import os
import json

from etl.src.ETLProcessor import ETLProcessor

def main():
    """
        Implement ETL Processor

    """
    # Constants
    URL = "http://www."
    OUTPUT_DIR = "data"
    
    # Processor
    etl = ETLProcessor(URL, OUTPUT_DIR)

    try: 
        etl.run()
    except ValueError as e:
        print(f"Value Error: {e}")
    except Exception as e:
        print(f"Default Error: {e}")

# -- Execute ETL Program
if __name__ == "__main__":
    main()
