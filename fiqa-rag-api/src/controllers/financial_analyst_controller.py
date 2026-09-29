from typing import Optional
from fastapi import APIRouter, HTTPException, status
from src.models.analysis_request import AnalysisRequest
from src.services.task_memory_service import TaskMemoryService

class FinancialAnalystController:
    def __init__(self, *args, **kwargs) -> None:
        self._market_expert_service = (kwargs.get("market_expert_service") or kwargs.get("expert_service") or (args[0] if args else None))
        self._memory_service = TaskMemoryService()
        self.router = APIRouter(tags=["Financial Analyst"])
        self._register_routes()

    def _resolve_prompt_version(self, prompt_version: Optional[str] = None) -> str:
        try:
            return self._market_expert_service.resolve_prompt_version(prompt_version)
        except ValueError as error:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error

    def _register_routes(self) -> None:
        @self.router.post("/financial/ask", status_code=status.HTTP_200_OK)
        def ask_financial_analyst(payload: AnalysisRequest):
            prompt_version = self._resolve_prompt_version(payload.prompt_version)
            return self._market_expert_service.execute_financial_analysis(query=payload.query, search_limit=payload.search_limit or 5, task_id=payload.task_id or "default_task", prompt_version=prompt_version)

        @self.router.get("/financial/prompt-versions", status_code=status.HTTP_200_OK)
        def get_prompt_versions():
            return {
                "default": self._resolve_prompt_version(),
                "versions": self._market_expert_service.get_available_prompt_versions()
            }

        @self.router.get("/financial/tasks/{task_id}/history", status_code=status.HTTP_200_OK)
        def get_task_history(task_id: str, prompt_version: Optional[str] = None):
            effective_prompt_version = self._resolve_prompt_version(prompt_version)
            return {
                "task_id": task_id,
                "prompt_version": effective_prompt_version,
                "history": self._memory_service.get_task_history(task_id, effective_prompt_version)
            }

        @self.router.delete("/financial/tasks/{task_id}", status_code=status.HTTP_200_OK)
        def clear_task_memory(task_id: str, prompt_version: Optional[str] = None):
            effective_prompt_version = self._resolve_prompt_version(prompt_version) if prompt_version is not None else None
            self._memory_service.clear_task(task_id, effective_prompt_version)
            version_scope = f" for prompt version '{effective_prompt_version}'" if effective_prompt_version else " for all prompt versions"
            return {"message": f"Task {task_id} memory cleared successfully{version_scope}."}