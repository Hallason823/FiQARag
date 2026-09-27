from typing import List, Dict, Any, TypedDict

class FinancialAnalystState(TypedDict, total=False):
    query: str
    task_id: str
    top_k: int
    conversation_history: str
    retrieved_chunks: List[Dict[str, Any]]
    max_score: float
    formatted_context: str
    generated_answer: str