import streamlit as st
from dotenv import load_dotenv
import os
from datetime import datetime
import time

from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.rag_chain import RAGChain

load_dotenv()

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------
st.set_page_config(
    page_title="InsightDocs AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# Professional CSS (Production Grade)
# ---------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    
    /* Brand Header */
    .brand-header {
        text-align: center;
        padding: 2.5rem 0;
        margin-bottom: 2rem;
    }
    
    .brand-logo {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .brand-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .brand-subtitle {
        color: #64748b;
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        border-right: 1px solid #e2e8f0;
    }
    
    .sidebar-brand {
        text-align: center;
        padding: 2rem 1rem;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    .sidebar-logo {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .sidebar-title {
        font-size: 1.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .sidebar-tagline {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 0.9rem;
        font-weight: 600;
        color: #334155;
        margin: 1.5rem 0 0.75rem 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Document Cards */
    .doc-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.9rem;
        margin-bottom: 0.6rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .doc-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        transform: translateY(-1px);
    }
    
    .doc-name {
        font-weight: 600;
        color: #1e293b;
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
    }
    
    .doc-meta {
        font-size: 0.75rem;
        color: #94a3b8;
    }
    
    /* Chat Messages */
    .stChatMessage {
        background: transparent !important;
        padding: 1.25rem 1rem;
    }
    
    .stChatMessage[data-testid*="user"] {
        background: #f1f5f9 !important;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    .stChatMessage[data-testid*="assistant"] {
        background: white !important;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.25rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.25);
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.35);
        transform: translateY(-1px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #cbd5e1;
        border-radius: 10px;
        padding: 1.5rem;
        background: #f8fafc;
        transition: all 0.2s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #667eea;
        background: #f1f5f9;
    }
    
    /* Welcome Cards */
    .welcome-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .welcome-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .welcome-subtitle {
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Feature Grid */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.25rem;
        margin-top: 2rem;
    }
    
    .feature-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.75rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .feature-card:hover {
        border-color: #667eea;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
        transform: translateY(-4px);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
    }
    
    .feature-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        font-size: 0.9rem;
        color: #64748b;
        line-height: 1.5;
    }
    
    /* Source Cards */
    .source-card {
        background: #f8fafc;
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.75rem 0;
        transition: all 0.2s ease;
    }
    
    .source-card:hover {
        background: #f1f5f9;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
    }
    
    .source-title {
        font-weight: 600;
        color: #334155;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .source-content {
        font-size: 0.85rem;
        color: #64748b;
        line-height: 1.6;
        margin-bottom: 0.5rem;
    }
    
    .source-meta {
        font-size: 0.75rem;
        color: #94a3b8;
        padding-top: 0.5rem;
        border-top: 1px solid #e2e8f0;
    }
    
    /* Confidence Badge */
    .confidence-badge {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.75rem;
    }
    
    .confidence-high {
        background: #d1fae5;
        color: #065f46;
    }
    
    .confidence-medium {
        background: #fef3c7;
        color: #92400e;
    }
    
    .confidence-low {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Stats */
    .stat-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.25rem;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
    }
    
    /* Quick Actions */
    .quick-actions {
        margin-bottom: 2rem;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f8fafc;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Chat Input */
    .stChatInputContainer {
        border-top: 1px solid #e2e8f0;
        padding-top: 1rem;
        margin-top: 1rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Session State
# ---------------------------------------------------
def init_session():
    defaults = {
        "chat_history": [],
        "documents": [],
        "vector_store": None,
        "rag_chain": None,
        "processor": None,
        "total_queries": 0,
        "show_welcome": True
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def initialize():
    if st.session_state.vector_store is None:
        with st.spinner("🔄 Initializing AI systems..."):
            st.session_state.vector_store = VectorStore()
            st.session_state.processor = DocumentProcessor()
            st.session_state.rag_chain = RAGChain(st.session_state.vector_store)


# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class='sidebar-brand'>
            <div class='sidebar-logo'>📊</div>
            <div class='sidebar-title'>InsightDocs AI</div>
            <div class='sidebar-tagline'>Enterprise Document Intelligence</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Upload Section
        st.markdown("<div class='section-header'>📤 Upload Documents</div>", unsafe_allow_html=True)
        
        uploaded = st.file_uploader(
            "Choose files",
            type=["pdf", "docx", "txt", "csv"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        if uploaded:
            if st.button("🚀 Process Documents", use_container_width=True, type="primary"):
                process_docs(uploaded)
        
        # Documents List
        if st.session_state.documents:
            st.markdown(f"<div class='section-header'>📚 Documents ({len(st.session_state.documents)})</div>", unsafe_allow_html=True)
            
            for i, doc in enumerate(st.session_state.documents):
                st.markdown(f"""
                <div class='doc-card'>
                    <div class='doc-name'>📄 {doc['name'][:22]}{'...' if len(doc['name']) > 22 else ''}</div>
                    <div class='doc-meta'>{doc['chunks']} chunks • {doc['time']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Stats
        if st.session_state.documents:
            st.markdown("<div class='section-header'>📊 Statistics</div>", unsafe_allow_html=True)
            
            total_chunks = sum(d['chunks'] for d in st.session_state.documents)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-value'>{st.session_state.total_queries}</div>
                    <div class='stat-label'>Queries</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-value'>{total_chunks}</div>
                    <div class='stat-label'>Chunks</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Actions
        st.markdown("<div class='section-header'>⚙️ Actions</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset All", use_container_width=True):
                reset_app()
        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.show_welcome = True
                st.rerun()
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.caption("💡 Powered by Groq & LangChain")


# ---------------------------------------------------
# Document Processing
# ---------------------------------------------------
def process_docs(files):
    new_files = [f for f in files if f.name not in [d['name'] for d in st.session_state.documents]]
    
    if not new_files:
        st.warning("All files already processed!")
        return
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, file in enumerate(new_files):
        status_text.info(f"⏳ Processing **{file.name}**...")
        
        chunks = st.session_state.processor.process_file(file)
        
        if chunks:
            st.session_state.vector_store.add_documents(chunks)
            st.session_state.documents.append({
                "name": file.name,
                "chunks": len(chunks),
                "time": datetime.now().strftime("%H:%M")
            })
        
        progress_bar.progress((i + 1) / len(new_files))
    
    status_text.success(f"✅ Successfully processed {len(new_files)} document(s)!")
    st.session_state.show_welcome = False
    time.sleep(1.5)
    st.rerun()


def reset_app():
    if st.session_state.vector_store:
        st.session_state.vector_store.reset()
    st.session_state.chat_history = []
    st.session_state.documents = []
    st.session_state.total_queries = 0
    st.session_state.show_welcome = True
    st.rerun()


# ---------------------------------------------------
# Welcome Screen
# ---------------------------------------------------
def render_welcome():
    st.markdown("""
    <div class='welcome-container'>
        <div class='welcome-title'>Welcome to InsightDocs AI</div>
        <div class='welcome-subtitle'>Transform your documents into intelligent conversations</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-grid'>
        <div class='feature-card'>
            <div class='feature-icon'>📤</div>
            <div class='feature-title'>Upload Documents</div>
            <div class='feature-desc'>Support for PDF, DOCX, TXT, and CSV files</div>
        </div>
        <div class='feature-card'>
            <div class='feature-icon'>🔍</div>
            <div class='feature-title'>Smart Search</div>
            <div class='feature-desc'>AI-powered semantic search across all documents</div>
        </div>
        <div class='feature-card'>
            <div class='feature-icon'>💬</div>
            <div class='feature-title'>Chat Interface</div>
            <div class='feature-desc'>Natural conversation with source citations</div>
        </div>
        <div class='feature-card'>
            <div class='feature-icon'>💡</div>
            <div class='feature-title'>Extract Insights</div>
            <div class='feature-desc'>Generate summaries and key findings</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------
# Chat Interface
# ---------------------------------------------------
def render_chat():
    st.markdown("""
    <div class='brand-header'>
        <div class='brand-logo'>📊</div>
        <div class='brand-title'>InsightDocs AI</div>
        <div class='brand-subtitle'>Ask intelligent questions about your documents</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Actions
    if st.session_state.documents and not st.session_state.show_welcome:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📋 Summarize", use_container_width=True):
                generate_summary()
        
        with col2:
            if st.button("💡 Insights", use_container_width=True):
                generate_insights()
        
        with col3:
            if st.button("❓ Examples", use_container_width=True):
                show_examples()
        
        with col4:
            if st.button("📊 Stats", use_container_width=True):
                show_stats()
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Chat History
    if st.session_state.show_welcome or not st.session_state.chat_history:
        render_welcome()
    else:
        for msg in st.session_state.chat_history:
            avatar = "👤" if msg["role"] == "user" else "🤖"
            
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
                
                if msg.get("confidence"):
                    render_confidence(msg["confidence"])
                
                if msg.get("sources"):
                    render_sources(msg["sources"])
    
    # Chat Input
    if question := st.chat_input("💬 Ask a question about your documents..."):
        if not st.session_state.documents:
            st.warning("⚠️ Please upload documents first!")
        else:
            st.session_state.show_welcome = False
            handle_question(question)


# ---------------------------------------------------
# Question Handling (Streaming)
# ---------------------------------------------------
def handle_question(question):
    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)
    
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Stream response
        for chunk in st.session_state.rag_chain.stream_answer(
            question,
            st.session_state.chat_history[:-1]
        ):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        
        # Get sources and confidence
        _, sources, confidence = st.session_state.rag_chain.get_answer(
            question,
            st.session_state.chat_history[:-1]
        )
        
        render_confidence(confidence)
        
        if sources:
            render_sources(sources)
    
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": full_response,
        "sources": sources,
        "confidence": confidence
    })
    
    st.session_state.total_queries += 1


# ---------------------------------------------------
# UI Components
# ---------------------------------------------------
def render_confidence(confidence):
    if confidence >= 80:
        badge_class = "confidence-high"
        label = "High Confidence"
    elif confidence >= 50:
        badge_class = "confidence-medium"
        label = "Medium Confidence"
    else:
        badge_class = "confidence-low"
        label = "Low Confidence"
    
    st.markdown(f"""
    <span class='confidence-badge {badge_class}'>
        {label}: {confidence:.0f}%
    </span>
    """, unsafe_allow_html=True)


def render_sources(sources):
    with st.expander("📚 View Sources"):
        for i, source in enumerate(sources[:3], 1):
            source_name = source["metadata"].get("source", "Unknown")
            page = source["metadata"].get("page", "")
            score = source.get("score", 0)
            
            page_info = f", Page {page}" if page else ""
            
            st.markdown(f"""
            <div class='source-card'>
                <div class='source-title'>Source {i}: {source_name}{page_info}</div>
                <div class='source-content'>{source['content'][:280]}...</div>
                <div class='source-meta'>Relevance Score: {score:.0%}</div>
            </div>
            """, unsafe_allow_html=True)


def generate_summary():
    source = st.session_state.documents[0]["name"]
    with st.spinner("📝 Generating comprehensive summary..."):
        summary = st.session_state.rag_chain.summarize_document(source)
    
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": summary
    })
    st.rerun()


def generate_insights():
    source = st.session_state.documents[0]["name"]
    with st.spinner("💡 Extracting key insights..."):
        insights = st.session_state.rag_chain.extract_key_insights(source)
    
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": insights
    })
    st.rerun()


def show_examples():
    examples = """### 💭 Example Questions

• What is the main topic or theme of this document?
• What are the key findings or conclusions?
• Are there any important dates, deadlines, or milestones?
• What recommendations or action items are mentioned?
• What data, statistics, or metrics are highlighted?
• Who are the main stakeholders or parties involved?
• What are the potential risks or challenges discussed?
• What are the next steps or future plans outlined?"""
    
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": examples
    })
    st.rerun()


def show_stats():
    total_chunks = sum(d['chunks'] for d in st.session_state.documents)
    avg_chunks = total_chunks // len(st.session_state.documents) if st.session_state.documents else 0
    
    stats = f"""### 📊 Usage Statistics

**Total Documents:** {len(st.session_state.documents)}  
**Total Chunks:** {total_chunks}  
**Total Queries:** {st.session_state.total_queries}  
**Average Chunks per Document:** {avg_chunks}

Your documents have been processed and are ready for intelligent queries!"""
    
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": stats
    })
    st.rerun()


# ---------------------------------------------------
# Main
# ---------------------------------------------------
def main():
    init_session()
    initialize()
    render_sidebar()
    render_chat()


if __name__ == "__main__":
    main()