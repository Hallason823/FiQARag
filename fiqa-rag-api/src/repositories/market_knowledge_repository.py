from typing import List, Dict, Any
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from src.processors.logger_mix_in import LoggerMixIn
from src.models.application_settings import ApplicationSettings

class MarketKnowledgeRepository(LoggerMixIn):
    def __init__(self) -> None:
        self._settings = ApplicationSettings()
        self._embedding_model = SentenceTransformer(self._settings.EMBEDDING_MODEL_REGISTRY)
        self._vector_index = None
        self._indexed_chunks_metadata = []

    def save_document_chunks(self, structured_chunks: List[Dict[str, Any]]) -> None:
        if not structured_chunks:
            return
        self._logger.info(f"Generating semantic embeddings for {len(structured_chunks)} chunks.")
        chunk_texts_list = [chunk["texto"] for chunk in structured_chunks]
        computed_embeddings = self._embedding_model.encode(chunk_texts_list, normalize_embeddings=True).astype("float32")
        vector_dimension = computed_embeddings.shape[1]
        self._vector_index = faiss.IndexFlatIP(vector_dimension)
        self._vector_index.add(computed_embeddings)
        self._indexed_chunks_metadata = structured_chunks
        self._logger.info("FAISS vector index successfully populated.")

    def find_similar_chunks(self, user_query: str, top_k: int = None) -> List[Dict[str, Any]]:
        search_limit = top_k if top_k is not None else self._settings.default_top_k
        self._logger.info(f"Searching FAISS index for query similarity: '{user_query}' with limit: {search_limit}")
        query_embedding = self._embedding_model.encode([user_query], normalize_embeddings=True).astype("float32")
        similarity_scores, matrix_indices = self._vector_index.search(query_embedding, search_limit)
        formatted_search_results = []
        for score, index in zip(similarity_scores[0], matrix_indices[0]):
            if index == -1:
                continue
            matched_chunk = self._indexed_chunks_metadata[index].copy()
            matched_chunk["score"] = float(score)
            formatted_search_results.append(matched_chunk)
        return formatted_search_results