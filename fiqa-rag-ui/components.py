import textwrap
import streamlit as st
from styles import ROBOT_SVG

def render_top_bar(task_id: str, is_online: bool, on_reset_callback):
    status_class = "status-ok" if is_online else "status-off"
    status_label = "Online" if is_online else "Offline"

    col1, col2 = st.columns([8, 2])
    with col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; padding: 0.2rem 0;">
            <span class="brand-badge">FiQA Analyst</span>
            <span class="brand-badge" style="font-weight: 400; font-size: 0.8rem;">Task ID: <b>{task_id}</b></span>
            <span class="status-pill {status_class}">[ {status_label} ]</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("Nova Conversa", use_container_width=True):
            on_reset_callback()

    st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.06); margin: 0.3rem 0 1.5rem 0;'>", unsafe_allow_html=True)

def render_hero_section():
    hero_html = f"""
    <div class="hero-box">
        <div class="hero-title">Ready to Analyze Financial Markets?</div>
        <div class="hero-subtitle">Assistente RAG especializado em dados e documentos do FiQA</div>
        <div class="mascot-row">
            <div class="speech-bubble">Consulta de mercado especializada</div>
            <div class="robot-icon">{ROBOT_SVG}</div>
            <div class="speech-bubble">Base vetorial FAISS em tempo real</div>
        </div>
    </div>
    """
    st.markdown(textwrap.dedent(hero_html), unsafe_allow_html=True)

def render_suggestion_chips(on_select_callback):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Should companies provide on-the-job training?", use_container_width=True):
            on_select_callback("Should companies be expected to provide on-the-job training to workers according to the documents?")
        if st.button("What percentage of my company if I only put money?", use_container_width=True):
            on_select_callback("What percentage of my company should I have if I only put money?")

    with col2:
        if st.button("What is considered a business expense on a trip?", use_container_width=True):
            on_select_callback("What is considered a business expense on a business trip?")
        if st.button("How does inflation affect corporate bond yields?", use_container_width=True):
            on_select_callback("How does inflation affect corporate bond yields?")

def render_chat_history(messages):
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("Fontes Consultadas (FAISS Chunks)"):
                    for idx, src in enumerate(msg["sources"], start=1):
                        doc_id = src.get("doc_id", "N/A")
                        text = src.get("content") or src.get("text", "")
                        st.markdown(f"**Fonte {idx} — Doc ID:** `{doc_id}`")
                        st.info(text)