import json
from typing import Any, Dict, List
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
        self._groq_client = Groq(api_key=self._settings.groq_api_key)
        self._prompt_catalog: Dict[str, Any] = {}
        self._load_external_prompt_configurations()

    def _load_external_prompt_configurations(self) -> None:
        prompt_file_path = self._settings.prompt_config_file_path
        self._logger.info(f"Loading prompt version '{self._settings.prompt_version}' from path: '{prompt_file_path}'")
        with open(prompt_file_path, "r", encoding="utf-8") as file:
            self._prompt_catalog = json.load(file)

    def has_prompt(self, prompt_name: str) -> bool:
        return prompt_name in self._prompt_catalog

    def get_prompt(self, prompt_name: str) -> Dict[str, str]:
        if not self.has_prompt(prompt_name):
            raise KeyError(f"Prompt '{prompt_name}' not found in version '{self._settings.prompt_version}'.")
        return self._prompt_catalog[prompt_name]

    def _build_generation_messages(self, user_query: str, retrieved_context: str, conversation_history: str) -> List[Dict[str, str]]:
        generation_prompt = self.get_prompt(self.GENERATION_PROMPT_KEY)
        user_template = generation_prompt[self.USER_TEMPLATE_KEY]
        if self.HISTORY_PLACEHOLDER in user_template:
            history_text = conversation_history or generation_prompt.get(self.EMPTY_HISTORY_TEXT_KEY, "")
            formatted_user_prompt = user_template.format(history=history_text, context=retrieved_context, query=user_query)
        else:
            legacy_context = f"CONVERSATION HISTORY FOR THIS TASK:\n{conversation_history}\n\nRETRIEVED DOCUMENTS FROM THE FIQA DATABASE:\n{retrieved_context}" if conversation_history else retrieved_context
            formatted_user_prompt = user_template.format(context=legacy_context, query=user_query)
        return [{"role": "system", "content": generation_prompt[self.SYSTEM_KEY]}, {"role": "user", "content": formatted_user_prompt}]

    def format_document(self, index: int, chunk: Dict[str, Any]) -> str:
        document_template = self.get_prompt(self.GENERATION_PROMPT_KEY).get(self.DOCUMENT_TEMPLATE_KEY, self.DEFAULT_DOCUMENT_TEMPLATE)
        return document_template.format(index=index, document_id=chunk.get("document_id", "N/A"), text=chunk.get("text", ""))

    def _execute_chat_completion(self, messages: List[Dict[str, str]], max_tokens: int, stage_name: str) -> str:
        model_name = self._settings.generation_model_name
        self._logger.info(f"Dispatching '{stage_name}' request to Groq API using model '{model_name}' and prompt version '{self._settings.prompt_version}'")
        api_response = self._groq_client.chat.completions.create(model=model_name, messages=messages,
                                                                 temperature=self._settings.model_temperature, max_completion_tokens=max_tokens, reasoning_effort=self._settings.reasoning_effort_level)
        return api_response.choices[0].message.content or ""

    def execute_text_generation(self, user_query: str, retrieved_context: str, conversation_history: str = "") -> str:
        messages = self._build_generation_messages(user_query=user_query, retrieved_context=retrieved_context, conversation_history=conversation_history)
        return self._execute_chat_completion(messages=messages, max_tokens=self._settings.max_completion_tokens, stage_name="generation")

    def execute_question_classification(self, user_query: str, conversation_history: str = "") -> str:
        classification_prompt = self.get_prompt(self.CLASSIFICATION_PROMPT_KEY)
        history_text = conversation_history or classification_prompt.get(self.EMPTY_HISTORY_TEXT_KEY, "")
        formatted_user_prompt = classification_prompt[self.USER_TEMPLATE_KEY].format(history=history_text, query=user_query)
        messages = [{"role": "system", "content": classification_prompt[self.SYSTEM_KEY]}, {"role": "user", "content": formatted_user_prompt}]
        return self._execute_chat_completion(messages=messages, max_tokens=self._settings.classification_max_tokens, stage_name="classification")

    def execute_answer_verification(self, user_query: str, retrieved_context: str, generated_answer: str) -> str:
        verification_prompt = self.get_prompt(self.VERIFICATION_PROMPT_KEY)
        formatted_user_prompt = verification_prompt[self.USER_TEMPLATE_KEY].format(context=retrieved_context, query=user_query, answer=generated_answer)
        messages = [{"role": "system", "content": verification_prompt[self.SYSTEM_KEY]}, {"role": "user", "content": formatted_user_prompt}]
        return self._execute_chat_completion(messages=messages, max_tokens=self._settings.verification_max_tokens, stage_name="verification")