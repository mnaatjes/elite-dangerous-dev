from dataclasses import dataclass

@dataclass
class Headers:
    user_agent: str
    accept: str = "application/json, application/x-gzip"
    accept_encoding: str = "gzip, defalte, br, json"
    connection: str = "keep-alive"
    cache_control: str = "no-cache"
