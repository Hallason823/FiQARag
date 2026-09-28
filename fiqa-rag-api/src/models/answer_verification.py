from typing import List, Literal
from pydantic import BaseModel, Field

class AnswerVerification(BaseModel):
    verdict: Literal["SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_SUPPORTED", "UNVERIFIED"]
    follows_embedded_instructions: bool = False
    unsupported_claims: List[str] = Field(default_factory=list, max_length=5)
    reason: str = Field(default="", max_length=300)

    @property
    def is_rejected(self) -> bool:
        return self.verdict == "NOT_SUPPORTED" or self.follows_embedded_instructions

    @classmethod
    def fallback(cls, reason: str) -> "AnswerVerification":
        return cls(verdict="UNVERIFIED", follows_embedded_instructions=False, unsupported_claims=[], reason=reason)