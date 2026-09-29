from typing import Dict, Any, List, Optional
from src.services.agent_workflow_builder import AgentWorkflowBuilder
from src.services.task_memory_service import TaskMemoryService
from src.repositories.market_knowledge_repository import MarketKnowledgeRepository
from src.repositories.language_model_repository import LanguageModelRepository
from src.processors.logger_mix_in import LoggerMixIn
from src.models.application_settings import ApplicationSettings

class MarketExpertService(LoggerMixIn):
    def __init__(self, knowledge_repository: Optional[MarketKnowledgeRepository] = None, llm_repository: Optional[LanguageModelRepository] = None, workflow_builder: Optional[AgentWorkflowBuilder] = None, **kwargs) -> None:
        self._settings = ApplicationSettings()
        self._llm_repository = llm_repository or LanguageModelRepository()
        self._workflow_builder = AgentWorkflowBuilder(knowledge_repository=knowledge_repository, llm_repository=self._llm_repository) if workflow_builder is None else workflow_builder
        self._workflow = self._workflow_builder.compile_agent_graph()
        self._memory_service = TaskMemoryService()

    def get_available_prompt_versions(self) -> List[str]:
        return self._llm_repository.get_available_prompt_versions()

    def resolve_prompt_version(self, requested_version: Optional[str] = None) -> str:
        return self._llm_repository.resolve_prompt_version(requested_version)

    def execute_financial_analysis(self, query: str, search_limit: int = 5, task_id: str = "default_task", prompt_version: Optional[str] = None) -> Dict[str, Any]:
        effective_prompt_version = self.resolve_prompt_version(prompt_version)
        history = self._memory_service.get_formatted_history(task_id, effective_prompt_version)
        initial_state = {"query": query, "task_id": task_id, "prompt_version": effective_prompt_version, "top_k": search_limit, "conversation_history": history}
        final_state = self._workflow.invoke(initial_state)
        answer = (final_state.get("generated_answer") or "No response generated.").strip()
        abstention_reason = final_state.get("abstention_reason")
        if abstention_reason is None and answer == ApplicationSettings.ABSTENTION_MESSAGE:
            abstention_reason = "INSUFFICIENT_EVIDENCE"
        if abstention_reason is None:
            self._memory_service.add_exchange(task_id, query, answer, effective_prompt_version)
        sources = [] if abstention_reason else [{"doc_id": chunk.get("document_id", "N/A"), "content": chunk.get("text", "")} for chunk in final_state.get("retrieved_chunks", [])]
        configuration = {
            "prompt_version": effective_prompt_version,
            "fixtures_version": self._settings.fixtures_version,
            "include_fixtures": self._settings.include_fixtures,
            "model_name": self._settings.generation_model_name,
            "temperature": self._settings.model_temperature
        }
        return {
            "query": query,
            "task_id": task_id,
            "prompt_version": effective_prompt_version,
            "answer": answer,
            "sources": sources,
            "classification": final_state.get("classification"),
            "verification": final_state.get("verification"),
            "abstention_reason": abstention_reason,
            "configuration": configuration
        }