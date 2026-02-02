from dataclasses import dataclass
from .Headers import Headers

@dataclass
class Endpoint:
    source_id: str
    url: str
    method: str
    headers: Headers
    