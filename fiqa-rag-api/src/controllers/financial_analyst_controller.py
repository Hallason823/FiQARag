from fastapi import APIRouter, status
from src.models.analysis_request import AnalysisRequest
from src.services.task_memory_service import TaskMemoryService

class FinancialAnalystController:
    def __init__(self, *args, **kwargs) -> None:
        self._market_expert_service = (
            kwargs.get("market_expert_service")
            or kwargs.get("expert_service")
            or (args[0] if args else None)
        )
        self._memory_service = TaskMemoryService()
        self.router = APIRouter(tags=["Financial Analyst"])
        self._register_routes()

    def _register_routes(self) -> None:
        @self.router.post("/financial/ask", status_code=status.HTTP_200_OK)
        def ask_financial_analyst(payload: AnalysisRequest):
            return self._market_expert_service.execute_financial_analysis(
                query=payload.query,
                search_limit=payload.search_limit or 5,
                task_id=payload.task_id or "default_task"
            )

        @self.router.get("/financial/tasks/{task_id}/history", status_code=status.HTTP_200_OK)
        def get_task_history(task_id: str):
            return {
                "task_id": task_id,
                "history": self._memory_service.get_task_history(task_id)
            }

        @self.router.delete("/financial/tasks/{task_id}", status_code=status.HTTP_200_OK)
        def clear_task_memory(task_id: str):
            self._memory_service.clear_task(task_id)
            return {"message": f"Task {task_id} memory cleared successfully."}
