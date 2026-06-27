from dotenv import load_dotenv
load_dotenv()  # must be first — before any other import

import streamlit as st
from datetime import datetime
import time

from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.rag_chain import RAGChain

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "DocuMind AI — Intelligent Document Analysis"},
)

# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap');

/* ─────────────────────────────────────────────────────
   HIDE STREAMLIT CHROME
───────────────────────────────────────────────────── */
#MainMenu                               { visibility: hidden !important; }
header[data-testid="stHeader"]          { display: none !important; }
[data-testid="stHeader"]                { display: none !important; }
[data-testid="stDecoration"]            { display: none !important; }
[data-testid="stToolbar"]               { display: none !important; }
[data-testid="stStatusWidget"]          { display: none !important; }
footer                                  { display: none !important; }
.stDeployButton                         { display: none !important; }

/* ─────────────────────────────────────────────────────
   DESIGN TOKENS
───────────────────────────────────────────────────── */
:root {
    --ink:           #0F0F1A;
    --amber:         #E8A030;
    --amber-soft:    rgba(232,160,48,0.10);
    --amber-border:  rgba(232,160,48,0.22);
    --amber-ring:    rgba(232,160,48,0.20);
    --paper:         #F9F8F6;
    --white:         #FFFFFF;
    --muted:         #6B7280;
    --border:        rgba(0,0,0,0.07);
    --border-med:    rgba(0,0,0,0.11);
    --sb-bg:         #0D0D1A;
    --sb-border:     rgba(255,255,255,0.07);
    --sb-text:       rgba(255,255,255,0.82);
    --sb-muted:      rgba(255,255,255,0.32);
    --sb-hover:      rgba(232,160,48,0.09);
    --sb-hover-bd:   rgba(232,160,48,0.22);
}

/* ─────────────────────────────────────────────────────
   BASE
───────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}
.main {
    background: var(--paper) !important;
    padding-top: 0 !important;
}
.block-container {
    padding: 1.6rem 2rem 2rem !important;
    max-width: 100% !important;
}

/* ─────────────────────────────────────────────────────
   SIDEBAR SHELL
───────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--sb-bg) !important;
    border-right: 1px solid var(--sb-border) !important;
    min-width: 240px !important;
    max-width: 280px !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 1.2rem 1rem 1rem !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
}

/* ─────────────────────────────────────────────────────
   SCROLLBAR
───────────────────────────────────────────────────── */
::-webkit-scrollbar              { width: 3px; }
::-webkit-scrollbar-track        { background: transparent; }
::-webkit-scrollbar-thumb        { background: rgba(232,160,48,0.22); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover  { background: rgba(232,160,48,0.40); }

/* ─────────────────────────────────────────────────────
   SIDEBAR: BRAND
───────────────────────────────────────────────────── */
.sb-brand {
    display: flex;
    align-items: center;
    gap: 9px;
    padding-bottom: 0.95rem;
    border-bottom: 1px solid var(--sb-border);
    margin-bottom: 0.2rem;
}
.sb-brand .mark {
    width: 34px; height: 34px;
    border-radius: 8px;
    background: var(--amber);
    display: flex; align-items: center; justify-content: center;
    font-family: 'DM Serif Display', serif;
    font-size: 0.78rem;
    font-weight: 400;
    color: var(--ink);
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(232,160,48,0.30);
    letter-spacing: -0.5px;
}
.sb-brand .nm {
    font-family: 'DM Serif Display', serif;
    font-size: 1rem;
    color: #F5F0E8;
    margin: 0; line-height: 1.15;
}
.sb-brand .tg {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: var(--sb-muted);
    letter-spacing: 0.05em;
    margin: 0;
}

/* ─────────────────────────────────────────────────────
   SIDEBAR: SECTION LABEL
───────────────────────────────────────────────────── */
.sb-lbl {
    display: block;
    font-size: 0.6rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--sb-muted);
    margin: 0.85rem 0 0.4rem;
}
section[data-testid="stSidebar"] {
    transform: translateX(0) !important;
    visibility: visible !important;
    display: block !important;
    min-width: 240px !important;
}

