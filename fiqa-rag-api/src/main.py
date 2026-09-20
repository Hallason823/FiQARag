import logging
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.repositories.source_dataset_repository import SourceDatasetRepository
from src.processors.text_splitter_processor import TextSplitterProcessor
from src.repositories.market_knowledge_repository import MarketKnowledgeRepository
from src.repositories.language_model_repository import LanguageModelRepository

def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    data_repository = SourceDatasetRepository()
    text_splitter = TextSplitterProcessor()
    vector_repository = MarketKnowledgeRepository()
    llm_repository = LanguageModelRepository()
    try:
        raw_documents = data_repository.get_raw_documents()
        print(f"Total Source Documents Available: {len(raw_documents)}")
        all_chunks = []
        sample_limit = 1000
        sample_doc_ids = list(raw_documents.keys())[:sample_limit]
        print(f"Processing chunking for a sample of {sample_limit} documents...")
        for doc_id in sample_doc_ids:
            target_doc = raw_documents[doc_id]
            chunks = text_splitter.split_text(document_id=doc_id, title=target_doc.get("title", ""), text=target_doc.get("text", ""))
            all_chunks.extend(chunks)  
        print(f"Total Chunks Generated: {len(all_chunks)}")  
        vector_repository.save_document_chunks(all_chunks)
        print("Successfully saved and indexed all chunks in FAISS database.\n")
        user_query = "Should a company be expected to provide on-the-job training to its workers?"
        print(f"Executing semantic search for query: '{user_query}'")
        search_results = vector_repository.find_similar_chunks(user_query=user_query)        
        context_string = "\n\n".join([f"[Source {index}] {result['texto']}" for index, result in enumerate(search_results, start=1)])
        print("\n=======================================================================")
        print("RETRIVED CONTEXT")
        print("=======================================================================")
        print(context_string)
        print("=======================================================================\n")
        print("Dispatching context and query to the Language Model Repository...")
        ai_response = llm_repository.execute_text_generation(user_query=user_query, retrieved_context=context_string)
        print("\n=======================================================================")
        print("FINAL AI RESPONSE")
        print("=======================================================================")
        print(ai_response)
        print("=======================================================================")
    except Exception as error:
        print(f"Error executing main integration test pipeline: {error}")

if __name__ == "__main__":
    main()