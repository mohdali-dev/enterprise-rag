# DocuMind AI

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)


---

## Core Capabilities

*   **Multi-Format Ingestion:** Parses and processes PDF, DOCX, TXT, and CSV files using intelligent text chunking with boundary awareness and metadata preservation.
*   **Context-Grounded Q&A:** Answers natural language queries using a RAG pipeline that strictly grounds responses in the provided context to mitigate hallucinations.
*   **Traceable Citations:** Provides precise source tracking, including document names and page numbers, for every generated response.
*   **Automated Summarization:** Generates executive summaries and extracts key insights from large document corpora.
*   **Privacy-First Design:** Employs local vector storage (ChromaDB) and local embedding models to ensure sensitive document data remains on-premises.
*   **High-Throughput Inference:** Utilizes Groq's inference engine to deliver sub-second response times and real-time token streaming.

---

## System Architecture

```text
+---------------------------------------------------------+
|                   Streamlit Frontend                    |
|      (Chat Interface, Document Management, UI/UX)       |
+-----------------------------+---------------------------+
                              |
+-----------------------------v---------------------------+
|                Document Processor                       |
|      (Parsing, Cleaning, and Semantic Chunking)         |
+-----------------------------+---------------------------+
                              |
+-----------------------------v---------------------------+
|             Vector Embeddings Layer                     |
|       (HuggingFace Sentence Transformers - Local)       |
+-----------------------------+---------------------------+
                              |
+-----------------------------v---------------------------+
|                  Vector Database                        |
|        (ChromaDB - Local storage, Cosine Similarity)    |
+-----------------------------+---------------------------+
                              |
+-----------------------------v---------------------------+
|                 RAG Pipeline (LangChain)                |
|        (Context Retrieval, Prompt Engineering)          |
+-----------------------------+---------------------------+
                              |
+-----------------------------v---------------------------+
|                    Groq LLM API                         |
|          (Llama 3 - Fast Inference & Streaming)         |
+---------------------------------------------------------+
```

### Technology Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **LLM Provider** | Groq (Llama 3.3-70B) | High-throughput, low-latency inference. |
| **Embeddings** | HuggingFace (`all-MiniLM-L6-v2`) | High-quality semantic representations, runs locally. |
| **Vector Database** | ChromaDB | Lightweight, persistent, local vector storage. |
| **Orchestration** | LangChain | Robust framework for RAG pipeline and state management. |
| **Frontend** | Streamlit | Rapid development of interactive, data-driven web apps. |

---

## Performance Metrics

*   **Inference Latency:** ~500ms (via Groq API)
*   **Document Processing:** ~2-3 seconds per 10MB
*   **Vector Search:** ~50ms (ChromaDB)
*   **End-to-End Latency:** ~1-2 seconds for complete RAG cycle

---

## Getting Started

### Prerequisites

*   Python 3.10 or higher
*   Groq API Key (Obtain from [console.groq.com](https://console.groq.com))
*   Git
*   Approximately 2GB of disk space for embedding models

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/mohd-ali10/documind-ai.git
    cd documind-ai
    ```

2.  **Set up a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    Create a `.env` file in the root directory and add your Groq API key:
    ```env
    GROQ_API_KEY=gsk_your_actual_key_here
    ```

5.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
    The application will be accessible at `http://localhost:8501`.

---

## Project Structure

```text
documind-ai/
├── app.py                      # Main Streamlit application and UI logic
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .streamlit/
│   └── config.toml             # Streamlit configuration and theming
└── src/                        # Core application modules
    ├── __init__.py
    ├── document_processor.py   # File parsing, cleaning, and text chunking
    ├── vector_store.py         # ChromaDB operations and embedding management
    └── rag_chain.py            # RAG pipeline, prompt engineering, and LLM integration
```

### Module Overview

*   **`app.py`**: Handles the Streamlit UI, session state management, custom CSS styling, and user interactions.
*   **`src/document_processor.py`**: Routes files to specific parsers (pdfplumber, python-docx, etc.) and implements recursive character text splitting with configurable chunk size and overlap.
*   **`src/vector_store.py`**: Manages the ChromaDB lifecycle, including document insertion, similarity search, metadata filtering, and collection resets.
*   **`src/rag_chain.py`**: Constructs the LangChain RAG pipeline, formats context for the LLM, manages chat history, and handles streaming responses and summarization tasks.

---

## Configuration & Customization

### Environment Variables
*   `GROQ_API_KEY`: Required for LLM inference.
*   *(Optional)* `PINECONE_API_KEY`, `OPENAI_API_KEY`: Reserved for future integrations.

### Streamlit Configuration
Modify `.streamlit/config.toml` to adjust theming, server ports, and logging levels.

### Tuning RAG Parameters
You can adjust the chunking strategy and LLM parameters directly in the source code:
*   **Chunking:** Modify `chunk_size` and `chunk_overlap` in `src/document_processor.py`.
*   **LLM Parameters:** Adjust `temperature` and `model` in `src/rag_chain.py`.

---

## Deployment

### Streamlit Cloud (Recommended)
1.  Push your code to a GitHub repository.
2.  Navigate to [share.streamlit.io](https://share.streamlit.io) and create a new app.
3.  Link your repository, set the branch to `main`, and the main file to `app.py`.
4.  Add your `GROQ_API_KEY` in the app's "Secrets" settings before deploying.

### Docker
A `Dockerfile` is provided for containerized deployment:
```bash
docker build -t documind-ai .
docker run -p 8501:8501 -e GROQ_API_KEY=your_key documind-ai
```

---

## Security & Privacy Considerations

*   **Local Processing:** Document parsing and vector embeddings are processed locally. Only the final text queries are sent to the Groq API.
*   **Data Isolation:** Vector embeddings are stored locally in ChromaDB. No document content is permanently stored on external servers.
*   **Secret Management:** API keys are managed via `.env` files locally and Streamlit Secrets in production. Ensure `.env` is included in `.gitignore`.

---

## Roadmap

*   [ ] **Multi-Tenancy:** Role-based access control and user authentication.
*   [ ] **Advanced Analytics:** Dashboard for document processing metrics and query insights.
*   [ ] **Scalable Vector DB:** Integration with Pinecone or Milvus for distributed deployments.
*   [ ] **Export Capabilities:** Export chat history and summaries to PDF/JSON.
*   [ ] **API Endpoints:** Expose RAG capabilities via a FastAPI backend.

---

## Contributing

Contributions are welcome. Please follow these steps:
1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/YourFeature`).
3.  Commit your changes (`git commit -m 'Add some feature'`).
4.  Push to the branch (`git push origin feature/YourFeature`).
5.  Open a Pull Request.


---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

**Sikandar Ali**  
*AI Developer & Software Engineer*

*   **GitHub:** [github.com/mohd-ali10](https://github.com/mohd-ali10)
*   **LinkedIn:** [linkedin.com/in/mohdali1](https://linkedin.com/in/mohdali1)
*   **Email:** [aliskdse@gmail.com](mailto:aliskdse@gmail.com)
