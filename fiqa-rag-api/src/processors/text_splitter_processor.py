from typing import List, Dict, Any, Generator, Tuple
from src.processors.logger_mix_in import LoggerMixIn
from src.models.application_settings import ApplicationSettings

class TextSplitterProcessor(LoggerMixIn):
    def __init__(self) -> None:
        self._settings = ApplicationSettings()

    def _calculate_window_indices(self, total_words: int) -> Generator[Tuple[int, int], None, None]:
        window_start_index = 0
        while window_start_index < total_words:
            window_end_index = min(window_start_index + self._settings.default_chunk_size, total_words)
            yield window_start_index, window_end_index
            if window_end_index == total_words:
                break
            window_start_index += self._settings.default_chunk_size - self._settings.default_chunk_overlap

    def _build_chunk_payload(self, document_id: str, title: str, text: str, sequence_number: int) -> Dict[str, Any]:
        return {"chunk_id": f"{document_id}_c{sequence_number}", "documento_id": document_id, "titulo": title, "texto": text}

    def split_text(self, document_id: str, title: str, text: str) -> List[Dict[str, Any]]:
        self._logger.info(f"Executing chunking process for document ID: '{document_id}'")
        words_list = text.split()
        structured_chunks = []
        chunk_sequence_number = 1
        for start_index, end_index in self._calculate_window_indices(len(words_list)):
            sliced_words = words_list[start_index:end_index]
            formatted_chunk_text = " ".join(sliced_words)
            chunk_payload = self._build_chunk_payload(document_id=document_id, title=title, text=formatted_chunk_text, sequence_number=chunk_sequence_number)
            structured_chunks.append(chunk_payload)
            chunk_sequence_number += 1
        return structured_chunks