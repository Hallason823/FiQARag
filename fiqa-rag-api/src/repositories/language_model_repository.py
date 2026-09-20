import json
from typing import Any
from groq import Groq
from src.processors.logger_mix_in import LoggerMixIn
from src.models.application_settings import ApplicationSettings

class LanguageModelRepository(LoggerMixIn):
    def __init__(self) -> None:
        self._settings = ApplicationSettings()
        self._groq_client = Groq(api_key=self._settings.groq_api_key)
        self._system_instruction_prompt = ""
        self._user_context_template_prompt = ""
        self._load_external_prompt_configurations()

    def _load_external_prompt_configurations(self) -> None:
        self._logger.info(f"Loading external prompt templates from path: '{self._settings.PROMPT_CONFIG_FILE_PATH}'")
        with open(self._settings.PROMPT_CONFIG_FILE_PATH, "r", encoding="utf-8") as file:
            prompt_templates = json.load(file)
            self._system_instruction_prompt = prompt_templates["system_instruction"]
            self._user_context_template_prompt = prompt_templates["user_template"]

    def execute_text_generation(self, user_query: str, retrieved_context: str, target_model: str = None) -> str:
        model_name = target_model if target_model is not None else self._settings.generation_model_name
        self._logger.info(f"Dispatching completion request to Groq API using model hierarchy: '{model_name}'")
        formatted_user_prompt = self._user_context_template_prompt.format(context=retrieved_context, query=user_query)
        api_response = self._groq_client.chat.completions.create(model=model_name, messages=[{"role": "system", "content": self._system_instruction_prompt},{"role": "user", "content": formatted_user_prompt}],
                                                                 temperature=self._settings.model_temperature,  max_completion_tokens=self._settings.max_completion_tokens, reasoning_effort=self._settings.reasoning_effort_level)
        return api_response.choices[0].message.content