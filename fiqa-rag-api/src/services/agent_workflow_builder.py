from typing import Literal
from langgraph.graph import StateGraph, START, END
from src.models.financial_analyst_state import FinancialAnalystState
from src.repositories.market_knowledge_repository import MarketKnowledgeRepository
from src.repositories.language_model_repository import LanguageModelRepository
from src.processors.logger_mix_in import LoggerMixIn

class AgentWorkflowBuilder(LoggerMixIn):

    EVIDENCE_THRESHOLD_SCORE: float = 0.5
    RETRIEVAL_STAGE_NODE_KEY: str = "retrieve_knowledge_node"
    CONTEXT_STAGE_NODE_KEY: str = "build_context_node"
    GENERATION_STAGE_NODE_KEY: str = "generate_answer_node"
    ABSTENTION_STAGE_NODE_KEY: str = "handle_abstention_node"

    def __init__(self, knowledge_repository: MarketKnowledgeRepository, llm_repository: LanguageModelRepository) -> None:
        self._knowledge_repository = knowledge_repository
        self._llm_repository = llm_repository

    def retrieve_knowledge_node(self, state: FinancialAnalystState) -> FinancialAnalystState:
        user_query = state["query"]
        search_limit = state.get("top_k")
        matched_chunks = self._knowledge_repository.find_similar_chunks(user_query=user_query, top_k=search_limit)
        highest_score = matched_chunks[0]["score"] if matched_chunks else 0.0
        return {"retrieved_chunks": matched_chunks, "score_maximo": highest_score}

    def build_context_node(self, state: FinancialAnalystState) -> FinancialAnalystState:
        chunks_list = state["retrieved_chunks"]
        compiled_context = "\n\n".join([f"[Source {index}] {chunk['texto']}" for index, chunk in enumerate(chunks_list, start=1)])
        return {"formatted_context": compiled_context}

    def generate_answer_node(self, state: FinancialAnalystState) -> FinancialAnalystState:
        user_query = state["query"]
        context_data = state["formatted_context"]
        model_response = self._llm_repository.execute_text_generation(user_query=user_query,retrieved_context=context_data)
        return {"generated_answer": model_response}

    def handle_abstention_node(self, state: FinancialAnalystState) -> FinancialAnalystState:
        return {"generated_answer": "I could not find this information in the consulted database."}

    def evaluate_evidence_routing(self, state: FinancialAnalystState) -> Literal["valid_evidence", "invalid_evidence"]:
        if state["score_maximo"] >= self.EVIDENCE_THRESHOLD_SCORE:
            return "valid_evidence"
        return "invalid_evidence"

    def compile_agent_graph(self) -> Any:
        workflow_graph = StateGraph(FinancialAnalystState)
        workflow_graph.add_node(self.RETRIEVAL_STAGE_NODE_KEY, self.retrieve_knowledge_node)
        workflow_graph.add_node(self.CONTEXT_STAGE_NODE_KEY, self.build_context_node)
        workflow_graph.add_node(self.GENERATION_STAGE_NODE_KEY, self.generate_answer_node)
        workflow_graph.add_node(self.ABSTENTION_STAGE_NODE_KEY, self.handle_abstention_node)
        workflow_graph.add_edge(START, self.RETRIEVAL_STAGE_NODE_KEY)
        workflow_graph.add_conditional_edges(self.RETRIEVAL_STAGE_NODE_KEY, self.evaluate_evidence_routing,{"valid_evidence": self.CONTEXT_STAGE_NODE_KEY, "invalid_evidence": self.ABSTENTION_STAGE_NODE_KEY})
        workflow_graph.add_edge(self.CONTEXT_STAGE_NODE_KEY, self.GENERATION_STAGE_NODE_KEY)
        workflow_graph.add_edge(self.GENERATION_STAGE_NODE_KEY, END)
        workflow_graph.add_edge(self.ABSTENTION_STAGE_NODE_KEY, END)
        return workflow_graph.compile()

    def print_workflow_graph(self) -> None:
        compiled_graph = self.compile_agent_graph()
        print("\n" + "=" * 40)
        print("LANGGRAPH WORKFLOW STRUCTURE")
        print("=" * 40)
        print(compiled_graph.get_graph().draw_mermaid())
        print("=" * 40 + "\n")