import uuid
import streamlit as st

from config import PAGE_TITLE, PAGE_ICON
from styles import MAIN_CSS
from api_client import FinancialApiClient
from components import (
    render_top_bar,
    render_hero_section,
    render_suggestion_chips,
    render_chat_history
)

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(MAIN_CSS, unsafe_allow_html=True)

if "task_id" not in st.session_state:
    st.session_state.task_id = str(uuid.uuid4())[:8]

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_query" not in st.session_state:
    st.session_state.selected_query = None

def reset_session():
    st.session_state.task_id = str(uuid.uuid4())[:8]
    st.session_state.messages = []
    st.session_state.selected_query = None
    st.rerun()

def handle_query_selection(query_text: str):
    st.session_state.selected_query = query_text
    st.rerun()

api_online = FinancialApiClient.check_health()
render_top_bar(st.session_state.task_id, api_online, reset_session)

if len(st.session_state.messages) == 0:
    render_hero_section()
    render_suggestion_chips(handle_query_selection)

render_chat_history(st.session_state.messages)

user_prompt = st.chat_input("Faca uma pergunta sobre financas, tributos ou empresas...")
active_query = user_prompt or st.session_state.selected_query

if active_query:
    st.session_state.selected_query = None
    st.session_state.messages.append({"role": "user", "content": active_query})

    with st.chat_message("user"):
        st.markdown(active_query)

    with st.chat_message("assistant"):
        with st.spinner("A consultar base vetorial e a gerar sintese com Llama-3..."):
            success, response_data = FinancialApiClient.ask_analyst(
                query=active_query,
                task_id=st.session_state.task_id,
                limit=5
            )

            if success:
                raw_answer = response_data.get("answer") or response_data.get("response")
                if isinstance(raw_answer, dict):
                    answer = raw_answer.get("answer") or raw_answer.get("content") or str(raw_answer)
                    sources = response_data.get("sources") or raw_answer.get("sources", [])
                else:
                    answer = str(raw_answer) if raw_answer is not None else "Resposta processada."
                    sources = response_data.get("sources", [])

                st.markdown(answer)

                if sources:
                    with st.expander("Fontes Consultadas (FAISS Chunks)"):
                        for idx, src in enumerate(sources, start=1):
                            doc_id = src.get("doc_id", "N/A")
                            text = src.get("content") or src.get("text", "")
                            st.markdown(f"**Fonte {idx} — Doc ID:** `{doc_id}`")
                            st.info(text)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
            else:
                error_msg = response_data.get("error", "Erro desconhecido na execucao.")
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})