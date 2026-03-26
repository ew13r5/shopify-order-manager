from pydantic import BaseModel

class ExportTaskResponse(BaseModel):
    task_id: str
    status: str = "pending"
