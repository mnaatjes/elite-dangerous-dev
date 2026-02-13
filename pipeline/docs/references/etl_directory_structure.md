# ETL Directory Structure

This document outlines the recommended file system structure for organizing raw downloaded data, metadata, and processed binary output within the ETL pipeline. It distinguishes between production and testing environments to maintain clarity and efficiency.

## 1. Production Environment Structure

The production environment will use a structured hierarchy to store raw data downloads, their associated metadata, and the final processed binary files.

```
pipeline/
├── etl/
│   ├── data/
│   │   ├── raw_downloads/
│   │   │   ├── edsm/
│   │   │   │   ├── 2026/
│   │   │   │   │   ├── 01/
│   │   │   │   │   │   ├── edsm_systems_20260115-083000.json.gz
│   │   │   │   │   │   ├── edsm_systems_20260115-083000.json.gz.sha256
│   │   │   │   │   │   └── edsm_systems_20260115-083000.meta.json
│   │   │   │   │   ├── 02/
│   │   │   │   │   │   ├── edsm_systems_20260208-120000.json.gz
│   │   │   │   │   │   ├── edsm_systems_20260208-120000.json.gz.sha256
│   │   │   │   │   │   └── edsm_systems_20260208-120000.meta.json
│   │   │   │   └── spansh/
│   │   │   │       ├── 2026/
│   │   │   │       │   ├── 01/
│   │   │   │       │   │   ├── spansh_systems_20260116-100000.json.gz
│   │   │   │       │   │   ├── spansh_systems_20260116-100000.json.gz.sha256
│   │   │   │       │   │   └── spansh_systems_20260116-100000.meta.json
│   │   ├── processed_bin/
│   │   │   ├── systems_processed_edsm_20260208-120000.bin
│   │   │   └── systems_processed_edsm_20260208-120000.bin.sha256
│   │   └── logs/
│   │       └── etl_process.log
│   └── src/
│       ├── ... (ETL Python source files)
```

**Explanation:**

*   `etl/data/`: A top-level directory within the `etl` module dedicated to all data artifacts.
*   `etl/data/raw_downloads/`: Stores all raw `json.gz` files from external sources.
    *   `<source_id>/`: Sub-directories for each data source (e.g., `edsm`, `spansh`).
    *   `<year>/<month>/`: Further sub-directories based on the download year and month for easy organization and archival.
    *   Each downloaded `json.gz` file will have an accompanying `.sha256` checksum file and a `.meta.json` file.
*   `etl/data/processed_bin/`: Stores the final processed binary output files and their checksums.
    *   The binary filename will incorporate the source and timestamp for traceability (e.g., `systems_processed_edsm_20260208-120000.bin`).
*   `etl/data/logs/`: Contains the log files for the ETL process, as defined in the logging strategy.

## 2. Testing Environment Structure

The testing environment will maintain its own, separate data structure. Test data should be small, representative, and committed to version control where appropriate. Network requests should generally be mocked during testing.

```
pipeline/
├── etl/
│   ├── tests/
│   │   ├── data/
│   │   │   ├── raw_downloads/
│   │   │   │   ├── edsm/
│   │   │   │   │   ├── test_data_small.json.gz
│   │   │   │   │   ├── test_data_small.json.gz.sha256
│   │   │   │   │   └── test_data_small.meta.json
│   │   │   │   └── spansh/
│   │   │   │       ├── test_data_minimal.json.gz
│   │   │   │       ├── test_data_minimal.json.gz.sha256
│   │   │   │       └── test_data_minimal.meta.json
│   │   │   └── expected_output/
│   │   │       ├── bin/
│   │   │       │   ├── test_output_small.bin
│   │   │       │   └── test_output_small.bin.sha256
│   │   │       └── raw/
│   │   │           └── tmp/
│   │   └── ... (Test Python files)
```

**Explanation:**

*   `etl/tests/data/`: A dedicated directory for all test-related data.
*   `etl/tests/data/raw_downloads/`: Contains small, hand-crafted or truncated `json.gz` files used as input for tests. These files represent various scenarios (e.g., valid data, data with validation errors, edge cases). Each test raw download should have its own `.sha256` and `.meta.json` files for consistency.
*   `etl/tests/data/expected_output/`: Stores pre-calculated, byte-perfect binary outputs and their checksums for assertion against the actual output of the `Transformer` and `Loader` during testing. This is crucial for validating binary packing logic.
*   The `Extractor` in test mode should be configured to use these local test files instead of making live network calls.