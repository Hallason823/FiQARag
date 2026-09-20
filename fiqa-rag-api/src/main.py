import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.repositories.source_dataset_repository import SourceDatasetRepository
from src.processors.text_splitter_processor import TextSplitterProcessor

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    repository = SourceDatasetRepository()
    splitter = TextSplitterProcessor()
    
    try:
        raw_documents = repository.get_raw_documents()
        print(f"Documents: {len(raw_documents)}")
        doc_id = list(raw_documents.keys())[1]
        target_doc = raw_documents[doc_id]
        print(f"Original Doc [{doc_id}]: {target_doc}\n")
        chunks = splitter.split_text(document_id=doc_id, title=target_doc.get("title", ""), text=target_doc.get("text", ""))
        print(f"Total Chunks Generated: {len(chunks)}")
        for chunk in chunks:
            print(f"--> Chunk ID: {chunk['chunk_id']}")
            print(f"    Text: {chunk['texto']}\n")
        
    except Exception as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    main()
