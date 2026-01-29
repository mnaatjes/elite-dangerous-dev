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
    *   **Download Procedure:** The data dumps are available at **https://www.edsm.net/dump**. Standard `wget` or `curl` commands can be used to download the desired files.

### Spansh's Guide

*   **What is it?** A highly specialized set of tools, most famous for its powerful route planners (e.g., Neutron Router, Road to Riches).
*   **Primary Data Source:** Likely a combination of EDSM data dumps, its own processing of EDDN, and user submissions.
*   **Data Provided:** While the tools are the main feature, Spansh also provides its own data dumps, often pre-filtered for specific use cases (e.g., just neutron stars, just populated systems). These are convenient for specialized applications.
*   **Accessing the Data:**
    *   **Download Procedure:** Data dumps are available as `.json.gz` files from the "Dumps" page at **https://spansh.co.uk/dumps**.

---

## Other Services & Tools

### Inara - [https://inara.cz/elite/inara-api/](https://inara.cz/elite/inara-api/)

*   **What is it?** A comprehensive player companion website and encyclopedia. Its focus is on player-centric information: tracking personal progress, finding engineers, managing materials, and viewing community goals.
*   **Accessing the Data:** Inara has a public API for targeted queries but is not a source for bulk galaxy data dumps.

### EDAstro (Elite Dangerous Astrometrics) - [https://edastro.com/mapcharts/](https://edastro.com/mapcharts/)

*   **What is it?** A website for data visualization, offering maps and charts of the galaxy.
*   **Primary Data Source:** It is a data consumer, using data from EDSM and EDDN.
*   **Accessing the Data:** It provides a specialized API for some of its datasets (like the Galactic Exploration Catalog) but does not offer bulk dumps.

### EDDiscovery

*   **What is it?** A powerful client application that players run. It reads the game journal, provides many in-app tools for explorers, and is a major contributor of data to services like EDSM and EDDN. It is a **source of data**, not a dataset provider.

### ICARUS Terminal

*   **What is it?** A "second-screen" companion app that displays information from other services like EDSM and Inara in a touch-friendly interface. It is a **data consumer**, not a provider.

### Elite Dangerous Market Connector (EDMC)

*   **What is it?** A lightweight client application that players run. Its primary purpose is to read the game journal and upload market and exploration data to the EDDN. It is a **source of data**, not a dataset provider.
