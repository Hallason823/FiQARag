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
    st.session_state.task_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_query" not in st.session_state:
    st.session_state.selected_query = None

api_online = FinancialApiClient.check_health()
versions_success, versions_data = FinancialApiClient.get_prompt_versions() if api_online else (False, {})

if versions_success:
    available_prompt_versions = [
        version
        for version in versions_data.get("versions", [])
        if isinstance(version, str)
    ]
    default_prompt_version = versions_data.get("default")

    if default_prompt_version not in available_prompt_versions:
        default_prompt_version = available_prompt_versions[0] if available_prompt_versions else None

    st.session_state.available_prompt_versions = available_prompt_versions
    st.session_state.default_prompt_version = default_prompt_version
else:
    available_prompt_versions = st.session_state.get("available_prompt_versions", [])
    default_prompt_version = st.session_state.get("default_prompt_version")

if available_prompt_versions:
    selected_prompt_version = st.session_state.get("prompt_version")
    if selected_prompt_version not in available_prompt_versions:
        selected_prompt_version = default_prompt_version or available_prompt_versions[0]
        st.session_state.prompt_version = selected_prompt_version

    if st.session_state.get("prompt_version_selector") not in available_prompt_versions:
        st.session_state.prompt_version_selector = selected_prompt_version

def reset_session():
    st.session_state.task_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.selected_query = None
    st.rerun()

def handle_prompt_version_change():
    selected_prompt_version = st.session_state.get("prompt_version_selector")
    if selected_prompt_version == st.session_state.get("prompt_version"):
        return

    st.session_state.prompt_version = selected_prompt_version
    st.session_state.task_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.selected_query = None

def handle_query_selection(query_text: str):
    st.session_state.selected_query = query_text
    st.rerun()

render_top_bar(
    task_id=st.session_state.task_id,
    is_online=api_online,
    prompt_versions=available_prompt_versions,
    on_prompt_version_change=handle_prompt_version_change,
    on_reset_callback=reset_session
)

if len(st.session_state.messages) == 0:
    render_hero_section()
    render_suggestion_chips(handle_query_selection)

render_chat_history(st.session_state.messages)

user_prompt = st.chat_input("Fa�a uma pergunta sobre financas, tributos ou empresas...")
active_query = user_prompt or st.session_state.selected_query

if active_query:
    st.session_state.selected_query = None
    st.session_state.messages.append({"role": "user", "content": active_query})

    with st.chat_message("user"):
        st.markdown(active_query)

    with st.chat_message("assistant"):
        with st.spinner("Classificando a pergunta, consultando a base e verificando a resposta..."):
            success, response_data = FinancialApiClient.ask_analyst(
                query=active_query,
                task_id=st.session_state.task_id,
                limit=5,
                prompt_version=st.session_state.get("prompt_version")
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
                            st.markdown(f"**Fonte {idx} - Doc ID:** `{doc_id}`")
                            st.info(text)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "prompt_version": response_data.get("prompt_version")
                })
            else:
                error_msg = response_data.get("error", "Erro desconhecido na execucao.")
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})