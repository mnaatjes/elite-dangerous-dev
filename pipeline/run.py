from etl.main import run_etl_pipeline
"""
    Executes ETL Pipeline
"""

# Execution of ETL Pipeline
if __name__ == '__main__':
    print("Running ETL Pipeline...\n")
    
    ## Try and Catch Exceptions
    try:
        run_etl_pipeline()

    # File not found errors
    except FileNotFoundError as e:
        print(f" >> File Not Found: \n{e}")
    # Type Error
    except TypeError as e:
        print(f">> Type Error: \n{e}")
    #Value Error
    except ValueError as e:
        print(f" >> Value Error: \n{e}")
    #Default / Unknown Exceptions
    except Exception as e:
        print(f" >> Default Error: \n{e}")
