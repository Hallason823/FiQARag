import textwrap

MAIN_CSS = textwrap.dedent("""
<style>
.stApp {
    background: radial-gradient(circle at 50% 15%, #131722 0%, #080a0f 85%);
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
header[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* Faixa inferior transparente */
div[data-testid="stBottomBlockContainer"],
footer,
div[data-testid="stBottom"] {
    background: transparent !important;
    border: none !important;
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

/* 1. Anular completamente o invólucro exterior para remover a moldura externa dupla */
[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* 2. Pílula única definida diretamente no contentor de escrita interior */
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] form {
    background-color: #151a27 !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 9999px !important;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45) !important;
    padding: 4px 12px 4px 22px !important;
    min-height: 52px !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease !important;
}

[data-testid="stChatInput"] > div:focus-within,
[data-testid="stChatInput"] form:focus-within {
    border-color: #3b82f6 !important;
    background-color: #182032 !important;
    box-shadow: 0 8px 32px rgba(59, 130, 246, 0.25) !important;
}

/* 3. Forçar transparência estrita em todos os nós filhos internos (elimina a caixa cinzenta) */
[data-testid="stChatInput"] [data-baseweb="base-input"],
[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] div[class*="stChatInput"] div {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* 4. Tipografia da área de escrita */
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    background-color: transparent !important;
    color: #f8fafc !important;
    font-size: 0.93rem !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    padding: 8px 0 !important;
    line-height: 1.45 !important;
    resize: none !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
}

/* 5. Botão de envio integrado e alinhado ao centro */
[data-testid="stChatInput"] button {
    border-radius: 50% !important;
    background-color: #2563eb !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    color: #ffffff !important;
    width: 36px !important;
    height: 36px !important;
    min-width: 36px !important;
    min-height: 36px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
    box-shadow: 0 2px 10px rgba(37, 99, 235, 0.4) !important;
    transition: all 0.2s ease !important;
}

[data-testid="stChatInput"] button:hover {
    background-color: #1d4ed8 !important;
    border-color: #3b82f6 !important;
    transform: scale(1.06) !important;
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
""")

ROBOT_SVG = """
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
"""