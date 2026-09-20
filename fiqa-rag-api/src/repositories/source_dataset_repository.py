from typing import Dict, Any
from datasets import load_dataset
from src.processors.logger_mix_in import LoggerMixIn

"""Manages infrastructure operations to download and index the raw FiQA dataset from Hugging Face."""
class SourceDatasetRepository(LoggerMixIn):

    CORPUS_DATASET_REGISTRY: str = "BeIR/fiqa"
    MAPPING_DATASET_REGISTRY: str = "BeIR/fiqa-qrels"
    CORPUS_SPLIT_KEY: str = "corpus"
    QUERIES_SPLIT_KEY: str = "queries"
    TEST_PARTITION_KEY: str = "test"

    #Centralizes the Hugging Face API call and progress logging for any dataset partition.
    def _load_dataset_split(self, path: str, split: str) -> Any:
        self._logger.info(f"Fetching source partition '{split}' from registry path: '{path}'")
        return load_dataset(path, split)

    #Downloads the complete financial document corpus and maps the IDs to their corresponding text data.
    def get_raw_documents(self) -> Dict[str, Dict[str, Any]]:
        dataset = self._load_dataset_split(self.CORPUS_DATASET_REGISTRY, self.CORPUS_SPLIT_KEY)
        return {str(document["_id"]): document for document in dataset}
    
    #Downloads the financial test questions/queries and indexes them by their string ID.
    def get_queries(self) -> Dict[str, Dict[str, Any]]:
        dataset = self._load_dataset_split(self.CORPUS_DATASET_REGISTRY, self.QUERIES_SPLIT_KEY)
        return {str(query["_id"]): query for query in dataset}

    #Retrieves the official ground-truth test mappings (QRELS) used to evaluate the RAG pipeline.
    def get_test_mapping(self) -> Any:
        return self._load_dataset_split(self.MAPPING_DATASET_REGISTRY, self.TEST_PARTITION_KEY)