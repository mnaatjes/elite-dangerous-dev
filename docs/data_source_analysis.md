# Elite Dangerous Data Source Analysis

This document outlines the major data sources available in the Elite Dangerous community. The goal is to understand what data is available, where it comes from, how consistent it is, and how to access it.

## The Data Ecosystem: An Overview

Most third-party tools and websites exist in a symbiotic ecosystem. The flow of data generally works like this:

1.  **Player Clients:** Players run client applications like **Elite Dangerous Market Connector (EDMC)** or **EDDiscovery** alongside the game.
2.  **Data Relay (EDDN):** These clients capture live events from the game's journal file (e.g., scanning a planet, docking at a station, buying a commodity). They sanitize this data and publish it to the **Elite Dangerous Data Network (EDDN)**, a public data firehose.
3.  **Data Aggregators:** Major services like **EDSM**, **Inara**, and **Spansh** subscribe to the EDDN firehose. They consume this real-time data and combine it with their own user submissions and historical data to build their comprehensive databases.

This means that for dynamic data like market prices or faction states, the major services are generally consistent because they share the same live source (EDDN). For exploration data, EDSM is often considered the canonical source.

---

## Primary Bulk Data Providers

### EDSM (Elite Dangerous Star Map) - [https://www.edsm.net/](https://www.edsm.net/)

*   **What is it?** A massive, community-built database focused on galactic mapping and exploration data. It is often considered the most comprehensive source for star system and celestial body information as discovered by the player base.
*   **Primary Data Source:** Aggregates exploration data submitted by players via tools like EDMC and EDDiscovery. It also consumes data from EDDN.
*   **Data Provided:** Detailed system and body information (names, types, properties), faction states, station services, and player flight logs. This is the best source for a "complete picture" of the galaxy.
*   **Accessing the Data:**
    *   **Data Dumps:** EDSM provides full database dumps updated daily, including gzipped JSON files for systems, bodies, stations, etc.
    *   **Download Procedure:** The data dumps are available at **https://www.edsm.net/en/nightly-dumps**.

### Spansh's Guide - [https://spansh.co.uk/dumps](https://spansh.co.uk/dumps)

*   **What is it?** A highly specialized set of tools, most famous for its powerful route planners.
*   **Primary Data Source:** Likely a combination of EDSM data dumps, its own processing of EDDN, and user submissions.
*   **Data Provided:** Spansh provides its own data dumps, often pre-filtered for specific use cases (e.g., just neutron stars, just populated systems), which are convenient for specialized applications.

### EDAstro Map Chart Files - [https://edastro.com/mapcharts/files.html](https://edastro.com/mapcharts/files.html)

*   **What is it?** A collection of specialized datasets derived from EDSM and EDDN data, presented as downloadable files.
*   **Data Provided:** A wide variety of specific datasets, such as lists of all Earth-like worlds, systems with high body counts, etc., available as CSV or JSONL files.
*   **Use Case:** Excellent for pre-filtered, specialized datasets, which can save us from having to process the entire EDSM database for certain tasks.
*   **Schema Analysis (`systems7day.jsonl`):** The schema is highly compatible with other sources, containing the critical `id64`, `name`, and `coords` fields, along with useful pre-calculated data like `sol_dist`.

---

## API & Service Providers

This section covers services that provide data via a query-based API rather than bulk dumps.

### Inara - [https://inara.cz/elite/inara-api/](https://inara.cz/elite/inara-api/)

*   **What is it?** A comprehensive player companion website and encyclopedia.
*   **Accessing the Data:** Inara has a public API for targeted queries (e.g., looking up a specific commodity or engineer). It is not a source for bulk galaxy data.

### EDAstro API - [https://edastro.com/api-details.html](https://edastro.com/api-details.html)

*   **What is it?** An API for targeted lookups of star systems or Points of Interest from the Galactic Exploration Catalog (GEC).
*   **Accessing the Data:** The API is rate-limited and best suited for applications that need to look up specific items rather than download an entire dataset.

---

## Community Standards & Development Resources

This section covers community projects that, while not direct data sources, provide critical standards, code, or logic for interpreting galactic data.

### EDDN (Elite Dangerous Data Network) - [https://github.com/EDCD/EDDN/](https://github.com/EDCD/EDDN/)

*   **What is it?** EDDN is the real-time data "firehose" for the Elite Dangerous community. It relays live game events from players to subscribers but does not store or archive data itself.
*   **Usefulness for our Project:** Its primary value is the **`schemas/` directory (on the `live` branch)**. These JSON Schemas are the definitive, community-enforced standard for all shared data. Aligning with these schemas ensures our database is compatible with the wider ecosystem.
*   **Schema Analysis (Data Consistency):** The schemas enforce strict consistency for core system data. Any event related to a system **must** provide:
    *   `"StarSystem"` (string): The system's name.
    *   `"SystemAddress"` (integer): The unique 64-bit ID for the system (equivalent to `id64`).
    *   `"StarPos"` (array): An array of three floats `[x, y, z]` for the system's coordinates.
*   **Conclusion:** The EDDN schemas are the source of truth for data structure and consistency in the community.

### klightspeed/EliteDangerousRegionMap - [https://github.com/klightspeed/EliteDangerousRegionMap](https://github.com/klightspeed/EliteDangerousRegionMap)

*   **What is it?** A repository containing code and data to determine which of the 42 galactic regions a star system belongs to.
*   **Usefulness:** This is a key resource for porting the coordinate-to-region logic to our C++ application, allowing us to categorize systems by region.

---

## Data Source Clients

These are applications that players run to generate and submit the data that feeds the entire ecosystem. They are sources of data, but not dataset providers.

*   **EDDiscovery:** A powerful client application that reads the game journal and contributes to EDSM and EDDN.
*   **Elite Dangerous Market Connector (EDMC):** A lightweight client whose primary purpose is to upload market and exploration data to EDDN.
*   **ICARUS Terminal:** A "second-screen" companion app that primarily consumes data from other services.