[data-testid="collapsedControl"] {
    display: none !important;
}
/* ─────────────────────────────────────────────────────
   SIDEBAR: FILE UPLOADER — complete dark theme
───────────────────────────────────────────────────── */

/* nuke white background at every nesting level */
section[data-testid="stSidebar"] [data-testid="stFileUploader"],
section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div > div,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] div,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] section,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] label,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] span {
    background: transparent !important;
    background-color: transparent !important;
}

/* drop zone border */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div:first-child {
    border: 1px dashed rgba(255,255,255,0.14) !important;
    border-radius: 8px !important;
    background: rgba(255,255,255,0.025) !important;
    padding: 0.55rem !important;
}

/* all text inside uploader — muted by default */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] p,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] li {
    color: var(--sb-muted) !important;
    font-size: 0.72rem !important;
}

/* browse / add-more button */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background: rgba(255,255,255,0.06) !important;
    border: 0.5px solid rgba(255,255,255,0.13) !important;
    color: var(--sb-text) !important;
    border-radius: 6px !important;
    font-size: 0.72rem !important;
    box-shadow: none !important;
    padding: 0.28rem 0.6rem !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] button:hover {
    background: rgba(255,255,255,0.10) !important;
    border-color: rgba(255,255,255,0.20) !important;
}

/* uploaded file chip container */
section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] {
    background: rgba(255,255,255,0.04) !important;
    border: 0.5px solid rgba(255,255,255,0.09) !important;
    border-radius: 6px !important;
    max-width: 100% !important;
    width: 100% !important;
    overflow: visible !important;
    padding: 4px 6px !important;
}

/* THE FIX: force ALL text/spans inside chip to be white and full-width */
section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] *,
section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] small,
section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] p {
    color: var(--sb-text) !important;
    opacity: 1 !important;
    white-space: normal !important;
    word-break: break-word !important;
    max-width: 176px !important;
    display: block !important;
    font-size: 0.72rem !important;
    line-height: 1.4 !important;
    background: transparent !important;
}

/* delete (✕) button on chip */
section[data-testid="stSidebar"] [data-testid="stFileUploaderDeleteBtn"] button,
section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] [data-testid="baseButton-secondary"] {
    background: rgba(255,255,255,0.07) !important;
    border: 0.5px solid rgba(255,255,255,0.12) !important;
    border-radius: 50% !important;
    color: var(--sb-muted) !important;
    width: 20px !important; height: 20px !important;
    padding: 0 !important;
    min-width: unset !important;
    font-size: 0.65rem !important;
}

/* ─────────────────────────────────────────────────────
   SIDEBAR: DOCUMENT ITEM
───────────────────────────────────────────────────── */
.doc-item {
    display: flex; align-items: flex-start; gap: 7px;
    padding: 7px 9px; border-radius: 7px;
    border: 0.5px solid var(--sb-border);
    margin-bottom: 4px;
    transition: background 0.15s, border-color 0.15s;
    cursor: default;
}
.doc-item:hover {
    background: var(--sb-hover);
    border-color: var(--sb-hover-bd);
}
.doc-item .di-icon { font-size: 0.85rem; flex-shrink: 0; margin-top: 2px; }
.doc-item .di-name {
    font-size: 0.74rem; font-weight: 500;
    color: var(--sb-text);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    max-width: 130px; display: block;
}
.doc-item .di-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; color: var(--sb-muted); display: block;
}

/* ─────────────────────────────────────────────────────
   SIDEBAR: STATS PILLS
───────────────────────────────────────────────────── */
.sb-stats {
    display: grid; grid-template-columns: 1fr 1fr; gap: 5px;
    margin-top: 0.55rem;
}
.ss {
    background: rgba(255,255,255,0.035);
    border: 0.5px solid var(--sb-border);
    border-radius: 7px; padding: 6px 8px; text-align: center;
}
.ss .sv {
    font-family: 'DM Serif Display', serif;
    font-size: 1.35rem; color: #F5F0E8; line-height: 1;
}
.ss .sl { font-size: 0.61rem; color: var(--sb-muted); margin-top: 2px; }

