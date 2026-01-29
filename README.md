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

## Proposed Project Directory Structure

```
/
|-- bin/              # Compiled binaries and executables
|-- build/            # Build-related files (for out-of-source builds)
|-- data/             # Raw data files (e.g., from Spansh)
|   `-- spansh/
|-- docs/             # Project documentation
|-- include/          # Public headers for libraries and executables
|   `-- elite_dangerous/
|       |-- core/       # Core data structures (e.g., StarSystem, Coordinates)
|       |-- io/         # Data loading and parsing (e.g., JsonLoader)
|       |-- routing/    # Pathfinding logic (e.g., Router)
|       `-- spatial/    # Spatial indexing (e.g., R-tree wrapper)
|-- lib/              # Compiled static or dynamic libraries (.a, .so)
|-- src/              # Source code implementation (.cpp files)
|   |-- app/            # Main application source (e.g., a CLI tool)
|   |   `-- main.cpp
|   |-- core/           # Implementation of core data structures
|   |-- io/             # Implementation of I/O logic
|   |-- routing/        # Implementation of pathfinding algorithms
|   `-- spatial/        # Implementation of the spatial index
|-- tests/            # Unit and integration tests
|   |-- core/
|   |-- io/
|   |-- routing/
|   `-- spatial/
|-- third_party/      # External libraries (e.g., JSON parsers, spatial libs)
|-- .gitignore
|-- CMakeLists.txt      # Root CMake build script
`-- README.md
```

### Rationale and Division of Responsibilities

This structure is designed to be modular and addresses the key points from your requirements document:

*   **Separation of Concerns:** The core logic is decoupled from the main application. Each directory under `src/` and `include/` represents a distinct module with a single responsibility.
    *   **`src/io`**: Handles **Input Data Handling**. Its job is to read and parse the JSON data, dealing with compression and memory-efficient streaming.
    *   **`src/spatial`**: Manages **Data Querying**. This module will contain the R-tree or other spatial index, providing a clean API to query for star systems.
    *   **`src/routing`**: Implements the **Routing and Pathfinding** logic. It will use the `spatial` module to find nearby nodes and calculate routes.
    *   **`src/core`**: Contains the fundamental data types (like a `StarSystem` class) used by all other modules.
    *   **`src/app`**: This is the user-facing part of the application. It orchestrates the other modules to perform a task (e.g., takes start/end points from the user and uses the `routing` module to print a route).

*   **Public vs. Private Code:**
    *   **`include/`** contains the "public" headers. These define the interfaces for your modules. Other modules should only interact via these headers.
    *   **`src/`** contains the "private" implementation details. If you change the code in a `.cpp` file here, as long as the corresponding header in `include/` doesn't change, other modules won't be affected.

*   **Extensibility:** This design is highly extensible. If you need new functionality, you can add a new module (e.g., `src/analytics`, `include/elite_dangerous/analytics`) without breaking existing code. This directly addresses requirement #4.

*   **Build & Dependency Management:**
    *   **`build/`**: Using an "out-of-source" build directory keeps your main project folder clean from build artifacts.
    *   **`third_party/`**: Provides a standard location for any external libraries you might vendor into the project, like a specific JSON parser or a pre-compiled library.
    *   **`CMakeLists.txt`**: This is the standard for building modern C++ projects. It will define how to build each module into a library and then link them together to create the final executable in `bin/`.

This structure provides a solid foundation for building a complex application, making it easier to develop, test, and maintain over time.
