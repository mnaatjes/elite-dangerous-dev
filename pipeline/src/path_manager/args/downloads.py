from typing import TypedDict

class DownloadsArgs(TypedDict):
    source:str
    service:str
    dataset:str
    timestamp:str
    version:str
    extension:str