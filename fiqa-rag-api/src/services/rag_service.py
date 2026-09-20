from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START, END

class RAGState(TypedDict):
    question: str
    search_results: List[Dict[str, Any]]
    context_string: str
    answer: str

class RAGService:
    def __init__(self, vector_repository, llm_repository):
        self.vector_repo = vector_repository
        self.llm_repo = llm_repository
        self.graph = self._build_graph()

    def _retrieve(self, state: RAGState) -> Dict[str, Any]:
        results = self.vector_repo.find_similar_chunks(user_query=state["question"])
        context = "\n\n".join([f"[Source {i}] {r['texto']}" for i, r in enumerate(results, start=1)])
        return {"search_results": results, "context_string": context}

    def _generate(self, state: RAGState) -> Dict[str, Any]:
        response = self.llm_repo.execute_text_generation(
            user_query=state["question"],
            retrieved_context=state["context_string"]
        )
        return {"answer": response}

    def _build_graph(self):
        workflow = StateGraph(RAGState)
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("generate", self._generate)
        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        return workflow.compile()

    def answer_query(self, question: str) -> Dict[str, Any]:
        return self.graph.invoke({
            "question": question,
            "search_results": [],
            "context_string": "",
            "answer": ""
        })