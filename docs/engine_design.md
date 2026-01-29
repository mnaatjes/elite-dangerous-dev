# C++ Engine Design

This document outlines the proposed file structure and high-level design for the C++ routing engine, which resides in the `engine/` directory.

## 1. File Structure and Responsibilities

The engine is broken into several modules (`core`, `io`, `spatial`, `routing`), each with a clear responsibility. The public-facing interfaces are defined in header files (`.hpp`) within `engine/include/elite_router/`, and their logic is implemented in source files (`.cpp`) within `engine/src/`.

### `engine/include/elite_router/` - Public Interfaces (Headers)
*   **`core/Coordinates.hpp`**: A simple struct to represent X, Y, Z coordinates.
*   **`core/StarSystem.hpp`**: A class/struct defining a star system, holding properties like `id64`, `name`, `coords`, etc.
*   **`io/DataLoader.hpp`**: Defines the interface for loading system data, e.g., `loadSystems(...)`.
*   **`spatial/SpatialIndex.hpp`**: Defines the interface for the spatial index (R-tree), with methods like `build(...)` and `findWithinRadius(...)`.
*   **`routing/Router.hpp`**: Defines the main routing interface, with a key method like `findRoute(...)`.

### `engine/src/` - Private Implementations (Source)
*   **`core/StarSystem.cpp`**: Implementation for the `StarSystem` class methods.
*   **`io/JsonLoader.cpp`**: Implements the `DataLoader` to parse system data from `.json` files.
*   **`spatial/RTree.cpp`**: The core implementation of the R-tree data structure for the `SpatialIndex`.
*   **`routing/AStar.cpp`**: The implementation of the A* pathfinding algorithm.
*   **`app/main.cpp`**: A simple main entry point for a standalone executable to test the engine's functionality.

---

## 2. Class Diagrams

These diagrams show the high-level relationships between the main classes in each module.

### Core Module
```mermaid
classDiagram
  class A
```

### IO Module
```mermaid
classDiagram
  direction LR
  class DataLoader {
    <<interface>>
    +loadSystems(string filePath) vector<StarSystem>
  }
  class JsonLoader {
    +loadSystems(string filePath) vector<StarSystem>
  }
  class StarSystem {
    ...
  }
  DataLoader <|.. JsonLoader : implements
  JsonLoader ..> StarSystem : creates
```

### Spatial Module
```mermaid
classDiagram
  direction LR
  class SpatialIndex {
    <<interface>>
    +build(vector<StarSystem> systems) void
    +findWithinRadius(Coordinates center, double radius) vector<long long>
  }
  class RTree {
    +build(vector<StarSystem> systems) void
    +findWithinRadius(Coordinates center, double radius) vector<long long>
  }
   class StarSystem {
    ...
  }
  SpatialIndex <|.. RTree : implements
  RTree ..> StarSystem : uses
```

### Routing Module
```mermaid
classDiagram
  direction LR
  class Router {
    <<interface>>
    +findRoute(long long startId, long long endId) vector<long long>
  }
  class AStarRouter {
    -SpatialIndex& spatialIndex
    +findRoute(long long startId, long long endId) vector<long long>
  }
  class SpatialIndex {
    <<interface>>
  }
  Router <|.. AStarRouter : implements
  AStarRouter o-- SpatialIndex : uses
```

---

## 3. Process Flowchart

This flowchart shows the typical sequence of operations when the application runs to find a route.

```mermaid
graph TD
    subgraph "Initialization Phase"
        A["main() starts"] --> B["Instantiate JsonLoader"];
        B --> C["loader.loadSystems(...)"];
        C --> D["vector<StarSystem>"];
        D --> E["Instantiate RTree as SpatialIndex"];
        E --> F["spatialIndex.build(systems)"];
        F --> G["Instantiate AStarRouter with SpatialIndex"];
    end

    subgraph "User Interaction"
        H["Get Start/End System Names from User"];
        H --> I["Look up System IDs"];
    end

    subgraph "Routing Phase"
        J["router.findRoute(startId, endId)"];
        J --> K{"A* Search Loop"};
        K -- "Find neighbors" --> L["spatialIndex.findWithinRadius(...)"];
        L -- "Returns neighbors" --> K;
        K -- "Route found" --> M["vector<long long> route"];
    end

    subgraph "Output Phase"
        N["Display Route to User"];
    end

    G --> H;
    I --> J;
    M --> N;
```
