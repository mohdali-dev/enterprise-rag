import os
from dotenv import load_dotenv

# Load .env FIRST
load_dotenv()

import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
import time

from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.rag_chain import RAGChain

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "DocuMind AI — Intelligent Document Analysis"},
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Hide Streamlit chrome ── */
#MainMenu, header, footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
.stDeployButton { display: none; }

/* ── Tokens ── */
:root {
    --ink:        #0F0F1A;
    --amber:      #E8A030;
    --amber-soft: rgba(232,160,48,0.10);
    --amber-ring: rgba(232,160,48,0.18);
    --paper:      #FAFAF8;
    --white:      #FFFFFF;
    --muted:      #6B7280;
    --border:     rgba(0,0,0,0.07);
    --sb-bg:      #0F0F1A;
    --sb-border:  rgba(255,255,255,0.07);
    --sb-text:    rgba(255,255,255,0.75);
    --sb-muted:   rgba(255,255,255,0.30);
    --sb-hover:   rgba(232,160,48,0.09);
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}
.main {
    background: var(--paper) !important;
    padding-top: 0 !important;
}
.block-container {
    padding-top: 1.75rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}

/* ── Sidebar shell ── */
section[data-testid="stSidebar"] {
    background: var(--sb-bg) !important;
    border-right: 1px solid var(--sb-border) !important;
}
section[data-testid="stSidebar"] > div {
    padding-top: 1.25rem !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(232,160,48,0.25);
    border-radius: 2px;
}

/* ── Sidebar brand ── */
.sb-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 0 1rem;
    border-bottom: 1px solid var(--sb-border);
    margin-bottom: 0.25rem;
}
.sb-brand .mark {
    width: 36px; height: 36px;
    border-radius: 9px;
    background: var(--amber);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}
.sb-brand .nm {
    font-family: 'DM Serif Display', serif;
    font-size: 1.05rem;
    color: #F5F0E8;
    margin: 0; line-height: 1.1;
}
.sb-brand .tg {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--sb-muted);
    letter-spacing: 0.05em;
    margin: 0;
}

/* ── Sidebar label ── */
.sb-lbl {
    font-size: 0.61rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--sb-muted);
    margin: 0.85rem 0 0.4rem;
    display: block;
}
/* Force dark upload zone */
[data-testid="stFileUploader"] * {
    background-color: transparent !important;
}
/* ── File uploader override ── */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: transparent !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div {
    border: 1px dashed rgba(255,255,255,0.13) !important;
    border-radius: 8px !important;
    background: rgba(255,255,255,0.03) !important;
    padding: 0.75rem !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] p,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] small {
    color: var(--sb-muted) !important;
    font-size: 0.75rem !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background: rgba(255,255,255,0.06) !important;
    border: 0.5px solid rgba(255,255,255,0.12) !important;
    color: var(--sb-text) !important;
    border-radius: 6px !important;
    font-size: 0.75rem !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"],
section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div > div,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div > div > div,
section[data-testid="stSidebar"] [data-testeid="stFileUploader"] section {
    background: rgba(255,255,255,0.03) !important;
    border: 1px dashed rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
    color: var(--sb-muted) !important;
}
/* ── Doc item ── */
.doc-item {
    display: flex;
    align-items: flex-start;
    gap: 7px;
    padding: 7px 9px;
    border-radius: 7px;
    border: 0.5px solid var(--sb-border);
    margin-bottom: 4px;
    transition: background 0.15s, border-color 0.15s;
}
.doc-item:hover {
    background: var(--sb-hover);
    border-color: rgba(232,160,48,0.22);
}
.doc-item .di-icon {
    font-size: 0.88rem;
    flex-shrink: 0;
    margin-top: 2px;
}
.doc-item .di-name {
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--sb-text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 132px;
    display: block;
}
.doc-item .di-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.63rem;
    color: var(--sb-muted);
    display: block;
}

/* ── Stats pills ── */
.sb-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 5px;
    margin-top: 0.6rem;
}
.ss {
    background: rgba(255,255,255,0.04);
    border: 0.5px solid var(--sb-border);
    border-radius: 7px;
    padding: 7px 9px;
    text-align: center;
}
.ss .sv {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #F5F0E8;
    line-height: 1;
}
.ss .sl {
    font-size: 0.62rem;
    color: var(--sb-muted);
    margin-top: 2px;
}

/* ── Sidebar buttons ── */
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    color: var(--sb-text) !important;
    border: 0.5px solid var(--sb-border) !important;
    border-radius: 7px !important;
    font-size: 0.76rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 0.8rem !important;
    box-shadow: none !important;
    transition: all 0.15s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--sb-hover) !important;
    border-color: rgba(232,160,48,0.25) !important;
    color: var(--amber) !important;
}

