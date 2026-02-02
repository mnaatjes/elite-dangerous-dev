from dataclasses import dataclass, field
from .Endpoint import Endpoint

@dataclass
class ETLConfig:
    name: str
    output_dir: str
    download_dir: str
    endpoints: list[Endpoint]

    def __post_init__(self):
        # Validate Name
        if not self.name:
            raise ValueError(f"ETL Configuration missing 'name'!")
    
        #Validate Endpoint urls
        for ep in self.endpoints:
            if not ep.source_id:
                raise ValueError(f"Endpoint missing 'source_id'")
            if not ep.url.startswith(("http://", "https://")):
                raise ValueError(f"Invalid URL for Endpoint {ep.source_id}\nURL: {ep.url}\n")