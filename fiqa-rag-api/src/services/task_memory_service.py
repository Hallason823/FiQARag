from typing import Dict, List
from collections import defaultdict
from src.processors.logger_mix_in import LoggerMixIn

class TaskMemoryService(LoggerMixIn):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TaskMemoryService, cls).__new__(cls)
            cls._instance._memory = defaultdict(list)
        return cls._instance

    def add_exchange(self, task_id: str, query: str, answer: str) -> None:
        """Registra uma interação na tarefa especificada."""
        self._memory[task_id].append({
            "query": query,
            "answer": answer
        })
        # Mantém as últimas 4 conversas para evitar estouro de contexto
        if len(self._memory[task_id]) > 4:
            self._memory[task_id] = self._memory[task_id][-4:]
        self._logger.info(f"Task '{task_id}' atualizada no backend. Total de interações: {len(self._memory[task_id])}")

    def get_formatted_history(self, task_id: str) -> str:
        """Formata o histórico para injeção de contexto na LLM."""
        history = self._memory.get(task_id, [])
        if not history:
            return ""
        exchanges = []
        for item in history:
            exchanges.append(f"Usuário: {item['query']}\nAssistente: {item['answer']}")
        return "\n\n".join(exchanges)

    def get_task_history(self, task_id: str) -> List[Dict[str, str]]:
        return self._memory.get(task_id, [])

    def clear_task(self, task_id: str) -> None:
        if task_id in self._memory:
            del self._memory[task_id]
            self._logger.info(f"Contexto da Task '{task_id}' resetado no backend.")