/* ─────────────────────────────────────────────────────
   SIDEBAR: BUTTONS
───────────────────────────────────────────────────── */
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    color: var(--sb-text) !important;
    border: 0.5px solid var(--sb-border) !important;
    border-radius: 7px !important;
    font-size: 0.74rem !important; font-weight: 500 !important;
    padding: 0.38rem 0.75rem !important;
    box-shadow: none !important;
    width: 100% !important;
    transition: background 0.15s, border-color 0.15s, color 0.15s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--sb-hover) !important;
    border-color: var(--sb-hover-bd) !important;
    color: var(--amber) !important;
}

/* ─────────────────────────────────────────────────────
   SIDEBAR: SELECTBOX
───────────────────────────────────────────────────── */
section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 0.5px solid var(--sb-border) !important;
    border-radius: 7px !important;
    font-size: 0.74rem !important;
    color: var(--sb-text) !important;
}

/* ─────────────────────────────────────────────────────
   SIDEBAR: DIVIDER + TECH BADGE
───────────────────────────────────────────────────── */
.sb-divider {
    border: none;
    border-top: 1px solid var(--sb-border);
    margin: 0.55rem 0;
}
.tech-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem; color: var(--sb-muted);
    text-align: center; letter-spacing: 0.04em;
    padding-top: 0.55rem;
    border-top: 1px solid var(--sb-border);
    margin-top: 0.5rem;
}

/* ─────────────────────────────────────────────────────
   MAIN: PAGE HEADER
───────────────────────────────────────────────────── */
.page-header {
    display: flex; align-items: baseline;
    justify-content: space-between;
    padding-bottom: 0.8rem; margin-bottom: 0.85rem;
    border-bottom: 1px solid var(--border);
}
.page-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.7rem; font-weight: 400;
    color: var(--ink); margin: 0; letter-spacing: -0.3px;
}
.page-header h1 em { color: var(--amber); font-style: normal; }
.ph-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.67rem; color: var(--muted);
}

/* ─────────────────────────────────────────────────────
   MAIN: QUICK ACTION BUTTONS
───────────────────────────────────────────────────── */
.stButton > button {
    background: var(--white) !important;
    color: var(--muted) !important;
    border: 0.5px solid var(--border-med) !important;
    border-radius: 7px !important;
    font-size: 0.75rem !important; font-weight: 400 !important;
    padding: 0.36rem 0.85rem !important;
    box-shadow: none !important;
    letter-spacing: 0.01em !important;
    transition: border-color 0.15s, color 0.15s, background 0.15s !important;
}
.stButton > button:hover {
    border-color: var(--amber-border) !important;
    color: var(--ink) !important;
    background: #FFFCF4 !important;
}

/* ─────────────────────────────────────────────────────
   MAIN: DIVIDER
───────────────────────────────────────────────────── */
.main-divider {
    border: none; border-top: 1px solid var(--border);
    margin: 0.55rem 0 0.8rem;
}

