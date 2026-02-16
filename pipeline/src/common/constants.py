from enum import Enum

class NamingTemplate(str, Enum):
    METADATA="meta_{source}_{service}_{dataset}_{timestamp}_{version}.json"
    DOWNLOADS="{source}_{service}_{dataset}_{timestamp}_v{version}{extension}"
    MANIFEST="manifest_{service}_{version}.json"
    LOG="etl_{service}_{timestamp}.log"
    SAMPLE="sample_{source}_{service}_{dataset}_{timestamp}_v{version}{extension}"