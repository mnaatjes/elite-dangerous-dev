# Architecture and Language Choices

This document outlines the high-level architectural decisions regarding programming languages and how different parts of the project can interact. The goal is to leverage the strengths of different languages: C++ for performance-critical tasks and higher-level languages like Python for data processing and user interface logic.

## 1. Interacting with External Code (e.g., `id64` Algorithm)

A key challenge is integrating complex, community-reverse-engineered algorithms (like the `id64`-to-coordinate conversion) that may not have existing C++ implementations. We have three primary options for this:

### Option A: Port the Code to C++ (Recommended)

This involves a direct, line-by-line translation of the logic from a reference implementation (e.g., C# or Rust) into C++.

*   **Pros:**
    *   **Self-Contained:** The final C++ application has no external language dependencies.
    *   **Maximum Performance:** The logic runs as native C++ code.
*   **Cons:**
    *   Requires an upfront effort to translate and verify the code.

### Option B: Create a Wrapper around a Python/JS Script

This involves keeping the algorithm in a language like Python and having the C++ application call it as an external process.

*   **Pros:**
    *   Uses the existing, trusted code without translation.
    *   Easier to maintain the script in a familiar language.
*   **Cons:**
    *   **Significant Performance Overhead:** Starting a new process for each calculation is very slow and not viable for performance-critical loops.
    *   **External Dependency:** Requires the user to have a Python/Node.js interpreter installed and configured.

### Option C: Foreign Function Interface (FFI)

This involves compiling the Rust/C# code into a native shared library (`.dll` or `.so`) that the C++ application can link against and call directly.

*   **Pros:**
    *   Near-native performance without translating the core logic.
*   **Cons:**
    *   Can be complex to set up the build toolchain and the FFI bindings correctly.

**Recommendation:** For the core engine, **porting the code to C++ (Option A)** is the best long-term solution. It aligns with the goal of creating a high-performance, self-contained library.

---

## 2. Proposed Hybrid Language Architecture

We will structure the project by functionality, creating clear boundaries between components built with different languages. This plays to the strengths of both C++ and higher-level scripting languages.

### The `engine/` Directory (Must Be C++)

This directory will contain the self-contained, high-performance C++ library. This is the primary goal of our V1.0 roadmap and includes:

1.  **The Spatial Index (R-tree):** Building, loading, and querying the index with millions of points.
2.  **The Routing Algorithm (A*):** The inner loop of the pathfinder, which must be extremely fast.
3.  **Core Data Structures:** The fundamental classes (`StarSystem`, `Coordinates`) used by the engine.
4.  **`id64` and Region Logic:** The ported C++ version of community-reverse-engineered algorithms will live inside this engine.

### The `pipeline/` and `app/` Directories (Can Be Python/JS/PHP)

Other parts of the project do not have the same extreme performance requirements and are excellent candidates for languages you are more familiar with.

1.  **`app/` (The User Interface):** The main application the user interacts with. This can be a Python or JavaScript script that handles user input (e.g., "plot route from A to B") and then calls the C++ `engine` as a library to perform the calculation.
2.  **`pipeline/` (The Data Pipeline):** The entire V2.1 process for downloading, decompressing, parsing, and loading data into a database is a perfect task for **Python**. Its extensive libraries for data handling and web requests are ideal for this.
3.  **API Interaction:** Querying live APIs from services like EDSM or Inara from within the `pipeline` or `app` is significantly easier in Python or JavaScript than in C++.

This component-based architecture provides the best of both worlds: maximum performance where it counts, and the flexibility and development speed of familiar languages for the project's other parts.