/* ─────────────────────────────────────────────────────
   CHAT: MESSAGE WRAPPER
───────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.08rem 0 !important;
    gap: 9px !important;
}

/* ─────────────────────────────────────────────────────
   CHAT: USER BUBBLE
───────────────────────────────────────────────────── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
    [data-testid="stChatMessageContent"] {
    background: var(--ink) !important;
    border: none !important;
    border-radius: 12px 12px 3px 12px !important;
    padding: 0.58rem 0.9rem !important;
    max-width: 66% !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
    [data-testid="stChatMessageContent"] p {
    color: #F0ECE3 !important;
    font-size: 0.84rem !important;
    line-height: 1.62 !important;
    margin: 0 !important;
}

/* ─────────────────────────────────────────────────────
   CHAT: ASSISTANT BUBBLE
───────────────────────────────────────────────────── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stChatMessageContent"] {
    background: var(--white) !important;
    border: 0.5px solid var(--border-med) !important;
    border-radius: 3px 12px 12px 12px !important;
    padding: 0.65rem 0.95rem !important;
    max-width: 80% !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stChatMessageContent"] p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stChatMessageContent"] li {
    font-size: 0.84rem !important;
    line-height: 1.68 !important;
    color: var(--ink) !important;
    margin-bottom: 0.22rem !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stChatMessageContent"] strong {
    font-weight: 500 !important;
    color: var(--ink) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stChatMessageContent"] ul,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stChatMessageContent"] ol {
    padding-left: 1.1rem !important;
    margin: 0.2rem 0 !important;
}

/* ─────────────────────────────────────────────────────
   CHAT: AVATARS
───────────────────────────────────────────────────── */
[data-testid="chatAvatarIcon-user"] {
    background: rgba(0,0,0,0.05) !important;
    border: 0.5px solid var(--border-med) !important;
    color: var(--muted) !important;
}
[data-testid="chatAvatarIcon-assistant"] {
    background: var(--amber) !important;
    border: none !important;
    box-shadow: 0 2px 6px rgba(232,160,48,0.28) !important;
}
[data-testid="chatAvatarIcon-assistant"] svg,
[data-testid="chatAvatarIcon-assistant"] p {
    color: var(--ink) !important;
    fill: var(--ink) !important;
}

/* ─────────────────────────────────────────────────────
   CHAT: INPUT
───────────────────────────────────────────────────── */
[data-testid="stChatInput"] {
    border: 0.5px solid var(--border-med) !important;
    border-radius: 10px !important;
    background: var(--white) !important;
    box-shadow: none !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 3px var(--amber-ring) !important;
}
[data-testid="stChatInput"] textarea {
    font-size: 0.82rem !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--ink) !important;
    background: transparent !important;
}

/* ─────────────────────────────────────────────────────
   SOURCE CARD
───────────────────────────────────────────────────── */
.src-card {
    background: var(--paper);
    border: 0.5px solid var(--border);
    border-left: 2.5px solid var(--amber);
    border-radius: 0 8px 8px 0;
    padding: 0.58rem 0.85rem;
    margin: 0.38rem 0;
}
.sc-file {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; font-weight: 500;
    color: var(--ink);
    display: flex; align-items: center; gap: 5px; flex-wrap: wrap;
    margin-bottom: 0.22rem;
}
.sc-body { font-size: 0.78rem; color: var(--muted); line-height: 1.54; }
.match-badge {
    display: inline-block; padding: 1px 5px; border-radius: 4px;
    background: #EBF4DE; color: #3A6B10;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem; font-weight: 500;
}

/* ─────────────────────────────────────────────────────
   EXPANDER (sources)
───────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 0.5px solid var(--border-med) !important;
    border-radius: 8px !important;
    background: var(--white) !important;
    box-shadow: none !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.77rem !important;
    color: var(--muted) !important;
    padding: 0.48rem 0.75rem !important;
}
[data-testid="stExpander"] summary:hover { color: var(--ink) !important; }
[data-testid="stExpander"] > div:last-child {
    padding: 0.1rem 0.5rem 0.5rem !important;
}

/* ─────────────────────────────────────────────────────
   PROGRESS BAR
───────────────────────────────────────────────────── */
[data-testid="stProgressBar"] > div {
    background: var(--amber) !important;
    border-radius: 2px !important;
}

