<p align="center">
  <h1 align="center">🧠 DocuMind AI</h1>
  <p align="center">
    <strong>Enterprise-Grade Document Intelligence Platform</strong><br>
    <em>Transform static documents into interactive, context-grounded AI conversations using RAG.</em>
  </p>
  <p align="center">
    <a href="https://www.python.org/downloads/">
      <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    </a>
    <a href="https://streamlit.io/">
      <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
    </a>
    <a href="https://www.langchain.com/">
      <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain">
    </a>
    <a href="https://groq.com/">
      <img src="https://img.shields.io/badge/Groq-EE3124?style=for-the-badge&logo=groq&logoColor=white" alt="Groq">
    </a>
    <a href="https://github.com/mohdali-dev/DocuMind-AI/blob/main/LICENSE">
      <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
    </a>
  </p>
</p>

---

### 🌟 Overview
**DocuMind AI** is a production-ready Retrieval-Augmented Generation (RAG) application. It ingests complex documents, embeds them into a local vector database, and uses high-throughput LLM inference to answer questions with **zero hallucinations** and **traceable citations**.

### ✨ Key Features

| 📤 Smart Ingestion | 💬 Context-Grounded Q&A | 🎨 Professional UI/UX | ⚡ High Performance |
| :--- | :--- | :--- | :--- |
| Parses **PDF, DOCX, TXT, CSV** with intelligent semantic chunking. | Strictly answers based on uploaded docs to **eliminate hallucinations**. | Beautiful **Dark/Light mode**, responsive design, and smooth animations. | **Sub-second latency** powered by Groq's ultra-fast inference engine. |
| Preserves metadata (page numbers) and supports batch processing. | Every response includes **exact source citations** and page numbers. | Real-time token streaming and visual typing indicators. | **Privacy-first** local vector storage using ChromaDB. |

---

### 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│           (Chat Interface, Document Upload, UI)          │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Document Processor                      │
│           (PDF/DOCX parsing & semantic chunking)         │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Vector Embeddings Layer                     │
│         (HuggingFace Sentence Transformers - Local)      │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                 Vector Database                          │
│         (ChromaDB - Local storage, Cosine Similarity)    │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│               RAG Chain (LangChain)                      │
│          (Context Retrieval + Prompt Engineering)        │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Groq LLM API                            │
│           (Llama 3.3 - Fast inference & streaming)       │
└─────────────────────────────────────────────────────────┘
```

### 🛠️ Technology Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **LLM Engine** | Groq (Llama 3.3-70B) | Ultra-fast, low-latency text generation (~0.3s). |
| **Orchestration** | LangChain | Robust RAG pipeline, state management, and prompting. |
| **Vector Database** | ChromaDB | Local, persistent, and fast vector storage. |
| **Embeddings** | HuggingFace (`all-MiniLM-L6-v2`) | High-quality, lightweight local semantic embeddings. |
| **Frontend** | Streamlit | Interactive, production-ready web interface. |

---

### 📊 Performance Metrics

| Metric | Performance | Notes |
| :--- | :--- | :--- |
| **Inference Latency** | `~500ms` | Powered by Groq API |
| **Document Processing** | `~2-3s / 10MB` | Local parsing & chunking |
| **Vector Search** | `~50ms` | ChromaDB cosine similarity |
| **Total E2E Latency** | `~1-2s` | Complete RAG cycle |

---

### 🚀 Quick Start

Get the application running locally in minutes:

```bash
# 1. Clone the repository
git clone https://github.com/mohdali-dev/DocuMind-AI.git
cd DocuMind-AI

# 2. Set up a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Open .env and add your Groq API key: GROQ_API_KEY=your_key_here

# 4. Launch the application
streamlit run app.py
```
*The app will open automatically at `http://localhost:8501`.*

---

### 💻 Usage Guide

1. **Upload Documents:** Click "Upload Documents" in the sidebar. Select files (PDF, DOCX, TXT, CSV) and click "Process".
2. **Ask Questions:** Type natural language queries in the chat input. The AI will respond with context-grounded answers.
3. **View Sources:** Click "View Sources" below any answer to see exact quotes, page numbers, and relevance scores.
4. **Generate Insights:** Use the sidebar quick actions to auto-generate executive summaries or extract key findings.

---

### 📂 Project Structure

