from pydantic import BaseModel

class Authorization(BaseModel):
    type: str = ""
    config: str = ""