import os
import uuid
import textwrap
import requests
import streamlit as st

st.set_page_config(
    page_title="FiQA AI - Financial Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

if "task_id" not in st.session_state:
    st.session_state.task_id = str(uuid.uuid4())[:8]

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_query" not in st.session_state:
    st.session_state.selected_query = None

st.markdown(textwrap.dedent("""
<style>
.stApp {
    background: radial-gradient(circle at 50% 15%, #131722 0%, #080a0f 85%);
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
header[data-testid="stHeader"] {
    background-color: transparent !important;
}
.brand-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #141824;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 9999px;
    padding: 6px 14px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #cbd5e1;
}
.hero-box {
    text-align: center;
    margin: 1rem 0 2rem 0;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #ffffff;
    margin-bottom: 0.3rem;
}
.hero-subtitle {
    font-size: 0.95rem;
    color: #94a3b8;
    margin-bottom: 1.5rem;
}
.mascot-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    margin: 1.2rem 0 2.2rem 0;
}
.speech-bubble {
    background: #151a26;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 9999px;
    padding: 8px 18px;
    font-size: 0.84rem;
    color: #cbd5e1;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
}
.robot-icon {
    width: 85px;
    height: 85px;
    filter: drop-shadow(0 8px 24px rgba(59, 130, 246, 0.35));
    animation: floating 3s ease-in-out infinite;
}
@keyframes floating {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}
.stButton > button {
    border-radius: 9999px !important;
    background: #131722 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #cbd5e1 !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 1.3rem !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    border-color: #3b82f6 !important;
    color: #ffffff !important;
    background: #1a2030 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3) !important;
}
[data-testid="stChatMessage"] {
    background-color: #111522 !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 20px !important;
    padding: 1rem 1.3rem !important;
    margin-bottom: 0.85rem !important;
}
[data-testid="stChatInput"] {
    background-color: #111522 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 30px !important;
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4) !important;
}
div[data-testid="stExpander"] {
    background-color: #0d101b !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 14px !important;
}
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 500;
}
.status-ok {
    background: rgba(34, 197, 94, 0.12);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.25);
}
.status-off {
    background: rgba(239, 68, 68, 0.12);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.25);
}
</style>
"""), unsafe_allow_html=True)

api_online = False
try:
    health_resp = requests.get(f"{API_BASE_URL}/api/docs", timeout=2)
    api_online = (health_resp.status_code == 200)
except Exception:
    api_online = False

status_html = (
    '<span class="status-pill status-ok">● Online</span>'
    if api_online else
    '<span class="status-pill status-off">● Offline</span>'
)

top_col1, top_col2 = st.columns([8, 2])
with top_col1:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; padding: 0.2rem 0;">
        <span class="brand-badge">🤖 FiQA Analyst</span>
        <span class="brand-badge" style="font-weight: 400; font-size: 0.8rem;">Task ID: <b>{st.session_state.task_id}</b></span>
        {status_html}
    </div>
    """, unsafe_allow_html=True)

with top_col2:
    if st.button("➕ Nova Conversa", use_container_width=True):
        st.session_state.task_id = str(uuid.uuid4())[:8]
        st.session_state.messages = []
        st.session_state.selected_query = None
        st.rerun()

st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.06); margin: 0.3rem 0 1.5rem 0;'>", unsafe_allow_html=True)

if len(st.session_state.messages) == 0:
    hero_html = """
    <div class="hero-box">
        <div class="hero-title">Ready to Analyze Financial Markets?</div>
        <div class="hero-subtitle">Assistente RAG inteligente especializado em dados e documentos do FiQA</div>
        <div class="mascot-row">
            <div class="speech-bubble">💬 Precisa de dados de mercado?</div>
            <div class="robot-icon">
                <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="50" cy="50" r="46" fill="#151a26" stroke="#3b82f6" stroke-width="3"/>
                    <rect x="28" y="32" width="44" height="28" rx="8" fill="#090b10"/>
                    <circle cx="40" cy="46" r="4" fill="#60a5fa"/>
                    <circle cx="60" cy="46" r="4" fill="#60a5fa"/>
                    <path d="M44 52Q50 56 56 52" stroke="#60a5fa" stroke-width="2" stroke-linecap="round"/>
                    <rect x="47" y="14" width="6" height="12" rx="3" fill="#3b82f6"/>
                    <circle cx="50" cy="12" r="4" fill="#60a5fa"/>
                    <rect x="20" y="38" width="6" height="16" rx="3" fill="#3b82f6"/>
                    <rect x="74" y="38" width="6" height="16" rx="3" fill="#3b82f6"/>
                </svg>
            </div>
            <div class="speech-bubble">📈 Consultando FAISS em tempo real</div>
        </div>
    </div>
    """
    st.markdown(textwrap.dedent(hero_html), unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏢 Should companies provide on-the-job training?", use_container_width=True):
            st.session_state.selected_query = "Should companies be expected to provide on-the-job training to workers according to the documents?"
            st.rerun()
        if st.button("📊 What percentage of my company if I only put money?", use_container_width=True):
            st.session_state.selected_query = "What percentage of my company should I have if I only put money?"
            st.rerun()

    with col2:
        if st.button("✈️ What is considered a business expense on a trip?", use_container_width=True):
            st.session_state.selected_query = "What is considered a business expense on a business trip?"
            st.rerun()
        if st.button("📈 How does inflation affect corporate bond yields?", use_container_width=True):
            st.session_state.selected_query = "How does inflation affect corporate bond yields?"
            st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 Fontes Consultadas (FAISS Chunks)"):
                for idx, src in enumerate(message["sources"], start=1):
                    doc_id = src.get("doc_id", "N/A")
                    text = src.get("content") or src.get("text", "")
                    st.markdown(f"**Fonte {idx} — Doc ID:** `{doc_id}`")
                    st.info(text)

user_prompt = st.chat_input("Faça uma pergunta sobre finanças, tributos ou empresas...")
active_query = user_prompt or st.session_state.selected_query

if active_query:
    st.session_state.selected_query = None
    st.session_state.messages.append({"role": "user", "content": active_query})
    
    with st.chat_message("user"):
        st.markdown(active_query)

    with st.chat_message("assistant"):
        with st.spinner("Consultando base vetorial e sintetizando com Llama-3..."):
            payload = {
                "query": active_query,
                "task_id": st.session_state.task_id,
                "search_limit": 5
            }

            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/financial/ask",
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()
                    raw_answer = data.get("answer") or data.get("response")
                    
                    if isinstance(raw_answer, dict):
                        answer = raw_answer.get("answer") or raw_answer.get("content") or str(raw_answer)
                        sources = data.get("sources") or raw_answer.get("sources", [])
                    else:
                        answer = str(raw_answer) if raw_answer is not None else "Resposta processada."
                        sources = data.get("sources", [])

                    st.markdown(answer)

                    if sources:
                        with st.expander("📚 Fontes Consultadas (FAISS Chunks)"):
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
                    error_msg = f"Erro na API ({response.status_code}): {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

            except requests.exceptions.RequestException as e:
                err_text = f"Falha na comunicação com a API: {str(e)}"
                st.error(err_text)
                st.session_state.messages.append({"role": "assistant", "content": err_text})