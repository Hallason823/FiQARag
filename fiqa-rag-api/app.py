import streamlit as st
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.repositories.source_dataset_repository import SourceDatasetRepository
from src.processors.text_splitter_processor import TextSplitterProcessor
from src.repositories.market_knowledge_repository import MarketKnowledgeRepository
from src.repositories.language_model_repository import LanguageModelRepository
from src.services.rag_service import RAGService

st.set_page_config(page_title="FiQA Financial Assistant", page_icon="📈", layout="centered")
st.title("FiQA Financial Assistant (RAG + LangGraph)")

@st.cache_resource(show_spinner="Carregando e indexando base FiQA...")
def init_rag_system():
    data_repository = SourceDatasetRepository()
    text_splitter = TextSplitterProcessor()
    vector_repository = MarketKnowledgeRepository()
    llm_repository = LanguageModelRepository()

    raw_documents = data_repository.get_raw_documents()
    sample_limit = 1000
    sample_doc_ids = list(raw_documents.keys())[:sample_limit]
    
    all_chunks = []
    for doc_id in sample_doc_ids:
        target_doc = raw_documents[doc_id]
        chunks = text_splitter.split_text(
            document_id=doc_id,
            title=target_doc.get("title", ""),
            text=target_doc.get("text", "")
        )
        all_chunks.extend(chunks)

    vector_repository.save_document_chunks(all_chunks)
    return RAGService(vector_repository, llm_repository)

rag_service = init_rag_system()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Faça uma pergunta sobre o mercado financeiro..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando grafo e gerando resposta..."):
            result = rag_service.answer_query(prompt)
            st.markdown(result["answer"])

            with st.expander("🔍 Fontes Recuperadas da Base FiQA"):
                for idx, src in enumerate(result["search_results"], start=1):
                    doc_id = src.get("documento_id", "N/A")
                    st.markdown(f"**Fonte {idx}** (ID: `{doc_id}`):")
                    st.caption(src["texto"])

    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})