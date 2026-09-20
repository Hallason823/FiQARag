from fastapi import APIRouter, HTTPException, status
from src.services.market_expert_service import MarketExpertService
from src.models.analysis_request import AnalysisRequest

class FinancialAnalystController:
    def __init__(self, expert_service: MarketExpertService) -> None:
        self._expert_service = expert_service
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self) -> None:
        @self.router.post("/financial/ask", status_code=status.HTTP_200_OK)
        def ask_financial_analyst(payload: AnalysisRequest):
            try:
                answer = self._expert_service.execute_financial_analysis(user_query=payload.query, search_limit=payload.search_limit)
                return {"query": payload.query, "answer": answer}
            except Exception as error:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal agent execution failure: {str(error)}")