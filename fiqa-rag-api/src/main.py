import os
import sys
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.repositories.market_knowledge_repository import MarketKnowledgeRepository
from src.repositories.language_model_repository import LanguageModelRepository
from src.services.market_expert_service import MarketExpertService
from src.controllers.financial_analyst_controller import FinancialAnalystController

def create_application() -> FastAPI:
    load_dotenv()
    app = FastAPI(title="FiQA Agntic RAG API", version="1.0.0", docs_url="/api/docs")
    knowledge_repository = MarketKnowledgeRepository()
    llm_repository = LanguageModelRepository()
    expert_service = MarketExpertService(knowledge_repository=knowledge_repository, llm_repository=llm_repository)
    financial_controller = FinancialAnalystController(expert_service=expert_service)
    app.include_router(financial_controller.router, prefix="/api/v1")
    return app

app = create_application()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)