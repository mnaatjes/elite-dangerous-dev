"""Constants and ENUMS for ETL Project-Wide"""

from enum import StrEnum

# --- Schema Validation Enums ---
class ETLProcess(StrEnum):
    DOWNLOADS   = "downloads"
    PROCESSING  = "processing"
    INGESTION   = "ingestion"
    VALIDATION  = "validation"

class ETLDomain(StrEnum):
    STATIONS    = "stations"
    SYSTEMS     = "systems"
    BODIES      = "bodies"
    COMMODITIES = "commodities"
    ROUTES      = "routes"
    NEUTRON     = "neutron"