from typing import List, Dict, Any, TypedDict

class FinancialAnalystState(TypedDict, total=False):
    query: str
    top_k: int
    retrieved_chunks: List[Dict[str, Any]]
    score_maximo: float
    formatted_context: str
    generated_answer: str