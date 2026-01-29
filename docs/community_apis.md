# Community APIs

This document provides a summary of known community-run APIs for Elite Dangerous, with instructions on how to use them.

## Elite Dangerous Astrometrics (EDAstro) API

EDAstro provides API access to its star system database and its Galactic Exploration Catalog (GEC) of Points of Interest (POIs).

### Registration & Authentication

The EDAstro API does not require registration or an API key for read-only access to its public endpoints.

### Rate Limiting

All API endpoints are rate-limited to **100 requests per 15-minute period**.

### Endpoints

#### Star System Data

*   **Retrieve a single star system:**
    *   URL: `https://edastro.com/api/starsystem?q={starsystem_name_or_id64}`
    *   Method: `GET`
    *   Example: `https://edastro.com/api/starsystem?q=Sol`

*   **Retrieve multiple star systems:**
    *   URL: `https://edastro.com/api/starsystem?q={system1},{system2},...`
    *   Method: `GET`
    *   Note: A maximum of 10 systems can be requested at once.
    *   Example: `https://edastro.com/api/starsystem?q=Sol,Achenar`

#### Galactic Exploration Catalog (GEC) POI Data

*   **List all GEC POIs:**
    *   URL: `https://edastro.com/gec/json/all`
    *   Method: `GET`
    *   Format: EDSM GMP-JSON

*   **List all GEC + GMP POIs combined:**
    *   URL: `https://edastro.com/gec/json/combined`
    *   Method: `GET`
    *   Note: The `id` field is not unique. A combination of `source` and `id` is required for a unique identifier.

*   **List all "rare" POIs:**
    *   URL: `https://edastro.com/gec/json/rare`
    *   Method: `GET`

*   **Get POI by ID:**
    *   URL: `https://edastro.com/gec/json/single/{poi_id}`
    *   Method: `GET`
    *   Example: `https://edastro.com/gec/json/single/1`

*   **Get POI by system id64:**
    *   URL: `https://edastro.com/gec/json/id64/{id64}`
    *   Method: `GET`
    *   Example: `https://edastro.com/gec/json/id64/10477373803`

*   **Get nearest POI to coordinates:**
    *   URL: `https://edastro.com/gec/json/nearest/{x}/{y}/{z}`
    *   Method: `GET`
    *   Example: `https://edastro.com/gec/json/nearest/0/0/0`

*   **Get nearest POI with minimum rating:**
    *   URL: `https://edastro.com/gec/json/nearest/{x}/{y}/{z}/{min_rating}`
    *   Method: `GET`

*   **Get a user's favorites:**
    *   URL: `https://edastro.com/gec/json/favorites/{user_id_or_name}`
    *   Method: `GET`

*   **Get POI categories:**
    *   URL: `https://edastro.com/gec/json/categories`
    *   Method: `GET`

*   **Get POI stats:**
    *   URL: `https://edastro.com/gec/json/stats`
    *   Method: `GET`
