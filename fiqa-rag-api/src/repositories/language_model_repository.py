import json
import os
from typing import Any, Dict, List, Optional
from groq import Groq
from src.processors.logger_mix_in import LoggerMixIn
from src.models.application_settings import ApplicationSettings

class LanguageModelRepository(LoggerMixIn):

    GENERATION_PROMPT_KEY: str = "generation"
    CLASSIFICATION_PROMPT_KEY: str = "classification"
    VERIFICATION_PROMPT_KEY: str = "verification"
    SYSTEM_KEY: str = "system"
    USER_TEMPLATE_KEY: str = "user_template"
    DOCUMENT_TEMPLATE_KEY: str = "document_template"
    EMPTY_HISTORY_TEXT_KEY: str = "empty_history_text"
    HISTORY_PLACEHOLDER: str = "{history}"
    DEFAULT_DOCUMENT_TEMPLATE: str = "[Source {index}] {text}"

    def __init__(self) -> None:
        self._settings = ApplicationSettings()
        self._prompt_catalogs: Dict[str, Dict[str, Any]] = {}
        self._load_external_prompt_configurations()
        self.resolve_prompt_version()
        self._groq_client = Groq(api_key=self._settings.groq_api_key)

    def _load_external_prompt_configurations(self) -> None:
        prompts_directory = self._settings.PROMPTS_DIRECTORY
        if not os.path.isdir(prompts_directory):
            raise FileNotFoundError(f"Prompt configuration directory not found: '{prompts_directory}'.")

        prompt_file_names = sorted(
            file_name
            for file_name in os.listdir(prompts_directory)
            if file_name.endswith(".json")
        )
        if not prompt_file_names:
            raise FileNotFoundError(f"No prompt configuration files found in: '{prompts_directory}'.")

        for file_name in prompt_file_names:
            prompt_version = os.path.splitext(file_name)[0]
            prompt_file_path = os.path.join(prompts_directory, file_name)
            with open(prompt_file_path, "r", encoding="utf-8") as file:
                prompt_catalog = json.load(file)

            if not isinstance(prompt_catalog, dict):
                raise ValueError(f"Prompt catalog '{prompt_version}' must contain a JSON object.")
            if self.GENERATION_PROMPT_KEY not in prompt_catalog:
                raise ValueError(f"Prompt catalog '{prompt_version}' does not contain a generation prompt.")

            self._prompt_catalogs[prompt_version] = prompt_catalog
            self._logger.info(f"Loaded prompt version '{prompt_version}' from path: '{prompt_file_path}'")

    def get_available_prompt_versions(self) -> List[str]:
        return sorted(self._prompt_catalogs.keys())

    def resolve_prompt_version(self, requested_version: Optional[str] = None) -> str:
        prompt_version = requested_version if requested_version is not None else self._settings.prompt_version
        if prompt_version not in self._prompt_catalogs:
            available_versions = ", ".join(self.get_available_prompt_versions())
            raise ValueError(f"Unknown prompt version '{prompt_version}'. Available versions: {available_versions}.")
        return prompt_version

    def has_prompt(self, prompt_name: str, prompt_version: Optional[str] = None) -> bool:
        effective_version = self.resolve_prompt_version(prompt_version)
        return prompt_name in self._prompt_catalogs[effective_version]

    def get_prompt(self, prompt_name: str, prompt_version: Optional[str] = None) -> Dict[str, str]:
        effective_version = self.resolve_prompt_version(prompt_version)
        prompt_catalog = self._prompt_catalogs[effective_version]
        if prompt_name not in prompt_catalog:
            raise KeyError(f"Prompt '{prompt_name}' not found in version '{effective_version}'.")
        return prompt_catalog[prompt_name]

    def _build_generation_messages(self, user_query: str, retrieved_context: str, conversation_history: str, prompt_version: Optional[str] = None) -> List[Dict[str, str]]:
        generation_prompt = self.get_prompt(self.GENERATION_PROMPT_KEY, prompt_version)
        user_template = generation_prompt[self.USER_TEMPLATE_KEY]
        if self.HISTORY_PLACEHOLDER in user_template:
            history_text = conversation_history or generation_prompt.get(self.EMPTY_HISTORY_TEXT_KEY, "")
            formatted_user_prompt = user_template.format(history=history_text, context=retrieved_context, query=user_query)
        else:
            legacy_context = f"CONVERSATION HISTORY FOR THIS TASK:\n{conversation_history}\n\nRETRIEVED DOCUMENTS FROM THE FIQA DATABASE:\n{retrieved_context}" if conversation_history else retrieved_context
            formatted_user_prompt = user_template.format(context=legacy_context, query=user_query)
        return [{"role": "system", "content": generation_prompt[self.SYSTEM_KEY]}, {"role": "user", "content": formatted_user_prompt}]

    def format_document(self, index: int, chunk: Dict[str, Any], prompt_version: Optional[str] = None) -> str:
        document_template = self.get_prompt(self.GENERATION_PROMPT_KEY, prompt_version).get(self.DOCUMENT_TEMPLATE_KEY, self.DEFAULT_DOCUMENT_TEMPLATE)
        return document_template.format(index=index, document_id=chunk.get("document_id", "N/A"), text=chunk.get("text", ""))

    def _execute_chat_completion(self, messages: List[Dict[str, str]], max_tokens: int, stage_name: str, prompt_version: str) -> str:
        model_name = self._settings.generation_model_name
        self._logger.info(f"Dispatching '{stage_name}' request to Groq API using model '{model_name}' and prompt version '{prompt_version}'")
        api_response = self._groq_client.chat.completions.create(model=model_name, messages=messages,
                                                                 temperature=self._settings.model_temperature, max_completion_tokens=max_tokens, reasoning_effort=self._settings.reasoning_effort_level)
        return api_response.choices[0].message.content or ""

    def execute_text_generation(self, user_query: str, retrieved_context: str, conversation_history: str = "", prompt_version: Optional[str] = None) -> str:
        effective_version = self.resolve_prompt_version(prompt_version)
        messages = self._build_generation_messages(user_query=user_query, retrieved_context=retrieved_context, conversation_history=conversation_history, prompt_version=effective_version)
        return self._execute_chat_completion(messages=messages, max_tokens=self._settings.max_completion_tokens, stage_name="generation", prompt_version=effective_version)

    def execute_question_classification(self, user_query: str, conversation_history: str = "", prompt_version: Optional[str] = None) -> str:
        effective_version = self.resolve_prompt_version(prompt_version)
        classification_prompt = self.get_prompt(self.CLASSIFICATION_PROMPT_KEY, effective_version)
        history_text = conversation_history or classification_prompt.get(self.EMPTY_HISTORY_TEXT_KEY, "")
        formatted_user_prompt = classification_prompt[self.USER_TEMPLATE_KEY].format(history=history_text, query=user_query)
        messages = [{"role": "system", "content": classification_prompt[self.SYSTEM_KEY]}, {"role": "user", "content": formatted_user_prompt}]
        return self._execute_chat_completion(messages=messages, max_tokens=self._settings.classification_max_tokens, stage_name="classification", prompt_version=effective_version)

    def execute_answer_verification(self, user_query: str, retrieved_context: str, generated_answer: str, prompt_version: Optional[str] = None) -> str:
        effective_version = self.resolve_prompt_version(prompt_version)
        verification_prompt = self.get_prompt(self.VERIFICATION_PROMPT_KEY, effective_version)
        formatted_user_prompt = verification_prompt[self.USER_TEMPLATE_KEY].format(context=retrieved_context, query=user_query, answer=generated_answer)
        messages = [{"role": "system", "content": verification_prompt[self.SYSTEM_KEY]}, {"role": "user", "content": formatted_user_prompt}]
        return self._execute_chat_completion(messages=messages, max_tokens=self._settings.verification_max_tokens, stage_name="verification", prompt_version=effective_version)