# Database and JSON Schema Documentation

This document will track the schemas for our data sources as they are analyzed. The goal is to define a clean, relational structure for a potential database (as outlined in V2.1/V2.2 of the roadmap) and to understand the full scope of available data attributes.

This is a living document and will be updated as more data sources are audited.

---

## 1. EDSM Data Schema

*Source: EDSM Nightly Dumps (`systemsWithCoordinates.json`, `stations.json`, etc.)*

### 1.1. `systems` Table

This table contains one entry for each star system.

| Column Name   | Data Type     | Primary Key | Notes                                             |
|---------------|---------------|-------------|---------------------------------------------------|
| `id`          | `BIGINT`      | **Yes**     | EDSM's internal ID for the system.                |
| `id64`        | `BIGINT`      |             | 64-bit system address.                            |
| `name`        | `VARCHAR(255)`|             | Name of the system. Should be indexed.            |
| `coord_x`     | `DOUBLE`      |             | X coordinate.                                     |
| `coord_y`     | `DOUBLE`      |             | Y coordinate.                                     |
| `coord_z`     | `DOUBLE`      |             | Z coordinate.                                     |
| `date`        | `DATETIME`    |             | Last update time in EDSM.                         |
| `...`         | `...`         |             | *(More attributes to be added as they are identified)* |

*(A spatial index would be created on the `coord_x, coord_y, coord_z` columns.)*

### 1.2. `stations` Table

This table contains information about all stations, fleet carriers, and outposts.

| Column Name   | Data Type     | Primary Key | Notes                                             |
|---------------|---------------|-------------|---------------------------------------------------|
| `id`          | `BIGINT`      | **Yes**     | EDSM's internal ID for the station.               |
| `marketId`    | `BIGINT`      |             | In-game market ID.                                |
| `systemId`    | `BIGINT`      |             | Foreign key to the `systems` table (`systems.id`).|
| `name`        | `VARCHAR(255)`|             | Name of the station.                              |
| `type`        | `VARCHAR(255)`|             | e.g., "Coriolis Starport", "Fleet Carrier", etc.  |
| `...`         | `...`         |             | *(Services, allegiances, etc. to be added)*       |

### 1.3. `bodies` Table

This table will contain information about planets, stars, etc.

| Column Name   | Data Type     | Primary Key | Notes                                             |
|---------------|---------------|-------------|---------------------------------------------------|
| `id`          | `BIGINT`      | **Yes**     | EDSM's internal ID for the body.                  |
| `systemId`    | `BIGINT`      |             | Foreign key to the `systems` table.               |
| `name`        | `VARCHAR(255)`|             | Name of the body.                                 |
| `type`        | `VARCHAR(255)`|             | e.g., "Star", "Planet"                            |
| `subType`     | `VARCHAR(255)`|             | e.g., "F-type star", "Water world"                |
| `...`         | `...`         |             | *(Orbital parameters, materials, etc. to be added)*|

---

## 2. Spansh Data Schema

*Source: Spansh Data Dumps (`systems_neutron.json`)*

*(Schema to be documented here after further analysis.)*
