from typing import Literal
from pydantic import BaseModel, Field

class QuestionClassification(BaseModel):
    in_domain: bool
    category: Literal["PERSONAL_FINANCE", "INVESTING", "TAXES", "BANKING_AND_CREDIT", "BUSINESS_AND_ECONOMY", "OUT_OF_DOMAIN", "UNCLASSIFIED"]
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    contains_instructions: bool = False
    reason: str = Field(default="", max_length=300)

    @classmethod
    def fallback(cls, reason: str) -> "QuestionClassification":
        return cls(in_domain=True, category="UNCLASSIFIED", confidence="LOW", contains_instructions=False, reason=reason)