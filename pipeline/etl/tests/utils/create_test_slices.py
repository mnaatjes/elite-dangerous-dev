from pathlib import Path
from datetime import datetime
import gzip

def create_test_slices(source_filepath, target_dir, size_limit="1KB"):
    # Properties:
    # Define Sizes
    valid_sizes = {
        "1KB": 1024,
        "32KB": 32 * 1024,
        "1MB": 1024 * 1024
    }
    # Define filename ts
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Define base bytes written
    bytes_written = 0

    # Validate Source File
    source_filepath = Path(source_filepath)
    if not source_filepath.is_file():
        raise TypeError(f"Source File path is NOT a file! Filepath: {source_filepath}")

    # Validate Output Dir
    target_dir = Path(target_dir)
    if not target_dir.is_dir():
        raise TypeError(f"Directory {target_dir} does NOT exist!")
    
    # Define output_file
    output_file = Path(target_dir, f"{ts}.json.gz")
    # Define Size
    byte_limit = valid_sizes[size_limit]
    
    # Write
    with gzip.open(source_filepath, 'rt', encoding='utf-8') as file_in, \
        gzip.open(output_file, 'wt', encoding='utf-8') as file_out:

            #Line-by-line
            for line in file_in:
                # Break if byte limit reached
                if bytes_written >= byte_limit:
                    break
                # write
                file_out.write(line)
                bytes_written += len(line.encode('utf-8'))

    print("File Complete")
    
# Run
if __name__ == "__main__":
    ROOT_DIR    = Path("/srv/elite-dangerous-dev/pipeline")
    SOURCE_FILE = Path(ROOT_DIR, "etl/tests/data/spansh_systems_02062026_1425.json.gz")
    TARGET_DIR  = Path(ROOT_DIR, "etl/tests/data/samples/")

    try:
        create_test_slices(SOURCE_FILE, TARGET_DIR)
    except Exception as err:
        print(f"EXCEPTION: {err}")