/* ── Selectbox in sidebar ── */
section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 0.5px solid var(--sb-border) !important;
    border-radius: 7px !important;
    font-size: 0.76rem !important;
    color: var(--sb-text) !important;
}

/* ── Tech badge ── */
.tech-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: var(--sb-muted);
    text-align: center;
    letter-spacing: 0.04em;
    padding-top: 0.6rem;
    border-top: 1px solid var(--sb-border);
    margin-top: 0.5rem;
}

/* ── Page header ── */
.page-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    padding-bottom: 0.85rem;
    margin-bottom: 0.9rem;
    border-bottom: 1px solid var(--border);
}
.page-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.75rem;
    font-weight: 400;
    color: var(--ink);
    margin: 0;
    letter-spacing: -0.4px;
}
.page-header h1 em {
    color: var(--amber);
    font-style: normal;
}
.ph-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--muted);
}

/* ── Quick action bar ── */
.qa-bar {
    display: flex;
    gap: 6px;
    margin-bottom: 0.85rem;
    flex-wrap: wrap;
}

/* ── Main area buttons (quick actions) ── */
.stButton > button {
    background: var(--white) !important;
    color: var(--muted) !important;
    border: 0.5px solid var(--border) !important;
    border-radius: 7px !important;
    font-size: 0.76rem !important;
    font-weight: 400 !important;
    padding: 0.38rem 0.9rem !important;
    box-shadow: none !important;
    transition: border-color 0.15s, color 0.15s !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    border-color: var(--amber) !important;
    color: var(--ink) !important;
    background: #FFFCF5 !important;
}

/* ── Chat messages — hide default Streamlit avatar styling ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.1rem 0 !important;
    gap: 10px !important;
}

/* ── User bubble ── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: var(--ink) !important;
    color: #F5F0E8 !important;
    border-radius: 12px 12px 3px 12px !important;
    border: none !important;
    padding: 0.6rem 0.95rem !important;
    max-width: 68% !important;
    align-self: flex-end !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] p {
    color: #F5F0E8 !important;
    font-size: 0.84rem !important;
    line-height: 1.6 !important;
    margin: 0 !important;
}

/* ── Assistant bubble ── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: var(--white) !important;
    border: 0.5px solid var(--border) !important;
    border-radius: 3px 12px 12px 12px !important;
    padding: 0.7rem 1rem !important;
    max-width: 82% !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] li {
    font-size: 0.84rem !important;
    line-height: 1.68 !important;
    color: var(--ink) !important;
    margin-bottom: 0.25rem !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] strong {
    font-weight: 500 !important;
    color: var(--ink) !important;
}

/* ── Avatar icons ── */
[data-testid="chatAvatarIcon-user"] {
    background: rgba(0,0,0,0.06) !important;
    border: 0.5px solid var(--border) !important;
    color: var(--muted) !important;
}
[data-testid="chatAvatarIcon-assistant"] {
    background: var(--amber) !important;
    border: none !important;
    color: var(--ink) !important;
}
[data-testid="chatAvatarIcon-assistant"] svg {
    color: var(--ink) !important;
    fill: var(--ink) !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    border: 0.5px solid rgba(0,0,0,0.12) !important;
    border-radius: 10px !important;
    background: var(--white) !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 3px var(--amber-ring) !important;
}
[data-testid="stChatInput"] textarea {
    font-size: 0.83rem !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--ink) !important;
}

