from typing import Dict, List
from collections import defaultdict
from src.processors.logger_mix_in import LoggerMixIn
from src.models.application_settings import ApplicationSettings

class TaskMemoryService(LoggerMixIn):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TaskMemoryService, cls).__new__(cls)
            cls._instance._memory = defaultdict(list)
            cls._instance._settings = ApplicationSettings()
        return cls._instance

    def add_exchange(self, task_id: str, query: str, answer: str) -> None:
        self._memory[task_id].append({"query": query, "answer": answer})
        if len(self._memory[task_id]) > self._settings.max_history_exchanges:
            self._memory[task_id] = self._memory[task_id][-self._settings.max_history_exchanges:]
        self._logger.info(f"Task '{task_id}' updated in backend memory. Total exchanges: {len(self._memory[task_id])}")

    def get_formatted_history(self, task_id: str) -> str:
        history = self._memory.get(task_id, [])
        if not history:
            return ""
        exchanges = [f"User: {item['query']}\nAssistant: {item['answer']}" for item in history]
        return "\n\n".join(exchanges)

    def get_task_history(self, task_id: str) -> List[Dict[str, str]]:
        return self._memory.get(task_id, [])

    def clear_task(self, task_id: str) -> None:
        if task_id in self._memory:
            del self._memory[task_id]
            self._logger.info(f"Task '{task_id}' context cleared from backend memory.")