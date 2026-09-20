import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.repositories.source_dataset_repository import SourceDatasetRepository

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    repository = SourceDatasetRepository()
    try:
        raw_documents = repository.get_raw_documents()
        print(f"Documents: {len(raw_documents)}")
        first_doc_id = list(raw_documents.keys())[0]
        print(f"Sample Doc [{first_doc_id}]: {raw_documents[first_doc_id]}\n")
        queries = repository.get_queries()
        print(f"Queries: {len(queries)}")
        first_query_id = list(queries.keys())[0]
        print(f"Sample Query [{first_query_id}]: {queries[first_query_id]}\n")
        test_mapping = repository.get_test_mapping()
        print(f"Mappings: {len(test_mapping)}")
        print(f"Sample Mapping: {test_mapping[0]}\n")
        
    except Exception as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    main()