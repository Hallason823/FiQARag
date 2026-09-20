import os
from datasets import load_dataset
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_PATH = "vectorstore_fiqa"

def build_vectorstore(max_samples: int = 3000):
    """
    Carrega o corpus BeIR/fiqa e gera o índice vetorial persistente com ChromaDB.
    """
    print(f"Carregando {max_samples} documentos do dataset FiQA...")
    corpus = load_dataset("BeIR/fiqa", "corpus")["corpus"]
    
    docs = []
    for item in corpus.select(range(min(len(corpus), max_samples))):
        text = item["text"].strip()
        title = item.get("title", "").strip()
        content = f"{title}\n\n{text}".strip() if title else text
        
        docs.append(
            Document(
                page_content=content,
                metadata={"doc_id": item["_id"], "title": title}
            )
        )

    print("Gerando embeddings e persistindo no ChromaDB local...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=CHROMA_PATH)
    print(f"Sucesso! Vectorstore criado em '{CHROMA_PATH}'.")

if __name__ == "__main__":
    build_vectorstore()