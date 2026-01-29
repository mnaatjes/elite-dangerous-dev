# Program Requirements Specification

This document outlines the draft specifications and requirements for the Elite Dangerous galaxy plotting application.

## 1. Core Requirements

### 1.1. Input Data Handling
*   **Requirement:** The application must be able to ingest star system data from a JSON file.
*   **Considerations:**
    *   The input file may be compressed (e.g., `.gz`, `.bz2`). The application should handle decompression automatically.
    *   The JSON data can be very large (many gigabytes). The parsing strategy must be memory-efficient, likely using a streaming JSON parser to avoid loading the entire file into memory at once.

### 1.2. Data Querying
*   **Requirement:** The application must provide a mechanism to query for specific points or regions within the dataset quickly and efficiently.
*   **Considerations:**
    *   This is critical for finding start/end points for a route, or for finding all systems within a certain radius.
    *   A simple linear scan of the dataset will be too slow. A spatial index is required.

### 1.3. Routing and Pathfinding
*   **Requirement:** For specific applications like a "neutron plotter," the system must integrate a library capable of finding the most efficient route between two points in the 3D galaxy graph.
*   **Considerations:**
    *   The routing algorithm should be efficient for large graphs (millions of nodes). The A* algorithm is a strong candidate due to its use of heuristics.
    *   The system should be flexible enough to define edge weights based on factors like Euclidean distance and to filter nodes based on attributes (e.g., `mainStar` type being a "Neutron Star").

### 1.4. Extensibility
*   **Requirement:** The system should be designed to accommodate other libraries or modules for future functionality.
*   **Considerations:**
    *   A modular architecture would allow for adding new features (e.g., different types of plotters, data analysis tools) without rewriting the core application.

## 2. Key Architectural Decisions

### 2.1. Data Storage Strategy
*   **Question:** Is storing the data in a dedicated database the best approach?
*   **Initial Analysis:**
    *   **Database (e.g., PostgreSQL with PostGIS):**
        *   **Pros:** Robust, standardized, provides powerful querying capabilities (SQL), handles transactions and data integrity. Good for concurrent access if that becomes a requirement.
        *   **Cons:** Adds an external dependency, potentially more complex to set up and manage, might be slower for pure in-memory operations compared to a custom data structure.
    *   **In-Memory/File-Based Index:**
        *   **Pros:** Potentially faster for a single-user application, self-contained (no external database server), simpler deployment.
        *   **Cons:** The entire index must be built and loaded into memory, which could have a long start-up time and high memory usage. Saving/loading the index to/from disk needs to be managed.

### 2.2. Data Structure for Spatial Queries
*   **Question:** What is the most efficient and stable data structure for performing these queries?
*   **Initial Analysis:**
    *   **R-tree:** This is the industry-standard data structure for spatial indexing. It is highly efficient for "all points within a radius" or "nearest neighbor" queries, which are fundamental to building a graph for routing (i.e., finding all systems within jump range). Libraries like `libspatialindex` provide robust implementations.
    *   **Raw JSON:** Storing and querying the raw JSON file directly is not a viable option for performance. It would require a full scan for every query, which is unacceptably slow for a dataset of this size.
    *   **Other Structures (k-d tree, etc.):** While other spatial trees exist, R-trees are generally preferred for their performance and robustness in real-world, non-uniformly distributed datasets like a galaxy map.

**Recommendation:** An in-memory R-tree, built from the source JSON file on application start-up and potentially cached to disk, appears to be the most promising approach for achieving fast spatial queries without the overhead of an external database.
