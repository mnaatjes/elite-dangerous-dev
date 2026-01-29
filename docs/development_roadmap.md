# Development Roadmap

This document outlines the phased development roadmap for the Elite Dangerous galaxy plotter application, from an initial prototype to a scalable, database-backed system.

## Version 1.0: Pure In-Memory Prototype

This is the initial, foundational version of the application.

*   **Focus:** Develop the core C++ routing logic and spatial index (R-tree) implementation. The goal is to perfect the algorithms in a simple, controlled environment.
*   **Data Strategy:** The application will work with a single, manageable data file (e.g., `systems_neutron.json`) that can be loaded entirely into the system's RAM upon startup.
*   **Architecture:**
    1.  On startup, read the entire data file.
    2.  Build all necessary indexes (R-tree for spatial, hash maps for attributes) in memory.
    3.  All queries and routing algorithms operate on these in-memory data structures.
*   **Benefits:** This approach allows for rapid development and testing of the most algorithmically complex parts of the application. It results in a simple, self-contained executable with maximum runtime performance for the given dataset.

---

## Version 2.0: Hybrid File-Based Model (Scaling Up)

This version addresses the memory limitations of V1.0, allowing the application to handle the entire multi-gigabyte galaxy dataset without requiring a database server.

*   **Focus:** Scale the application to handle massive datasets while remaining a self-contained desktop application.
*   **Data Strategy:** This version introduces a "coarse-to-fine" search strategy. It requires a one-time pre-processing step to organize the raw galaxy data into a more queryable structure (e.g., splitting it into one file per sector).
*   **Architecture:**
    1.  For a given route, first determine the high-level "corridor" of sectors the route will likely pass through.
    2.  Selectively load only the data from the files corresponding to those sectors.
    3.  Build the in-memory indexes for this much smaller, temporary dataset.
    4.  Run the same core routing logic developed in V1.0.
*   **Benefits:** Achieves scalability and makes it feasible to route across the entire galaxy on memory-constrained machines, without adding an external database dependency.

---

## Version 2.1 / 2.2: Professional-Grade Database Architecture (Endgame)

This represents the most robust, scalable, and flexible "endgame" vision for the project. It decouples data management from the application logic.

### Version 2.1: The Data Platform

*   **Focus:** Create a dedicated and reliable "source of truth" for all galactic data. This is a classic data engineering task.
*   **Architecture:**
    1.  Ingest all bulk data from Spansh (and other sources) into a proper database (e.g., PostgreSQL with PostGIS).
    2.  Define robust tables, primary keys, and indexes (spatial and attribute-based).
    3.  Develop a separate, automated process that periodically fetches data updates to keep the database current and verified.

### Version 2.2: The Database-Backed Application

*   **Focus:** Evolve the application to leverage the dedicated data platform.
*   **Architecture:**
    1.  The application connects to the database to perform queries.
    2.  To plan a route, it sends a smart SQL query to fetch a relevant "corridor" of systems.
    3.  It takes the results of that query and builds a temporary, in-memory R-tree.
    4.  It runs the same high-speed routing logic perfected in V1.0 on this in-memory data.
*   **Benefits:** This "best of both worlds" approach combines the powerful querying and data management of a database with the raw speed of in-memory processing for the performance-critical routing task. It provides ultimate scalability and flexibility, allowing the application to easily expand with new features (e.g., trade analysis, data visualization) by leveraging the power of SQL.
