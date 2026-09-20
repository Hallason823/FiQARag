from typing import Dict, Any
from src.repositories.market_knowledge_repository import MarketKnowledgeRepository
from src.repositories.language_model_repository import LanguageModelRepository
from src.services.agent_workflow_builder import AgentWorkflowBuilder
from src.processors.logger_mix_in import LoggerMixIn
from src.models.application_settings import ApplicationSettings

class MarketExpertService(LoggerMixIn):
    def __init__(self, knowledge_repository: MarketKnowledgeRepository, llm_repository: LanguageModelRepository) -> None:
        self._knowledge_repository = knowledge_repository
        self._llm_repository = llm_repository
        self._settings = ApplicationSettings()
        self._compiled_agent_graph = self._initialize_and_compile_agent_graph()

    def _initialize_and_compile_agent_graph(self) -> Any:
        self._logger.info("Initializing workflow builder and compiling LangGraph state machine.")
        workflow_builder = AgentWorkflowBuilder(knowledge_repository=self._knowledge_repository, llm_repository=self._llm_repository)
        return workflow_builder.compile_agent_graph()

    def execute_financial_analysis(self, user_query: str, search_limit: int = None) -> str:
        self._logger.info(f"Initiating agent graph execution for query: '{user_query}'")
        target_limit = search_limit if search_limit is not None else self._settings.default_search_limit
        initial_state = {"query": user_query, "top_k": target_limit, "retrieved_chunks": [], "score_maximo": self._settings.INITIAL_SCORE_VALUE, "formatted_context": "", "generated_answer": ""}
        final_runtime_state = self._compiled_agent_graph.invoke(initial_state)
        return final_runtime_state.get("generated_answer", "")