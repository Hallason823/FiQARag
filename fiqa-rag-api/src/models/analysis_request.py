from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    query: str
    search_limit: int = None