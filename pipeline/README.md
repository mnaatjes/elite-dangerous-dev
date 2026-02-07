# Data Pipeline

This directory contains scripts and tools for the project's data engineering tasks, forming an ETL (Extract, Transform, Load) pipeline.

## ETL Module (`etl/`)

The `etl/` subdirectory contains the primary Python-based pipeline for processing bulk data dumps (e.g., from EDSM) into a format optimized for the C++ routing engine. This pipeline is now structured using a modular class-based approach, orchestrated by `ETLProcessor` and composed of `Extractor`, `Transformer`, and `Loader` components.

Refer to the `etl/SETUP.md` guide for instructions on how to set up the Python environment and run the scripts.

## V1 Pipeline Flowchart

This flowchart visualizes the V1 data pipeline, which processes the raw data dump into a custom binary file for direct consumption by the C++ engine, bypassing the need for a database.

```mermaid
graph TD
    subgraph "Python ETL Pipeline"
        A["Start: main.py"] --> B["ETLProcessor.run()<br/>(Orchestrates)"];
        B --> C["Extractor.fetch_data()<br/>(Downloads json.gz stream)"];
        C --> D["Transformer.transform_stream()<br/>(Decompresses, parses, validates, extracts, packs)"];
        D --> E["Loader.load_data()<br/>(Writes to systems_processed.bin)"];
    end

    subgraph "C++ Routing Engine"
        E --> F["Engine loads 'systems_processed.bin'<br/>directly into memory"];
        F --> G["Build R-Tree from in-memory data"];
        G --> H["Ready for Routing"];
    end
```

---

## Testing Strategy

To ensure the reliability and correctness of the ETL pipeline, we will implement a multi-layered testing regime.

### 1. Unit Testing

*   **Purpose:** To test individual functions and logic components in isolation.
*   **Tool:** `pytest`
*   **Strategy:**
    *   **Data Processing Logic:** Use small, hand-crafted `sample_input.json` and corresponding `expected_output.bin` files. Tests will run the `Transformer.transform()` method (or equivalent) against this sample and assert byte-for-byte equality of the output.
    *   **Network Operations:** Use `pytest-mock` to mock network requests (e.g., `requests.get` within the `Extractor`) to test download logic without actual internet access.

### 2. Integration Testing

*   **Purpose:** To verify that different parts of the script (decompression, parsing, extraction, packing) work correctly together.
*   **Tool:** `pytest`
*   **Strategy:** Run the entire pipeline on a small, yet realistic, gzipped sample of the EDSM data to ensure end-to-end functionality.

### 3. Static Analysis

*   **Purpose:** To maintain code quality, consistency, and identify potential issues early.
*   **Tools:**
    *   **Linter:** `flake8`
    *   **Formatter:** `black`

### Proposed Test Directory Structure

Tests will be co-located with the `etl` module:

```
pipeline/etl/
|-- main.py
|-- requirements.txt
|-- SETUP.md
`-- tests/
    |-- data/
    |   |-- sample_input.json
    |   `-- expected_output.bin
    `-- test_processing.py
```

---

## Data Validation and Logging Strategy

### Data Validation

*   **Stage:** Validation occurs within the `Transformer` class during the **Transform stage**.
*   **Method:** As each system object is streamed from the source, the `Transformer` will perform fast, inline checks for the presence and correct type of our minimally required fields (`id64`, `name`, `coords`).
*   **Error Handling:** Any record failing validation will be skipped and a warning will be logged. This ensures that malformed data in the source dump does not halt the entire pipeline.

### Logging Strategy

Logging is handled independently by each major component of the project.

#### Python ETL Script

*   **Library:** Python's built-in `logging` module.
*   **Scope:** The `ETLProcessor` and its constituent components (`Extractor`, `Transformer`, `Loader`) will log key events such as the start and end of the process, file download status, number of records processed, number of records skipped due to validation failures, and any critical errors.
*   **Output:** Logs will be written to both the console (for interactive use) and a dedicated log file (e.g., `pipeline/etl/logs/etl_process.log`).

#### C++ Routing Engine

*   **Library:** A high-performance, dedicated C++ logging library such as **`spdlog`**. The C++ engine will **not** call out to Python for logging.
*   **Scope:** The engine will log its own critical events, such as the R-tree build time, memory usage, and details of each routing query performed (start, end, time taken).
*   **Output:** Logs will be written to the console and/or a dedicated engine log file.
