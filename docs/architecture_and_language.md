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

We can structure the project to play to the strengths of multiple languages, separating the high-performance "Engine" from the higher-level "Shell" and "Tools".

### The "Engine" (Must Be C++)

The parts of the application where performance is paramount should be built as a C++ library. This is the primary goal of our V1.0 roadmap. This includes:

1.  **The Spatial Index (R-tree):** Building, loading, and querying the index with millions of points needs to be as fast as possible.
2.  **The Routing Algorithm (A*):** The inner loop of the pathfinder will execute millions of times for a long route and must be extremely fast.
3.  **Core Data Structures:** The fundamental classes (`StarSystem`, `Coordinates`) that the above components use.
4.  **`id64` and Region Logic:** The ported C++ version of these algorithms would live inside this engine.

### The "Shell" and "Tools" (Can Be Python/JS/PHP)

Many other parts of the project do not have the same extreme performance requirements and are excellent candidates for languages you are more familiar with.

1.  **The User Interface:** The main application the user interacts with can be a Python or JavaScript script. It would handle user input (e.g., "plot route from A to B"), call our C++ "Engine" to do the actual calculation, and then format and display the result.
2.  **The Data Pipeline (for V2.1):** The separate process that downloads data dumps, decompresses them, parses them, and inserts them into a database is a perfect task for **Python**. Its extensive libraries for data handling and web requests are ideal for this.
3.  **API Interaction:** Querying live APIs from services like EDSM or Inara is significantly easier and faster to develop in Python or JavaScript than in C++.

This hybrid architecture provides the best of both worlds: maximum performance where it counts, and the flexibility and development speed of familiar languages for the less performance-critical parts of the project.
