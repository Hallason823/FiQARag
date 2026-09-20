from typing import Dict, Any
from datasets import load_dataset
from src.processors.logger_mix_in import LoggerMixIn
from src.models.application_settings import ApplicationSettings

"""Manages infrastructure operations to download and index the raw FiQA dataset from Hugging Face."""
class SourceDatasetRepository(LoggerMixIn):
    def __init__(self) -> None:
        self._settings = ApplicationSettings()

    #Centralizes the Hugging Face API call and progress logging for any dataset partition.
    def _load_dataset_split(self, path: str, split: str, config: str = None) -> Any:
        self._logger.info(f"Fetching source partition '{split}' from registry path: '{path}'")
        if config:
            return load_dataset(path, config, split=split)
        return load_dataset(path, split)[split]

    #Downloads the complete financial document corpus and maps the IDs to their corresponding text data.
    def get_raw_documents(self) -> Dict[str, Dict[str, Any]]:
        dataset = self._load_dataset_split(self._settings.CORPUS_DATASET_REGISTRY, self._settings.CORPUS_SPLIT_KEY)
        return {str(document["_id"]): {"title": document.get("title", ""), "text": document.get("text", "")} for document in dataset}
    
    #Downloads the financial test questions/queries and indexes them by their string ID.
    def get_queries(self) -> Dict[str, Dict[str, Any]]:
        dataset = self._load_dataset_split(self._settings.CORPUS_DATASET_REGISTRY, self._settings.QUERIES_SPLIT_KEY)
        return {str(query["_id"]): {"text": query.get("text", "")} for query in dataset}

    #Retrieves the official ground-truth test mappings (QRELS) used to evaluate the RAG pipeline.
    def get_test_mapping(self) -> Any:
        return self._load_dataset_split(self._settings.MAPPING_DATASET_REGISTRY, self._settings.TEST_PARTITION_KEY, self._settings.DEFAULT_CONFIG_KEY)