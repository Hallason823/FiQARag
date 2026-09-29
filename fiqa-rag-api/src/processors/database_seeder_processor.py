from typing import Any, Dict
from src.repositories.source_dataset_repository import SourceDatasetRepository
from src.processors.text_splitter_processor import TextSplitterProcessor
from src.repositories.market_knowledge_repository import MarketKnowledgeRepository
from src.processors.logger_mix_in import LoggerMixIn
from src.models.application_settings import ApplicationSettings

class DatabaseSeederProcessor(LoggerMixIn):
    def __init__(self, dataset_repository: SourceDatasetRepository, splitter_processor: TextSplitterProcessor, knowledge_repository: MarketKnowledgeRepository) -> None:
        self._dataset_repository = dataset_repository
        self._splitter_processor = splitter_processor
        self._knowledge_repository = knowledge_repository
        self._settings = ApplicationSettings()

    def _append_fixture_documents(self, raw_documents_dict: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        if not self._settings.include_fixtures:
            return raw_documents_dict
        fixture_documents = self._dataset_repository.get_fixture_documents()
        self._logger.warning(f"INCLUDE_FIXTURES is enabled: {len(fixture_documents)} documents from '{self._settings.fixtures_version}' were added to the knowledge base ({list(fixture_documents)}).")
        return {**raw_documents_dict, **fixture_documents}

    def execute_initial_load(self) -> None:
        self._logger.info("Starting complete database seeding task manager pipeline.")
        raw_documents_dict = self._dataset_repository.get_raw_documents()
        self._logger.info(f"Successfully downloaded {len(raw_documents_dict)} raw documents from Hugging Face.")
        raw_documents_dict = self._append_fixture_documents(raw_documents_dict)
        total_documents = len(raw_documents_dict)
        all_processed_chunks = []
        document_counter = 1
        for doc_id, doc_data in raw_documents_dict.items():
            chunks = self._splitter_processor.split_text(document_id=doc_id, title=doc_data.get("title", ""), text=doc_data.get("text", ""))
            all_processed_chunks.extend(chunks)
            if document_counter % 10000 == 0 or document_counter == total_documents:
                self._logger.info(f"Chunking progress: {document_counter}/{total_documents} documents processed.")
            document_counter += 1
        self._logger.info(f"Text processing finished. Total of {len(all_processed_chunks)} chunks generated.")
        self._logger.info("Persisting computed data matrix into the FAISS vector repository.")
        self._knowledge_repository.save_document_chunks(all_processed_chunks)
        self._logger.info("Database seeding execution completed successfully. System is ready for RAG operations.")