import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.repositories.source_dataset_repository import SourceDatasetRepository
from src.processors.text_splitter_processor import TextSplitterProcessor
from src.repositories.market_knowledge_repository import MarketKnowledgeRepository

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    repository = SourceDatasetRepository()
    splitter = TextSplitterProcessor()
    vector_db = MarketKnowledgeRepository()
    
    try:
        raw_documents = repository.get_raw_documents()
        print(f"Total Source Documents Available: {len(raw_documents)}")
        all_chunks = []
        sample_limit = 100
        doc_ids_sample = list(raw_documents.keys())[:sample_limit]
        print(f"Processing chunking for a sample of {sample_limit} documents...")
        for doc_id in doc_ids_sample:
            target_doc = raw_documents[doc_id]
            chunks = splitter.split_text(document_id=doc_id, title=target_doc.get("title", ""), text=target_doc.get("text", ""))
            all_chunks.extend(chunks)  
        print(f"Total Chunks Generated: {len(all_chunks)}")
        vector_db.save_document_chunks(all_chunks)
        print("Successfully saved and indexed all chunks in FAISS database.\n")
        random_financial_query = "What are the rules and risks of short selling stocks?"
        print(f"Executing semantic search for random query: '{random_financial_query}'")
        search_results = vector_db.find_similar_chunks(user_query=random_financial_query)
        print(f"\nTop {len(search_results)} Most Semantic Similar Results Found:")
        print("=======================================================================")
        for index, result in enumerate(search_results, start=1):
            print(f"Rank {index} | Chunk ID: {result['chunk_id']} | Score: {result['score']:.4f}")
            print(f"Text Content: {result['texto']}")
            print("-" * 71)
            
    except Exception as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    main()