/* ── Source card ── */
.src-card {
    background: var(--paper);
    border: 0.5px solid var(--border);
    border-left: 2.5px solid var(--amber);
    border-radius: 0 8px 8px 0;
    padding: 0.6rem 0.9rem;
    margin: 0.4rem 0;
}
.src-card .sc-file {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.71rem;
    font-weight: 500;
    color: var(--ink);
    margin-bottom: 0.25rem;
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
}
.src-card .sc-body {
    font-size: 0.79rem;
    color: var(--muted);
    line-height: 1.55;
}
.match-badge {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 4px;
    background: #EAF3DE;
    color: #3B6D11;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    font-weight: 500;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    border: 0.5px solid var(--border) !important;
    border-radius: 8px !important;
    background: var(--white) !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.78rem !important;
    color: var(--muted) !important;
    padding: 0.5rem 0.75rem !important;
}
[data-testid="stExpander"] summary:hover {
    color: var(--ink) !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div {
    background: var(--amber) !important;
    border-radius: 2px !important;
}

/* ── Welcome cards ── */
.wc {
    background: var(--white);
    border: 0.5px solid var(--border);
    border-radius: 10px;
    padding: 1.1rem 1.15rem;
    height: 100%;
}
.wc-icon { font-size: 1.2rem; margin-bottom: 0.35rem; }
.wc-title {
    font-family: 'DM Serif Display', serif;
    font-size: 0.95rem;
    font-weight: 400;
    color: var(--ink);
    margin-bottom: 0.2rem;
}
.wc-body {
    font-size: 0.78rem;
    color: var(--muted);
    line-height: 1.55;
    margin: 0;
}

/* ── Divider ── */
.sb-divider {
    border: none;
    border-top: 1px solid var(--sb-border);
    margin: 0.55rem 0;
}
.main-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 0.6rem 0 0.85rem;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-size: 0.8rem !important;
}
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "chat_history": [],
        "documents_processed": [],
        "vector_store": None,
        "rag_chain": None,
        "processor": None,
        "query_count": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def initialize_components():
    if st.session_state.vector_store is None:
        st.session_state.vector_store = VectorStore()
        st.session_state.rag_chain = RAGChain(st.session_state.vector_store)
        st.session_state.processor = DocumentProcessor()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _ext_icon(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return {"pdf": "📄", "docx": "📝", "txt": "📃", "csv": "📊"}.get(ext, "📁")


def _total_chunks() -> int:
    return sum(d["chunks"] for d in st.session_state.documents_processed)


def _active_source(filter_doc: str) -> str:
    if filter_doc != "All documents" and filter_doc:
        return filter_doc
    return st.session_state.documents_processed[0]["name"]


# ── Document ops ──────────────────────────────────────────────────────────────
def process_documents(uploaded_files):
    existing = {d["name"] for d in st.session_state.documents_processed}
    new_files = [f for f in uploaded_files if f.name not in existing]

    if not new_files:
        st.sidebar.warning("All selected files are already loaded.")
        return

    pb = st.sidebar.progress(0)
    status = st.sidebar.empty()

    for i, file in enumerate(new_files):
        status.info(f"Processing {file.name}…")
        chunks = st.session_state.processor.process_file(file)
        if chunks and st.session_state.vector_store.add_documents(chunks):
            st.session_state.documents_processed.append({
                "name": file.name,
                "chunks": len(chunks),
                "processed_at": datetime.now().strftime("%H:%M"),
            })
        pb.progress((i + 1) / len(new_files))

    status.success(f"✓ {len(new_files)} file(s) ready")
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
    st.session_state.chat_history = []
    st.session_state.documents_processed = []
    st.session_state.query_count = 0
    st.rerun()


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Brand
        st.markdown("""
<div class="sb-brand">
    <div class="mark">🧠</div>
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
            if st.button("Process files →", use_container_width=True, key="process_btn"):
                process_documents(uploaded_files)

        st.markdown("<hr class='sb-divider'/>", unsafe_allow_html=True)

        # Loaded docs
        if st.session_state.documents_processed:
            st.markdown("<span class='sb-lbl'>Loaded documents</span>",
                        unsafe_allow_html=True)

            for i, doc in enumerate(st.session_state.documents_processed):
                col_doc, col_del = st.columns([5, 1])
                with col_doc:
                    icon = _ext_icon(doc["name"])
                    st.markdown(f"""
<div class="doc-item">
    <span class="di-icon">{icon}</span>
    <div>
        <span class="di-name" title="{doc['name']}">{doc['name']}</span>
        <span class="di-meta">{doc['chunks']} chunks · {doc['processed_at']}</span>
    </div>
</div>""", unsafe_allow_html=True)
                with col_del:
                    st.markdown("<div style='margin-top:3px'>", unsafe_allow_html=True)
                    if st.button("✕", key=f"del_{i}", help=f"Remove {doc['name']}"):
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

        # Scope filter
        st.markdown("<span class='sb-lbl'>Search scope</span>",
                    unsafe_allow_html=True)
        filter_doc = st.selectbox(
            "Scope",
            options=["All documents"] + [d["name"] for d in
                                         st.session_state.documents_processed],
            label_visibility="collapsed",
        )

        st.markdown("<hr class='sb-divider'/>", unsafe_allow_html=True)

        # Bottom row
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Reset all", use_container_width=True, key="reset_btn"):
                reset_app()
        with c2:
            st.markdown(
                f"<p style='font-family:JetBrains Mono,monospace;font-size:0.63rem;"
                f"color:rgba(255,255,255,0.28);text-align:right;margin-top:0.45rem'>"
                f"{st.session_state.query_count} queries</p>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<p class='tech-badge'>Groq · LangChain · FAISS</p>",
            unsafe_allow_html=True,
        )

    return filter_doc


# ── Source rendering ──────────────────────────────────────────────────────────
def render_sources(sources: list):
    if not sources:
        return
    with st.expander("📖 View sources"):
        for source in sources[:3]:
            name = source["metadata"].get("source", "Unknown")
            page = source["metadata"].get("page", "")
            score = source.get("score", 0)
            page_str = f" · p. {page}" if page else ""
            badge = f'<span class="match-badge">{score:.0%} match</span>'
            snippet = source["content"][:240].strip()
            st.markdown(f"""
<div class="src-card">
    <div class="sc-file">{name}{page_str}{badge}</div>
    <div class="sc-body">{snippet}…</div>
</div>""", unsafe_allow_html=True)


# ── Welcome screen ────────────────────────────────────────────────────────────
def render_welcome():
    col1, col2, col3 = st.columns(3)
    cards = [
        ("📤", "Upload",   "Drop any PDF, DOCX, TXT, or CSV into the sidebar and hit Process."),
        ("💬", "Ask",      "Type any question and get precise answers sourced from your documents."),
        ("✦",  "Insights", "Summarize documents or pull out key findings in one click."),
    ]
    for col, (icon, title, body) in zip([col1, col2, col3], cards):
        with col:
            st.markdown(f"""
<div class="wc">
    <div class="wc-icon">{icon}</div>
    <div class="wc-title">{title}</div>
    <p class="wc-body">{body}</p>
</div>""", unsafe_allow_html=True)


# ── Chat handler ──────────────────────────────────────────────────────────────
def handle_question(question: str, filter_doc: str):
    st.session_state.chat_history.append({"role": "user", "content": question})

    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("Searching…"):
            filter_source = (
                None if filter_doc == "All documents" else filter_doc
            )
            answer, sources = st.session_state.rag_chain.get_answer(
                question=question,
                chat_history=st.session_state.chat_history[:-1],
                filter_source=filter_source,
            )
        st.markdown(answer)
        if sources:
            render_sources(sources)

    st.session_state.chat_history.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )
    st.session_state.query_count += 1


# ── Main view ─────────────────────────────────────────────────────────────────
def render_chat(filter_doc: str):
    docs_loaded = bool(st.session_state.documents_processed)

    # Header
    if docs_loaded:
        meta = (
            f"· {st.session_state.query_count} "
            f"{'query' if st.session_state.query_count == 1 else 'queries'} "
            f"· {len(st.session_state.documents_processed)} "
            f"{'doc' if len(st.session_state.documents_processed) == 1 else 'docs'} loaded"
        )
    else:
        meta = "· upload documents to begin"

    st.markdown(f"""
<div class="page-header">
    <h1>Ask your <em>documents</em></h1>
    <span class="ph-meta">{meta}</span>
</div>""", unsafe_allow_html=True)

    # Quick actions — compact single row, only when docs loaded
    if docs_loaded:
        c1, c2, c3, c4 = st.columns([1, 1, 1.2, 1])

        with c1:
            if st.button("📋 Summarize", use_container_width=True, key="qa_sum"):
                with st.spinner("Summarizing…"):
                    text = st.session_state.rag_chain.summarize_document(
                        _active_source(filter_doc)
                    )
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"**Summary**\n\n{text}",
                    "sources": [],
                })
                st.rerun()

        with c2:
            if st.button("💡 Key insights", use_container_width=True, key="qa_ins"):
                with st.spinner("Extracting…"):
                    text = st.session_state.rag_chain.extract_key_insights(
                        _active_source(filter_doc)
                    )
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"**Key insights**\n\n{text}",
                    "sources": [],
                })
                st.rerun()

        with c3:
            if st.button("❓ Suggest questions", use_container_width=True, key="qa_sug"):
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": (
                        "**Questions to try:**\n\n"
                        "- What is the main topic of this document?\n"
                        "- What are the key findings or conclusions?\n"
                        "- Are there important dates or deadlines mentioned?\n"
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

    # Chat history or welcome
    if not st.session_state.chat_history:
        render_welcome()
    else:
        for msg in st.session_state.chat_history:
            avatar = "👤" if msg["role"] == "user" else "🧠"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and msg.get("sources"):
                    render_sources(msg["sources"])

    # Input — disabled until docs are loaded
    placeholder = (
        "Ask anything about your documents…"
        if docs_loaded
        else "Upload and process a document to start asking questions…"
    )
    if question := st.chat_input(placeholder, disabled=not docs_loaded):
        handle_question(question, filter_doc)


# ── Entry ─────────────────────────────────────────────────────────────────────
def main():
    init_session_state()
    initialize_components()
    filter_doc = render_sidebar()
    render_chat(filter_doc)


if __name__ == "__main__":
    main()