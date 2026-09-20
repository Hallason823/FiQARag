import os
import json
from typing import Any
from groq import Groq
from src.processors.logger_mix_in import LoggerMixIn

class LanguageModelRepository(LoggerMixIn):

    DEFAULT_GENERATION_MODEL: str = "qwen/qwen3.8-27b"
    PROMPT_CONFIG_FILE_PATH: str = os.path.join("config", "market_analyst_prompts.json")
    MODEL_TEMPERATURE: float = 0.0
    MAX_COMPLETION_TOKENS: int = 300
    REASONING_EFFORT_LEVEL: str = "none"

    def __init__(self) -> None:
        self._groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self._system_instruction_prompt = ""
        self._user_context_template_prompt = ""
        self._load_external_prompt_configurations()

    def _load_external_prompt_configurations(self) -> None:
        self._logger.info(f"Loading external prompt templates from path: '{self.PROMPT_CONFIG_FILE_PATH}'")
        with open(self.PROMPT_CONFIG_FILE_PATH, "r", encoding="utf-8") as file:
            prompt_templates = json.load(file)
            self._system_instruction_prompt = prompt_templates["system_instruction"]
            self._user_context_template_prompt = prompt_templates["user_template"]

    def execute_text_generation(self, user_query: str, retrieved_context: str, target_model: str = None) -> str:
        model_name = target_model if target_model is not None else self.DEFAULT_GENERATION_MODEL
        self._logger.info(f"Dispatching completion request to Groq API using model hierarchy: '{model_name}'")
        formatted_user_prompt = self._user_context_template_prompt.format(context=retrieved_context, query=user_query)
        api_response = self._groq_client.chat.completions.create(model=model_name, messages=[{"role": "system", "content": self._system_instruction_prompt},{"role": "user", "content": formatted_user_prompt}],
                                                                 temperature=self.MODEL_TEMPERATURE, max_completion_tokens=self.MAX_COMPLETION_TOKENS, reasoning_effort=self.REASONING_EFFORT_LEVEL)
        return api_response.choices[0].message.content