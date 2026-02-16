from pydantic import BaseModel

class TaskInput(BaseModel):
    task_id: int
    data_source: str

class TaskResult(BaseModel):
    success: bool
    message: str