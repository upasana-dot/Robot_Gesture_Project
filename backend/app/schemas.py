from pydantic import BaseModel, Field
from typing import Optional


class TaskRequest(BaseModel):
    instruction: str = Field(min_length=5, max_length=1000)


class ActionSchema(BaseModel):
    step_number: int
    action: str
    object_name: Optional[str] = None
    target: Optional[str] = None


class PlanResponse(BaseModel):
    task_id: int
    instruction: str
    status: str
    actions: list[ActionSchema]