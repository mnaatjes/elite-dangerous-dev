from typing import TypedDict

class MetadataArgs(TypedDict):
    source:str
    service:str
    dataset:str
    timestamp:str
    version:str
    extension:str