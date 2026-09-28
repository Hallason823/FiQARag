import json
from typing import Any, Dict
from groq import Groq
from src.processors.logger_mix_in import LoggerMixIn
from src.models.application_settings import ApplicationSettings

class LanguageModelRepository(LoggerMixIn):
    def __init__(self) -> None:
        self._settings = ApplicationSettings()
        self._groq_client = Groq(api_key=self._settings.groq_api_key)
        self._prompt_catalog: Dict[str, Any] = {}
        self._load_external_prompt_configurations()

    def _load_external_prompt_configurations(self) -> None:
        prompt_file_path = self._settings.prompt_config_file_path
        self._logger.info(f"Loading prompt version '{self._settings.prompt_version}' from path: '{prompt_file_path}'")
        with open(prompt_file_path, "r", encoding="utf-8") as file:
            self._prompt_catalog = json.load(file)

    def get_prompt(self, prompt_name: str) -> Dict[str, str]:
        if prompt_name not in self._prompt_catalog:
            raise KeyError(f"Prompt '{prompt_name}' not found in version '{self._settings.prompt_version}'.")
        return self._prompt_catalog[prompt_name]

    def execute_text_generation(self, user_query: str, retrieved_context: str, target_model: str = None) -> str:
        model_name = target_model if target_model is not None else self._settings.generation_model_name
        generation_prompt = self.get_prompt("generation")
        self._logger.info(f"Dispatching completion request to Groq API using model '{model_name}' and prompt version '{self._settings.prompt_version}'")
        formatted_user_prompt = generation_prompt["user_template"].format(context=retrieved_context, query=user_query)
        api_response = self._groq_client.chat.completions.create(model=model_name, messages=[{"role": "system", "content": generation_prompt["system"]}, {"role": "user", "content": formatted_user_prompt}],
                                                                 temperature=self._settings.model_temperature, max_completion_tokens=self._settings.max_completion_tokens, reasoning_effort=self._settings.reasoning_effort_level)
        return api_response.choices[0].message.content