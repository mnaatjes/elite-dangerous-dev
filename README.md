# Elite Dangerous Development

This repository is for development related to Elite Dangerous.

## Data Setup

The routing application requires a data file containing star system information. Due to its size, the data file is not tracked in this repository.

To download and decompress the required data, follow these steps:

1.  **Create the data directory:**
    ```bash
    mkdir -p data/spansh/dumps
    ```

2.  **Download the neutron systems data (154M):**
    ```bash
    wget -O data/spansh/dumps/systems_neutron.json.gz https://downloads.spansh.co.uk/systems_neutron.json.gz
    ```

3.  **Decompress the file:**
    ```bash
    gunzip -k data/spansh/dumps/systems_neutron.json.gz
    ```

## Project Directory Structure

This project is organized by functionality, separating the high-performance C++ engine from the data pipeline and user-facing application.

```
/
|-- app/              # User-facing application
|
|-- engine/           # High-performance C++ routing engine
|   |-- include/
|   |-- src/
|   `-- tests/
|
|-- pipeline/         # Scripts for the data pipeline (ETL)
|   |-- etl/
|   |   |-- process_data.py   # Main Python script for data processing
|   |   |-- requirements.txt  # Python dependencies
|   |   |-- SETUP.md          # Guide for setting up the Python environment
|   |   `-- output/           # Default location for generated data files
|   `-- README.md
|
|-- data/             # Raw, unprocessed data
|-- docs/             # Project documentation
|-- third_party/      # Third-party source code and libraries
|-- .gitignore
`-- README.md
```

### Rationale and Division of Responsibilities

*   **`engine/`**: Contains the self-contained, high-performance C++ routing engine. It can be built and tested independently.
*   **`pipeline/`**: Contains all Python scripts and resources related to the data pipeline. Its primary role is to download, parse, and transform raw data into an optimized format for the C++ `engine`.
*   **`app/`**: Contains the main user-facing application, which will use the `engine` to perform its core logic.
*   **Separation of Concerns:** This component-based architecture creates a clear separation of responsibilities, allowing for independent development and testing of each part of the project.
