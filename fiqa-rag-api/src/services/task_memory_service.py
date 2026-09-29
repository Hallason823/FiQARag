from typing import Dict, List, Optional, Tuple
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

    def _build_memory_key(self, task_id: str, prompt_version: Optional[str] = None) -> Tuple[str, str]:
        effective_version = prompt_version or self._settings.prompt_version
        return task_id, effective_version

    def add_exchange(self, task_id: str, query: str, answer: str, prompt_version: Optional[str] = None) -> None:
        memory_key = self._build_memory_key(task_id, prompt_version)
        self._memory[memory_key].append({"query": query, "answer": answer})
        if len(self._memory[memory_key]) > self._settings.max_history_exchanges:
            self._memory[memory_key] = self._memory[memory_key][-self._settings.max_history_exchanges:]
        self._logger.info(f"Task '{task_id}' updated in backend memory for prompt version '{memory_key[1]}'. Total exchanges: {len(self._memory[memory_key])}")

    def get_formatted_history(self, task_id: str, prompt_version: Optional[str] = None) -> str:
        memory_key = self._build_memory_key(task_id, prompt_version)
        history = self._memory.get(memory_key, [])
        if not history:
            return ""
        exchanges = [f"User: {item['query']}\nAssistant: {item['answer']}" for item in history]
        return "\n\n".join(exchanges)

    def get_task_history(self, task_id: str, prompt_version: Optional[str] = None) -> List[Dict[str, str]]:
        memory_key = self._build_memory_key(task_id, prompt_version)
        return self._memory.get(memory_key, [])

    def clear_task(self, task_id: str, prompt_version: Optional[str] = None) -> None:
        if prompt_version is not None:
            memory_key = self._build_memory_key(task_id, prompt_version)
            if memory_key in self._memory:
                del self._memory[memory_key]
                self._logger.info(f"Task '{task_id}' context cleared for prompt version '{prompt_version}'.")
            return

        task_keys = [memory_key for memory_key in self._memory if memory_key[0] == task_id]
        for memory_key in task_keys:
            del self._memory[memory_key]
        if task_keys:
            self._logger.info(f"Task '{task_id}' context cleared for all prompt versions.")