/* ─────────────────────────────────────────────────────
   WELCOME CARDS
───────────────────────────────────────────────────── */
.wc {
    background: var(--white);
    border: 0.5px solid var(--border-med);
    border-radius: 10px;
    padding: 1rem 1.1rem;
    height: 100%;
}
.wc-icon {
    font-size: 1rem;
    color: var(--amber);
    margin-bottom: 0.3rem;
    font-weight: 500;
}
.wc-title {
    font-family: 'DM Serif Display', serif !important;
    font-size: 0.95rem;
    font-weight: 400 !important;
    color: var(--ink);
    margin-bottom: 0.18rem;
}
.wc-body { font-size: 0.77rem; color: var(--muted); line-height: 1.55; margin: 0; }

/* ─────────────────────────────────────────────────────
   MISC
───────────────────────────────────────────────────── */
[data-testid="stAlert"]  { border-radius: 8px !important; font-size: 0.79rem !important; }
[data-testid="stSpinner"] p { font-size: 0.79rem !important; color: var(--muted) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "chat_history":        [],
        "documents_processed": [],
        "vector_store":        None,
        "rag_chain":           None,
        "processor":           None,
        "query_count":         0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def initialize_components():
    if st.session_state.vector_store is None:
        st.session_state.vector_store = VectorStore()
        st.session_state.rag_chain    = RAGChain(st.session_state.vector_store)
        st.session_state.processor    = DocumentProcessor()


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _ext_icon(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return {"pdf": "📄", "docx": "📝", "txt": "📃", "csv": "📊"}.get(ext, "📁")


def _total_chunks() -> int:
    return sum(d["chunks"] for d in st.session_state.documents_processed)


def _active_source(filter_doc: str) -> str:
    if not st.session_state.documents_processed:
        return ""
    if filter_doc and filter_doc != "All documents":
        return filter_doc
    return st.session_state.documents_processed[0]["name"]


def _pluralise(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


# ─────────────────────────────────────────────────────────────────────────────
# DOCUMENT OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────
def process_documents(uploaded_files):
    existing  = {d["name"] for d in st.session_state.documents_processed}
    new_files = [f for f in uploaded_files if f.name not in existing]

    if not new_files:
        st.sidebar.warning("All selected files are already loaded.")
        return

    pb     = st.sidebar.progress(0)
    status = st.sidebar.empty()

    for i, file in enumerate(new_files):
        status.info(f"Processing {file.name}…")
        try:
            chunks = st.session_state.processor.process_file(file)
            if chunks and st.session_state.vector_store.add_documents(chunks):
                st.session_state.documents_processed.append({
                    "name":         file.name,
                    "chunks":       len(chunks),
                    "processed_at": datetime.now().strftime("%H:%M"),
                })
        except Exception as e:
            status.error(f"Failed: {file.name} — {e}")
            time.sleep(1.5)

        pb.progress((i + 1) / len(new_files))

    status.success(f"✓ {_pluralise(len(new_files), 'file')} ready")
    time.sleep(1.2)
    pb.empty()
    status.empty()
    st.rerun()


def delete_document(doc_name: str):
    st.session_state.vector_store.delete_document(doc_name)
    st.session_state.documents_processed = [
        d for d in st.session_state.documents_processed
        if d["name"] != doc_name
    ]
    st.rerun()


def reset_app():
    if st.session_state.vector_store:
        st.session_state.vector_store.reset()
    st.session_state.chat_history        = []
    st.session_state.documents_processed = []
    st.session_state.query_count         = 0
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar() -> str:
    with st.sidebar:

        # Brand
        st.markdown("""
<div class="sb-brand">
    <div class="mark">AI</div>
    <div>
        <p class="nm">DocuMind</p>
        <p class="tg">document intelligence</p>
    </div>
</div>""", unsafe_allow_html=True)

        # Upload
        st.markdown("<span class='sb-lbl'>Upload</span>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Drop files",
            type=["pdf", "docx", "txt", "csv"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded_files:
            if st.button("Process files →", use_container_width=True,
                         key="process_btn"):
                process_documents(uploaded_files)

        st.markdown("<hr class='sb-divider'/>", unsafe_allow_html=True)

        # Loaded documents
        if st.session_state.documents_processed:
            st.markdown("<span class='sb-lbl'>Loaded documents</span>",
                        unsafe_allow_html=True)

            for i, doc in enumerate(st.session_state.documents_processed):
                col_doc, col_del = st.columns([5, 1])
                with col_doc:
                    st.markdown(f"""
<div class="doc-item">
    <span class="di-icon">{_ext_icon(doc['name'])}</span>
    <div>
        <span class="di-name" title="{doc['name']}">{doc['name']}</span>
        <span class="di-meta">{doc['chunks']} chunks · {doc['processed_at']}</span>
    </div>
</div>""", unsafe_allow_html=True)
                with col_del:
                    st.markdown("<div style='margin-top:3px'>",
                                unsafe_allow_html=True)
                    if st.button("✕", key=f"del_{i}",
                                 help=f"Remove {doc['name']}"):
                        delete_document(doc["name"])
                    st.markdown("</div>", unsafe_allow_html=True)

            # Stats
            st.markdown(f"""
<div class="sb-stats">
    <div class="ss">
        <div class="sv">{len(st.session_state.documents_processed)}</div>
        <div class="sl">documents</div>
    </div>
    <div class="ss">
        <div class="sv">{_total_chunks()}</div>
        <div class="sl">chunks</div>
    </div>
</div>""", unsafe_allow_html=True)

            st.markdown("<hr class='sb-divider'/>", unsafe_allow_html=True)

        # Search scope
        st.markdown("<span class='sb-lbl'>Search scope</span>",
                    unsafe_allow_html=True)
        filter_doc = st.selectbox(
            "Scope",
            options=(["All documents"] +
                     [d["name"] for d in st.session_state.documents_processed]),
            label_visibility="collapsed",
        )

        st.markdown("<hr class='sb-divider'/>", unsafe_allow_html=True)

        # Bottom controls
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Reset all", use_container_width=True, key="reset_btn"):
                reset_app()
        with c2:
            st.markdown(
                f"<p style='font-family:JetBrains Mono,monospace;font-size:0.61rem;"
                f"color:rgba(255,255,255,0.26);text-align:right;margin-top:0.42rem'>"
                f"{st.session_state.query_count} "
                f"{'query' if st.session_state.query_count == 1 else 'queries'}"
                f"</p>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<p class='tech-badge'>Groq · LangChain · FAISS</p>",
            unsafe_allow_html=True,
        )

    return filter_doc


# ─────────────────────────────────────────────────────────────────────────────
# SOURCE CARDS
# ─────────────────────────────────────────────────────────────────────────────
def render_sources(sources: list):
    if not sources:
        return
    with st.expander("📖 View sources"):
        for source in sources[:3]:
            name    = source["metadata"].get("source", "Unknown")
            page    = source["metadata"].get("page", "")
            score   = source.get("score", 0)
            pg_str  = f" · p. {page}" if page else ""
            badge   = f'<span class="match-badge">{score:.0%} match</span>'
            snippet = source["content"][:240].strip()
            st.markdown(f"""
<div class="src-card">
    <div class="sc-file">{name}{pg_str}{badge}</div>
    <div class="sc-body">{snippet}…</div>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# WELCOME SCREEN
# ─────────────────────────────────────────────────────────────────────────────
def render_welcome():
    col1, col2, col3 = st.columns(3)
    cards = [
        ("↑",  "Upload",
         "Drop any PDF, DOCX, TXT, or CSV into the sidebar and hit Process."),
        ("→",  "Ask",
         "Type any question and get precise, sourced answers from your documents."),
        ("✦",  "Insights",
         "Summarize documents or extract key findings instantly."),
    ]
    for col, (icon, title, body) in zip([col1, col2, col3], cards):
        with col:
            st.markdown(f"""
<div class="wc">
    <div class="wc-icon">{icon}</div>
    <div class="wc-title">{title}</div>
    <p class="wc-body">{body}</p>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CHAT HANDLER
# ─────────────────────────────────────────────────────────────────────────────
def handle_question(question: str, filter_doc: str):
    st.session_state.chat_history.append({"role": "user", "content": question})

    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("Searching…"):
            filter_source = (None if filter_doc == "All documents"
                             else filter_doc)
            try:
                answer, sources = st.session_state.rag_chain.get_answer(
                    question=question,
                    chat_history=st.session_state.chat_history[:-1],
                    filter_source=filter_source,
                )
            except Exception as e:
                answer  = (f"Something went wrong while searching. "
                           f"Please try again.\n\n_Error: {e}_")
                sources = []

        st.markdown(answer)
        if sources:
            render_sources(sources)

    st.session_state.chat_history.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )
    st.session_state.query_count += 1


# ─────────────────────────────────────────────────────────────────────────────
# MAIN VIEW
# ─────────────────────────────────────────────────────────────────────────────
def render_chat(filter_doc: str):
    docs_loaded = bool(st.session_state.documents_processed)

    # Header
    if docs_loaded:
        n_q  = st.session_state.query_count
        n_d  = len(st.session_state.documents_processed)
        meta = (f"· {_pluralise(n_q, 'query')} "
                f"· {_pluralise(n_d, 'doc')} loaded")
    else:
        meta = "· upload a document to begin"

    st.markdown(f"""
<div class="page-header">
    <h1>Ask your <em>documents</em></h1>
    <span class="ph-meta">{meta}</span>
</div>""", unsafe_allow_html=True)

    # Quick actions
    if docs_loaded:
        c1, c2, c3, c4 = st.columns([1, 1, 1.25, 1])

        with c1:
            if st.button("📋 Summarize", use_container_width=True, key="qa_sum"):
                src = _active_source(filter_doc)
                if src:
                    with st.spinner("Summarizing…"):
                        try:
                            text = st.session_state.rag_chain.summarize_document(src)
                        except Exception as e:
                            text = f"Could not summarize. Error: {e}"
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"**Summary**\n\n{text}",
                        "sources": [],
                    })
                    st.rerun()

        with c2:
            if st.button("💡 Key insights", use_container_width=True, key="qa_ins"):
                src = _active_source(filter_doc)
                if src:
                    with st.spinner("Extracting…"):
                        try:
                            text = st.session_state.rag_chain.extract_key_insights(src)
                        except Exception as e:
                            text = f"Could not extract insights. Error: {e}"
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"**Key insights**\n\n{text}",
                        "sources": [],
                    })
                    st.rerun()

        with c3:
            if st.button("❓ Suggest questions", use_container_width=True,
                         key="qa_sug"):
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": (
                        "**Questions to try:**\n\n"
                        "- What is the main topic of this document?\n"
                        "- What are the key findings or conclusions?\n"
                        "- Are there any important dates or deadlines?\n"
                        "- What recommendations are made?\n"
                        "- What data or statistics are highlighted?"
                    ),
                    "sources": [],
                })
                st.rerun()

        with c4:
            if st.button("🗑️ Clear chat", use_container_width=True, key="qa_clr"):
                st.session_state.chat_history = []
                st.rerun()

        st.markdown("<hr class='main-divider'/>", unsafe_allow_html=True)

    # Chat or welcome
    if not st.session_state.chat_history:
        render_welcome()
    else:
        for msg in st.session_state.chat_history:
            avatar = "👤" if msg["role"] == "user" else "🧠"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and msg.get("sources"):
                    render_sources(msg["sources"])

    # Input
    placeholder = (
        "Ask anything about your documents…"
        if docs_loaded
        else "Upload and process a document first…"
    )
    if question := st.chat_input(placeholder, disabled=not docs_loaded):
        handle_question(question, filter_doc)


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def main():
    init_session_state()
    initialize_components()
    filter_doc = render_sidebar()
    render_chat(filter_doc)


if __name__ == "__main__":
    main()
