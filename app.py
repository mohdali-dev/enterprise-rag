import streamlit as st
from dotenv import load_dotenv
import os
from datetime import datetime
import time

from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.rag_chain import RAGChain

load_dotenv()

# Page config
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "DocuMind AI - Intelligent Document Analysis"}
)

# Custom CSS
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #667eea;
        --secondary: #764ba2;
        --success: #10b981;
        --danger: #ef4444;
        --warning: #f59e0b;
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
        }
    }
    
    @media (prefers-color-scheme: light) {
        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
        }
    }
    
    /* Main container */
    .main {
        padding-top: 2rem;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Card styling */
    .card {
        background: var(--bg-secondary);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(102, 126, 234, 0.1);
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
    
    .card-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: #667eea;
    }
    
    /* Document list */
    .doc-item {
        background: var(--bg-primary);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.75rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid #667eea;
    }
    
    .doc-name {
        font-weight: 500;
        color: var(--text-primary);
    }
    
    .doc-info {
        font-size: 0.85rem;
        color: var(--text-secondary);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* Chat messages */
    .stChatMessage {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 1rem;
    }
    
    .stChatMessage[data-testid="ChatMessage"]:has(p:first-child:contains("user")) {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background: var(--bg-secondary);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: auto;
        padding: 0.75rem 1.5rem;
        border-radius: 8px 8px 0 0;
    }
    
    /* Success messages */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        border-radius: 8px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(102, 126, 234, 0.05);
        border-radius: 8px;
    }
    
    /* Source cards */
    .source-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.05) 100%);
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.75rem 0;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .source-card:hover {
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.15);
    }
    
    .source-title {
        font-weight: 600;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .source-content {
        font-size: 0.9rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }
    
    .source-meta {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    /* Quick action buttons */
    .quick-action-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    
    .quick-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Loading animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    defaults = {
        "chat_history": [],
        "documents_processed": [],
        "vector_store": None,
        "rag_chain": None,
        "processor": None,
        "query_count": 0,
        "theme": "light"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def initialize_components():
    if st.session_state.vector_store is None:
        st.session_state.vector_store = VectorStore()
        st.session_state.rag_chain = RAGChain(st.session_state.vector_store)
        st.session_state.processor = DocumentProcessor()

def render_sidebar():
    with st.sidebar:
        # Logo/Title
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='margin: 0; font-size: 2rem;'>🧠</h1>
            <p style='margin: 0.5rem 0 0 0; font-weight: 600;'>DocuMind AI</p>
            <p style='margin: 0; font-size: 0.85rem; opacity: 0.7;'>Document Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Upload section
        st.markdown("### 📁 Upload Documents")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            type=["pdf", "docx", "txt", "csv"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Process", use_container_width=True, key="process_btn"):
                    process_documents(uploaded_files)
            with col2:
                st.write("")  # Spacer
        
        st.markdown("---")
        
        # Documents list
        if st.session_state.documents_processed:
            st.markdown("### 📚 Loaded Documents")
            st.markdown(f"**Total:** {len(st.session_state.documents_processed)} files")
            
            for i, doc in enumerate(st.session_state.documents_processed):
                col1, col2, col3 = st.columns([2, 1, 0.5])
                with col1:
                    st.markdown(f"📄 **{doc['name'][:18]}...**")
                with col2:
                    st.caption(f"{doc['chunks']} chunks")
                with col3:
                    if st.button("🗑️", key=f"del_{i}", help="Delete"):
                        delete_document(doc['name'])
        
        st.markdown("---")
        
        # Filter section
        st.markdown("### 🔍 Filter")
        filter_doc = st.selectbox(
            "Document",
            options=["All Documents"] + [d['name'] for d in st.session_state.documents_processed],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Actions section
        st.markdown("### ⚙️ Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset", use_container_width=True, key="reset_btn"):
                reset_app()
        with col2:
            if st.button("📊 Stats", use_container_width=True, key="stats_btn"):
                st.session_state.show_stats = True
        
        st.markdown("---")
        st.caption("Made with ❤️ using Groq & LangChain")
        
        return filter_doc

def process_documents(uploaded_files):
    new_files = [
        f for f in uploaded_files
        if f.name not in [d['name'] for d in st.session_state.documents_processed]
    ]
    
    if not new_files:
        st.sidebar.warning("Documents already processed!")
        return
    
    progress_container = st.sidebar.container()
    progress_bar = progress_container.progress(0)
    status = progress_container.empty()
    
    for i, file in enumerate(new_files):
        status.info(f"⏳ Processing {file.name}...")
        chunks = st.session_state.processor.process_file(file)
        
        if chunks:
            success = st.session_state.vector_store.add_documents(chunks)
            
            if success:
                st.session_state.documents_processed.append({
                    "name": file.name,
                    "chunks": len(chunks),
                    "processed_at": datetime.now().strftime("%H:%M")
                })
        
        progress_bar.progress((i + 1) / len(new_files))
    
    status.success("✅ All documents processed!")
    time.sleep(1.5)
    progress_container.empty()
    st.rerun()

def delete_document(doc_name: str):
    st.session_state.vector_store.delete_document(doc_name)
    st.session_state.documents_processed = [
        d for d in st.session_state.documents_processed
        if d['name'] != doc_name
    ]
    st.rerun()

def reset_app():
    if st.session_state.vector_store:
        st.session_state.vector_store.reset()
    st.session_state.chat_history = []
    st.session_state.documents_processed = []
    st.session_state.query_count = 0
    st.rerun()

def render_sources(sources: list):
    with st.expander("📚 Sources & References"):
        for i, source in enumerate(sources[:3], 1):
            source_name = source["metadata"].get("source", "Unknown")
            page = source["metadata"].get("page", "")
            score = source.get("score", 0)
            
            page_info = f", Page {page}" if page else ""
            
            st.markdown(f"""
<div class='source-card'>
    <div class='source-title'>Source {i}: {source_name}{page_info}</div>
    <div class='source-content'>{source['content'][:200]}...</div>
    <div class='source-meta'>Relevance: {score:.0%}</div>
</div>
""", unsafe_allow_html=True)

def handle_question(question: str, filter_doc: str):
    st.session_state.chat_history.append({"role": "user", "content": question})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)
    
    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("🤔 Analyzing documents..."):
            filter_source = None if filter_doc == "All Documents" else filter_doc
            
            answer, sources = st.session_state.rag_chain.get_answer(
                question=question,
                chat_history=st.session_state.chat_history[:-1],
                filter_source=filter_source
            )
        
        st.markdown(answer)
        
        if sources:
            render_sources(sources)
    
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })
    
    st.session_state.query_count += 1

def render_welcome():
    st.markdown("""
<div class='header-container'>
    <h1 class='header-title'>🧠 DocuMind AI</h1>
    <p class='header-subtitle'>Intelligent Document Analysis & Q&A</p>
</div>
""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
<div class='card'>
    <div class='card-title'>📤 Upload</div>
    <p>Upload PDF, DOCX, TXT, or CSV files from the sidebar</p>
</div>
""", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
<div class='card'>
    <div class='card-title'>💬 Chat</div>
    <p>Ask questions and get instant answers with sources</p>
</div>
""", unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
<div class='card'>
    <div class='card-title'>✨ Insights</div>
    <p>Generate summaries and extract key information</p>
</div>
""", unsafe_allow_html=True)

def render_chat(filter_doc: str):
    st.markdown("""
<div class='header-container'>
    <h1 class='header-title'>🧠 DocuMind AI</h1>
    <p class='header-subtitle'>Chat with your documents intelligently</p>
</div>
""", unsafe_allow_html=True)
    
    # Quick actions
    if st.session_state.documents_processed:
        st.markdown("### ⚡ Quick Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📋 Summarize", use_container_width=True, key="summarize"):
                source = filter_doc if filter_doc != "All Documents" else st.session_state.documents_processed[0]["name"]
                with st.spinner("📝 Generating summary..."):
                    summary = st.session_state.rag_chain.summarize_document(source)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"**📋 Document Summary**\n\n{summary}",
                    "sources": []
                })
                st.rerun()
        
        with col2:
            if st.button("💡 Key Insights", use_container_width=True, key="insights"):
                source = filter_doc if filter_doc != "All Documents" else st.session_state.documents_processed[0]["name"]
                with st.spinner("💡 Extracting insights..."):
                    insights = st.session_state.rag_chain.extract_key_insights(source)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"**💡 Key Insights**\n\n{insights}",
                    "sources": []
                })
                st.rerun()
        
        with col3:
            if st.button("❓ Sample Q", use_container_width=True, key="samples"):
                samples = """**Suggested Questions:**
• What is the main topic of this document?
• What are the key findings or conclusions?
• Are there any important dates or deadlines mentioned?
• What recommendations are made?
• What data or statistics are highlighted?"""
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": samples,
                    "sources": []
                })
                st.rerun()
        
        with col4:
            if st.button("🗑️ Clear Chat", use_container_width=True, key="clear"):
                st.session_state.chat_history = []
                st.rerun()
        
        st.markdown("---")
    
    # Chat display
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.chat_history:
            render_welcome()
        else:
            for message in st.session_state.chat_history:
                avatar = "👤" if message["role"] == "user" else "🧠"
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])
                    
                    if message["role"] == "assistant" and "sources" in message and message["sources"]:
                        render_sources(message["sources"])
    
    # Chat input
    st.markdown("---")
    
    if question := st.chat_input(
        "💬 Ask anything about your documents...",
        disabled=not st.session_state.documents_processed
    ):
        handle_question(question, filter_doc)

def main():
    init_session_state()
    initialize_components()
    
    filter_doc = render_sidebar()
    render_chat(filter_doc)

if __name__ == "__main__":
    main()