from pydantic import BaseModel
from typing import Optional

class AnalysisRequest(BaseModel):
    query: str
    task_id: str = "default_task"
    search_limit: Optional[int] = 5
    prompt_version: Optional[str] = None