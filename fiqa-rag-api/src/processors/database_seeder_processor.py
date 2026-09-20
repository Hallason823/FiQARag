from src.repositories.source_dataset_repository import SourceDatasetRepository
from src.processors.text_splitter_processor import TextSplitterProcessor
from src.repositories.market_knowledge_repository import MarketKnowledgeRepository
from src.processors.logger_mix_in import LoggerMixIn

class DatabaseSeederProcessor(LoggerMixIn):
    def __init__(self, dataset_repository: SourceDatasetRepository, splitter_processor: TextSplitterProcessor, knowledge_repository: MarketKnowledgeRepository) -> None:
        self._dataset_repository = dataset_repository
        self._splitter_processor = splitter_processor
        self._knowledge_repository = knowledge_repository

    def execute_initial_load(self) -> None:
        self._logger.info("Starting complete database seeding task manager pipeline.")
        raw_documents_dict = self._dataset_repository.get_raw_documents()
        total_documents = len(raw_documents_dict)
        self._logger.info(f"Successfully downloaded {total_documents} raw documents from Hugging Face.")
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