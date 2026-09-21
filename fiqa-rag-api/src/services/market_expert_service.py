from typing import Dict, Any, Optional
from src.services.agent_workflow_builder import AgentWorkflowBuilder
from src.services.task_memory_service import TaskMemoryService
from src.repositories.market_knowledge_repository import MarketKnowledgeRepository
from src.repositories.language_model_repository import LanguageModelRepository
from src.processors.logger_mix_in import LoggerMixIn

class MarketExpertService(LoggerMixIn):
    def __init__(
        self,
        knowledge_repository: Optional[MarketKnowledgeRepository] = None,
        llm_repository: Optional[LanguageModelRepository] = None,
        workflow_builder: Optional[AgentWorkflowBuilder] = None,
        **kwargs
    ) -> None:
        if workflow_builder is not None:
            self._workflow_builder = workflow_builder
        else:
            self._workflow_builder = AgentWorkflowBuilder(
                knowledge_repository=knowledge_repository,
                llm_repository=llm_repository
            )
        self._workflow = self._workflow_builder.compile_agent_graph()
        self._memory_service = TaskMemoryService()

    def execute_financial_analysis(self, query: str, search_limit: int = 5, task_id: str = "default_task") -> Dict[str, Any]:
        history = self._memory_service.get_formatted_history(task_id)

        initial_state = {
            "query": query,
            "task_id": task_id,
            "top_k": search_limit,
            "conversation_history": history
        }

        final_state = self._workflow.invoke(initial_state)
        answer = final_state.get("generated_answer", "No response generated.")

        if answer != "I could not find this information in the consulted database.":
            self._memory_service.add_exchange(task_id, query, answer)

        sources = []
        for chunk in final_state.get("retrieved_chunks", []):
            sources.append({
                "doc_id": chunk.get("doc_id", "N/A"),
                "content": chunk.get("texto", "")
            })

        return {
            "query": query,
            "task_id": task_id,
            "answer": answer,
            "sources": sources
        }
