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
    *   **Download Procedure:** The data dumps are available at **https://www.edsm.net/en/nightly-dumps**. Standard `wget` or `curl` commands can be used to download the desired files.

    *   **Available Dumps Summary:** The following `.json.gz` files are available:
        *   **Systems Data:**
            *   `systemsWithCoordinates.json.gz`: The main file, containing all systems with known 3D coordinates.
            *   `systemsWithoutCoordinates.json.gz`: Systems known to exist but whose coordinates have not yet been triangulated.
            *   `systemsPopulated.json.gz`: A subset of systems that have a non-zero population.
            *   `systemsWithCoordinates7days.json.gz`: A smaller file containing only systems added or updated in the last 7 days.
        *   **Stations & Powerplay:**
            *   `stations.json.gz`: A complete list of all stations, outposts, fleet carriers, and planetary ports.
            *   `systemsPowerplay.json.gz`: Systems aligned with a PowerPlay figure, used for tracking political influence.
        *   **Exploration Data:**
            *   `bodies7days.json.gz`: Celestial bodies (planets, stars) that have been scanned and submitted in the last 7 days. A full dump of all bodies is not available, likely due to its extreme size.
            *   `codex.json.gz`: A list of all unique codex entries discovered by players (e.g., specific lifeforms or geological features).

### Spansh's Guide

*   **What is it?** A highly specialized set of tools, most famous for its powerful route planners (e.g., Neutron Router, Road to Riches).
*   **Primary Data Source:** Likely a combination of EDSM data dumps, its own processing of EDDN, and user submissions.
*   **Data Provided:** While the tools are the main feature, Spansh also provides its own data dumps, often pre-filtered for specific use cases (e.g., just neutron stars, just populated systems). These are convenient for specialized applications.
*   **Accessing the Data:**
    *   **Download Procedure:** Data dumps are available as `.json.gz` files from the "Dumps" page at **https://spansh.co.uk/dumps**.
    *   **Analyzed Dumps:**
        *   `systems_neutron.json.gz`: Contains only systems with a neutron star, black hole, or white dwarf. Confirms `id64`, `name`, `coords`, and `mainStar` attributes.
        *   `systems_1month.json.gz`: Contains all system types updated in the last month. Also confirms the same attribute structure.

---

## Other Services & Tools

### Inara - [https://inara.cz/elite/inara-api/](https://inara.cz/elite/inara-api/)

*   **What is it?** A comprehensive player companion website and encyclopedia. Its focus is on player-centric information: tracking personal progress, finding engineers, managing materials, and viewing community goals.
*   **Accessing the Data:** Inara has a public API for targeted queries but is not a source for bulk galaxy data dumps.

### EDAstro (Elite Dangerous Astrometrics) - [https://edastro.com/mapcharts/](https://edastro.com/mapcharts/)

*   **What is it?** A website for data visualization, offering maps and charts of the galaxy.
*   **Primary Data Source:** It is a data consumer, using data from EDSM and EDDN.
*   **Accessing the Data:** EDAstro provides a public API for targeted queries. It is not a source for bulk data dumps.
    *   **API Focus:** The API is primarily for retrieving information about individual star systems or points of interest from the Galactic Exploration Catalog (GEC).
    *   **Use Case:** Best suited for applications that need to look up specific items rather than download the entire dataset.
    *   **Restrictions:** The API is rate-limited (e.g., 100 requests per 15 minutes), reinforcing its use for targeted, non-bulk queries.

### EDDiscovery

*   **What is it?** A powerful client application that players run. It reads the game journal, provides many in-app tools for explorers, and is a major contributor of data to services like EDSM and EDDN. It is a **source of data**, not a dataset provider.

### ICARUS Terminal

*   **What is it?** A "second-screen" companion app that displays information from other services like EDSM and Inara in a touch-friendly interface. It is a **data consumer**, not a provider.

### Elite Dangerous Market Connector (EDMC)

*   **What is it?** A lightweight client application that players run. Its primary purpose is to read the game journal and upload market and exploration data to the EDDN. It is a **source of data**, not a dataset provider.

---

## Community Projects & Code

### klightspeed/EliteDangerousRegionMap

*   **URL:** [https://github.com/klightspeed/EliteDangerousRegionMap](https://github.com/klightspeed/EliteDangerousRegionMap)
*   **What is it?** A repository containing code and data to determine which of the 42 galactic regions a star system belongs to. It provides working implementations in Python, C#, JavaScript, and Rust.
*   **Usefulness:** This is a key resource for understanding the galactic grid. The C# and Rust implementations are clear references for porting the coordinate-to-region logic to C++.
*   **Data File:** `RegionMapData.json`
    *   **Analysis:** This file contains the pre-computed data necessary for the region-finding algorithm to work. It consists of two main parts:
        1.  `"regions"`: A simple array that maps a region ID (the array index) to the region's full name (e.g., `"The Void"`).
        2.  `"regionmap"`: A large array representing a 3D map of the galaxy. The data is compressed using **Run-Length Encoding (RLE)**. Each entry represents a "row" in the grid, with pairs of `[run_length, region_id]`. For example, `[1225, 0]` means "1225 grid cells belonging to region 0 (the void)".
    *   **How to Use:** By loading this file and implementing a C++ function to read the RLE data and convert system coordinates to a grid index, our application can determine the galactic region for any system. This would allow us to add a `region_id` foreign key to our `systems` table, which is a powerful tool for filtering and analysis.
