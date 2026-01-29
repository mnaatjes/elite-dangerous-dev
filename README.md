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

This project is organized by functionality, separating the high-performance C++ engine from the data pipeline and user-facing application, which can be written in higher-level languages like Python.

```
/
|-- app/              # The user-facing application (e.g., Python CLI)
|   |-- main.py
|   `-- requirements.txt
|
|-- engine/           # The C++ high-performance routing engine
|   |-- include/
|   |   `-- elite_router/
|   |-- src/
|   |-- tests/
|   `-- CMakeLists.txt
|
|-- pipeline/         # Python scripts for the data pipeline (ETL)
|   |-- scripts/
|   |-- tests/
|   `-- requirements.txt
|
|-- data/             # Raw, unprocessed data (as before)
|-- docs/             # Documentation (as before)
|-- .gitignore
`-- README.md
```

### Rationale and Division of Responsibilities

*   **`engine/`**: Contains the self-contained, high-performance C++ routing engine. This includes all C++ source (`src/`), public headers (`include/`), and tests. It can be built and tested independently of the other components.
*   **`pipeline/`**: Contains all Python scripts and resources related to the V2.1 data pipeline. This includes scripts for downloading, parsing, cleaning, and loading data into a database.
*   **`app/`**: Contains the main user-facing application. This can be a simple Python script that imports and calls the C++ `engine` as a library to perform routing calculations, while handling all user interaction itself.
*   **Separation of Concerns:** This component-based architecture creates a clear separation of responsibilities, allowing for independent development and testing of each part of the project.
