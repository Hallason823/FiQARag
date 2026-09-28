import json
import re
from typing import Any, Dict
from src.processors.logger_mix_in import LoggerMixIn

class StructuredOutputParser(LoggerMixIn):
    _CODE_FENCE_PATTERN = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)

    def parse_json_object(self, raw_text: str) -> Dict[str, Any]:
        if not raw_text:
            raise ValueError("Empty model output.")
        cleaned_text = self._CODE_FENCE_PATTERN.sub("", raw_text.strip())
        start_index = cleaned_text.find("{")
        end_index = cleaned_text.rfind("}")
        if start_index == -1 or end_index <= start_index:
            raise ValueError(f"No JSON object found in model output: {raw_text[:200]!r}")
        parsed_value = json.loads(cleaned_text[start_index:end_index + 1])
        if not isinstance(parsed_value, dict):
            raise ValueError("Model output is not a JSON object.")
        return parsed_value