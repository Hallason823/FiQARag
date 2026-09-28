from typing import Literal, Any
from pydantic import ValidationError
from langgraph.graph import StateGraph, START, END
from src.models.financial_analyst_state import FinancialAnalystState
from src.models.question_classification import QuestionClassification
from src.repositories.market_knowledge_repository import MarketKnowledgeRepository
from src.repositories.language_model_repository import LanguageModelRepository
from src.processors.structured_output_parser import StructuredOutputParser
from src.processors.logger_mix_in import LoggerMixIn
from src.models.application_settings import ApplicationSettings

class AgentWorkflowBuilder(LoggerMixIn):

    CLASSIFICATION_STAGE_NODE_KEY: str = "classify_question_node"
    OUT_OF_DOMAIN_STAGE_NODE_KEY: str = "handle_out_of_domain_node"
    RETRIEVAL_STAGE_NODE_KEY: str = "retrieve_knowledge_node"
    CONTEXT_STAGE_NODE_KEY: str = "build_context_node"
    GENERATION_STAGE_NODE_KEY: str = "generate_answer_node"
    ABSTENTION_STAGE_NODE_KEY: str = "handle_abstention_node"

    def __init__(self, knowledge_repository: MarketKnowledgeRepository, llm_repository: LanguageModelRepository) -> None:
        self._knowledge_repository = knowledge_repository
        self._llm_repository = llm_repository
        self._output_parser = StructuredOutputParser()
        self._settings = ApplicationSettings()

    def classify_question_node(self, state: FinancialAnalystState) -> FinancialAnalystState:
        if not self._llm_repository.has_prompt(LanguageModelRepository.CLASSIFICATION_PROMPT_KEY):
            return {}
        try:
            raw_output = self._llm_repository.execute_question_classification(user_query=state["query"], conversation_history=state.get("conversation_history", ""))
            classification = QuestionClassification.model_validate(self._output_parser.parse_json_object(raw_output))
        except (ValueError, ValidationError) as error:
            self._logger.warning(f"Invalid classifier output, continuing with fallback: {error}")
            classification = QuestionClassification.fallback(reason="Classifier output could not be parsed.")
        self._logger.info(f"Question classification: {classification.model_dump()}")
        return {"classification": classification.model_dump()}

    def evaluate_domain_routing(self, state: FinancialAnalystState) -> Literal["in_domain", "out_of_domain"]:
        classification = state.get("classification")
        if not classification:
            return "in_domain"
        if not classification["in_domain"] and classification["confidence"] != "LOW":
            return "out_of_domain"
        return "in_domain"

    def handle_out_of_domain_node(self, state: FinancialAnalystState) -> FinancialAnalystState:
        return {"generated_answer": self._settings.OUT_OF_DOMAIN_MESSAGE, "abstention_reason": "OUT_OF_DOMAIN"}

    def retrieve_knowledge_node(self, state: FinancialAnalystState) -> FinancialAnalystState:
        user_query = state["query"]
        search_limit = state.get("top_k", self._settings.default_top_k)
        matched_chunks = self._knowledge_repository.find_similar_chunks(user_query=user_query, top_k=search_limit)
        highest_score = matched_chunks[0]["score"] if matched_chunks else self._settings.INITIAL_SCORE_VALUE
        return {"retrieved_chunks": matched_chunks, "max_score": highest_score}

    def build_context_node(self, state: FinancialAnalystState) -> FinancialAnalystState:
        chunks_list = state.get("retrieved_chunks", [])
        compiled_context = "\n\n".join([self._llm_repository.format_document(index, chunk) for index, chunk in enumerate(chunks_list, start=1)])
        return {"formatted_context": compiled_context}

    def generate_answer_node(self, state: FinancialAnalystState) -> FinancialAnalystState:
        model_response = self._llm_repository.execute_text_generation(user_query=state["query"], retrieved_context=state.get("formatted_context", ""), conversation_history=state.get("conversation_history", ""))
        return {"generated_answer": model_response}

    def handle_abstention_node(self, state: FinancialAnalystState) -> FinancialAnalystState:
        return {"generated_answer": self._settings.ABSTENTION_MESSAGE, "abstention_reason": "LOW_RETRIEVAL_SCORE"}

    def evaluate_evidence_routing(self, state: FinancialAnalystState) -> Literal["valid_evidence", "invalid_evidence"]:
        max_score = state.get("max_score", self._settings.INITIAL_SCORE_VALUE)
        decision = "valid_evidence" if max_score >= self._settings.evidence_threshold_score else "invalid_evidence"
        self._logger.info(f"Evidence routing: max score {max_score:.3f} (threshold {self._settings.evidence_threshold_score}) -> {decision}")
        return decision

    def compile_agent_graph(self) -> Any:
        workflow_graph = StateGraph(FinancialAnalystState)
        workflow_graph.add_node(self.CLASSIFICATION_STAGE_NODE_KEY, self.classify_question_node)
        workflow_graph.add_node(self.OUT_OF_DOMAIN_STAGE_NODE_KEY, self.handle_out_of_domain_node)
        workflow_graph.add_node(self.RETRIEVAL_STAGE_NODE_KEY, self.retrieve_knowledge_node)
        workflow_graph.add_node(self.CONTEXT_STAGE_NODE_KEY, self.build_context_node)
        workflow_graph.add_node(self.GENERATION_STAGE_NODE_KEY, self.generate_answer_node)
        workflow_graph.add_node(self.ABSTENTION_STAGE_NODE_KEY, self.handle_abstention_node)
        workflow_graph.add_edge(START, self.CLASSIFICATION_STAGE_NODE_KEY)
        workflow_graph.add_conditional_edges(self.CLASSIFICATION_STAGE_NODE_KEY, self.evaluate_domain_routing, {"in_domain": self.RETRIEVAL_STAGE_NODE_KEY, "out_of_domain": self.OUT_OF_DOMAIN_STAGE_NODE_KEY})
        workflow_graph.add_conditional_edges(self.RETRIEVAL_STAGE_NODE_KEY, self.evaluate_evidence_routing, {"valid_evidence": self.CONTEXT_STAGE_NODE_KEY, "invalid_evidence": self.ABSTENTION_STAGE_NODE_KEY})
        workflow_graph.add_edge(self.CONTEXT_STAGE_NODE_KEY, self.GENERATION_STAGE_NODE_KEY)
        workflow_graph.add_edge(self.GENERATION_STAGE_NODE_KEY, END)
        workflow_graph.add_edge(self.ABSTENTION_STAGE_NODE_KEY, END)
        workflow_graph.add_edge(self.OUT_OF_DOMAIN_STAGE_NODE_KEY, END)
        return workflow_graph.compile()