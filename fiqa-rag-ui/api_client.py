import requests
from typing import Dict, Any, Optional, Tuple
from config import API_BASE_URL

class FinancialApiClient:
    @staticmethod
    def check_health() -> bool:
        try:
            response = requests.get(f"{API_BASE_URL}/api/docs", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    @staticmethod
    def get_prompt_versions() -> Tuple[bool, Dict[str, Any]]:
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/financial/prompt-versions",
                timeout=5
            )
            if response.status_code == 200:
                return True, response.json()
            return False, {"error": f"Erro na API ({response.status_code}): {response.text}"}
        except requests.exceptions.RequestException as exc:
            return False, {"error": f"Falha ao carregar versoes de prompt: {str(exc)}"}

    @staticmethod
    def ask_analyst(query: str, task_id: str, limit: int = 5, prompt_version: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        payload = {
            "query": query,
            "task_id": task_id,
            "search_limit": limit
        }
        if prompt_version is not None:
            payload["prompt_version"] = prompt_version

        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/financial/ask",
                json=payload,
                timeout=60
            )
            if response.status_code == 200:
                return True, response.json()
            return False, {"error": f"Erro na API ({response.status_code}): {response.text}"}
        except requests.exceptions.RequestException as exc:
            return False, {"error": f"Falha de comunicacao com o servidor: {str(exc)}"}