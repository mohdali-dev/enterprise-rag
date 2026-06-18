import streamlit as st
from dotenv import load_dotenv
import os
from datetime import datetime

from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.rag_chain import RAGChain

load_dotenv()

# Page config
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
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

def render_sidebar():
    with st.sidebar:
        st.markdown("## 📁 Document Manager")
        st.markdown("---")
        
        uploaded_files = st.file_uploader(
            "Upload Documents",
            type=["pdf", "docx", "txt", "csv"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("🚀 Process Documents", type="primary", use_container_width=True):
                process_documents(uploaded_files)
        
        if st.session_state.documents_processed:
            st.markdown("---")
            st.markdown("### 📚 Loaded Documents")
            
            for doc in st.session_state.documents_processed:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"📄 {doc['name'][:20]}...")
                with col2:
                    if st.button("🗑️", key=f"del_{doc['name']}"):
                        delete_document(doc['name'])
        
        st.markdown("---")
        
        filter_doc = st.selectbox(
            "Filter by Document",
            options=["All Documents"] + [d['name'] for d in st.session_state.documents_processed]
        )
        
        if st.button("🔄 Clear All", use_container_width=True):
            reset_app()
        
        return filter_doc

def process_documents(uploaded_files):
    new_files = [
        f for f in uploaded_files
        if f.name not in [d['name'] for d in st.session_state.documents_processed]
    ]
    
    if not new_files:
        st.sidebar.warning("Documents already processed!")
        return
    
    progress_bar = st.sidebar.progress(0)
    status = st.sidebar.empty()
    
    for i, file in enumerate(new_files):
        status.text(f"Processing {file.name}...")
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
    
    status.text("✅ Processing complete!")
    st.balloons()

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
    with st.expander("📚 View Sources"):
        for i, source in enumerate(sources[:3], 1):
            source_name = source["metadata"].get("source", "Unknown")
            page = source["metadata"].get("page", "")
            score = source.get("score", 0)
            
            page_info = f" | Page {page}" if page else ""
            
            st.markdown(f"""
**Source {i}:** {source_name}{page_info}  
Relevance: {score:.0%}  
_{source['content'][:150]}..._
""")

def handle_question(question: str, filter_doc: str):
    st.session_state.chat_history.append({"role": "user", "content": question})
    
    with st.chat_message("user"):
        st.markdown(question)
    
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
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

def render_chat(filter_doc: str):
    st.markdown("# 🧠 DocuMind AI")
    st.markdown("_Chat with your documents intelligently_")
    
    if st.session_state.documents_processed:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📋 Summarize", use_container_width=True):
                source = filter_doc if filter_doc != "All Documents" else st.session_state.documents_processed[0]["name"]
                with st.spinner("📝 Generating summary..."):
                    summary = st.session_state.rag_chain.summarize_document(source)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"**📋 Summary:**\n\n{summary}",
                    "sources": []
                })
                st.rerun()
        
        with col2:
            if st.button("💡 Key Insights", use_container_width=True):
                source = filter_doc if filter_doc != "All Documents" else st.session_state.documents_processed[0]["name"]
                with st.spinner("💡 Extracting insights..."):
                    insights = st.session_state.rag_chain.extract_key_insights(source)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"**💡 Key Insights:**\n\n{insights}",
                    "sources": []
                })
                st.rerun()
        
        with col3:
            if st.button("❓ Sample Q", use_container_width=True):
                sample = "**Sample Questions:**\n• What is the main topic?\n• What are key findings?\n• Are there important dates?"
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": sample,
                    "sources": []
                })
                st.rerun()
        
        with col4:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
    
    st.markdown("---")
    
    if not st.session_state.chat_history:
        st.info("👋 Upload documents using the sidebar to get started!")
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            if message["role"] == "assistant" and "sources" in message and message["sources"]:
                render_sources(message["sources"])
    
    if question := st.chat_input(
        "Ask anything about your documents...",
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