```text
DocuMind-AI/
├── app.py                      # Main Streamlit UI, routing, and session state
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .streamlit/
│   └── config.toml             # Streamlit configuration and theming
└── src/                        # Core backend modules
    ├── document_processor.py   # File parsing, cleaning, and text chunking
    ├── vector_store.py         # ChromaDB operations and embedding management
    └── rag_chain.py            # LangChain RAG pipeline and LLM integration
```

<details>
<summary><b>📄 View Detailed File Descriptions</b></summary>
<br>

*   **`app.py` (500+ lines):** Handles the Streamlit UI, custom CSS styling (light/dark modes), sidebar document management, chat interface rendering, and session state.
*   **`src/document_processor.py` (200+ lines):** Routes files to specific parsers (`pdfplumber`, `python-docx`, etc.) and implements recursive character text splitting (1000 token size, 200 token overlap).
*   **`src/vector_store.py` (150+ lines):** Manages the ChromaDB lifecycle, including document insertion, similarity search with metadata filtering, and collection resets.
*   **`src/rag_chain.py` (300+ lines):** Constructs the LangChain RAG pipeline, formats context for the LLM, manages chat history, and handles streaming responses and summarization.

</details>

---

### 🌐 Deployment

#### Option 1: Streamlit Cloud (Recommended)
1. Push your code to a GitHub repository.
2. Navigate to [share.streamlit.io](https://share.streamlit.io) and create a new app.
3. Link your repository, set the branch to `main`, and the main file to `app.py`.
4. Add your `GROQ_API_KEY` in the app's "Secrets" settings before deploying.

<details>
<summary><b>🐳 Option 2: Docker (Self-Hosted)</b></summary>
<br>

Create a `Dockerfile` in the root directory:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
**Build and Run:**
```bash
docker build -t docmind-ai .
docker run -p 8501:8501 -e GROQ_API_KEY=your_key docmind-ai
```

</details>

---

### 🔒 Security & Privacy

*   **Local Processing:** Document parsing and vector embeddings are processed locally. Only the final text queries are sent to the Groq API.
*   **Data Isolation:** Vector embeddings are stored locally in ChromaDB. No document content is permanently stored on external servers.
*   **Secret Management:** API keys are managed via `.env` files locally and Streamlit Secrets in production. Ensure `.env` is strictly included in `.gitignore`.

---

### 🛣️ Roadmap

- [x] **v1.0:** Initial release with PDF/DOCX/TXT/CSV support, RAG Q&A, and Dark/Light mode.
- [ ] **v1.1:** Multi-user support with authentication and chat history export (PDF/JSON).
- [ ] **v1.5:** Pinecone/Milvus integration for scalable cloud vector storage.
- [ ] **v2.0:** Fine-tuned domain-specific models and advanced analytics dashboard.

---

### 🤝 Contributing

Contributions are what make the open-source community amazing. We welcome pull requests!

1. Fork the Project (`git clone https://github.com/mohdali-dev/DocuMind-AI.git`)
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

*Please ensure your code is formatted using `black` and passes `flake8` linting.*

---

### 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
  <h3>👨‍💻 Developed by Muhammad Ali</h3>
  <p><em>AI/ML Engineer & Software Developer</em></p>
  
  <a href="https://mohdali.me">
    <img src="https://img.shields.io/badge/Website-mohdali.me-4285F4?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Website">
  </a>
  <a href="https://github.com/mohdali-dev">
    <img src="https://img.shields.io/badge/GitHub-mohdali--dev-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
  </a>
  <a href="https://huggingface.co/mohdali1">
    <img src="https://img.shields.io/badge/HuggingFace-mohdali1-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" alt="HuggingFace">
  </a>
  <a href="https://linkedin.com/in/mohdali1">
    <img src="https://img.shields.io/badge/LinkedIn-Muhammad%20Ali-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn">
  </a>
  <a href="mailto:aliskdse@gmail.com">
    <img src="https://img.shields.io/badge/Email-aliskdse@gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email">
  </a>
  <a href="https://orcid.org/0009-0005-3272-4489">
    <img src="https://img.shields.io/badge/ORCID-0009--0005--3272--4489-A6CE39?style=for-the-badge&logo=orcid&logoColor=white" alt="ORCID">
  </a>
</div>
