import fitz  # PyMuPDF
from docx import Document
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict
import logging

class DocumentProcessor:
    def __init__(self):
        # 1000 characters with a 200 overlap is the sweet spot for Llama 3
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def process_file(self, uploaded_file) -> List[Dict]:
        """Process an uploaded file and return chunks with metadata."""
        file_extension = uploaded_file.name.split(".")[-1].lower()
        
        if file_extension == "pdf":
            return self._process_pdf(uploaded_file)
        elif file_extension == "docx":
            return self._process_docx(uploaded_file)
        elif file_extension == "txt":
            return self._process_txt(uploaded_file)
        elif file_extension == "csv":
            return self._process_csv(uploaded_file)
        else:
            logging.warning(f"Unsupported file type uploaded: {file_extension}")
            return []
    
    def _process_pdf(self, file) -> List[Dict]:
        chunks = []
        try:
            # Streamlit UploadedFiles are byte streams. PyMuPDF handles this beautifully.
            file_bytes = file.read()
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            
            # FIX: Accumulate ALL text first to prevent the Page-Break Trap.
            # We inject page markers so the LLM can still cite page numbers accurately.
            full_text = ""
            for page_num in range(len(doc)):
                page_text = doc[page_num].get_text("text")
                if page_text.strip():
                    full_text += f"\n\n[START OF PAGE {page_num + 1}]\n" + page_text
            
            # Now we split the unified text. Overlaps will safely cross page boundaries.
            text_chunks = self.text_splitter.split_text(full_text)
            
            for i, chunk in enumerate(text_chunks):
                chunks.append({
                    "content": chunk,
                    "metadata": {
                        "source": file.name,
                        "chunk_index": i,
                        "type": "pdf"
                    }
                })
                
            doc.close()
        except Exception as e:
            logging.error(f"Error processing PDF {file.name}: {str(e)}")
            
        return chunks
    
    def _process_docx(self, file) -> List[Dict]:
        chunks = []
        try:
            doc = Document(file)
            full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            text_chunks = self.text_splitter.split_text(full_text)
            
            for i, chunk in enumerate(text_chunks):
                chunks.append({
                    "content": chunk,
                    "metadata": {
                        "source": file.name,
                        "chunk_index": i,
                        "type": "docx"
                    }
                })
        except Exception as e:
            logging.error(f"Error processing DOCX {file.name}: {str(e)}")
            
        return chunks
    
    def _process_txt(self, file) -> List[Dict]:
        chunks = []
        try:
            text = file.read().decode("utf-8")
            text_chunks = self.text_splitter.split_text(text)
            
            for i, chunk in enumerate(text_chunks):
                chunks.append({
                    "content": chunk,
                    "metadata": {
                        "source": file.name,
                        "chunk_index": i,
                        "type": "txt"
                    }
                })
        except Exception as e:
            logging.error(f"Error processing TXT {file.name}: {str(e)}")
            
        return chunks
    
    def _process_csv(self, file) -> List[Dict]:
        chunks = []
        try:
            df = pd.read_csv(file)
            
            # FIX: Convert the entire DataFrame into a Markdown table format.
            # This prevents ChromaDB from exploding with thousands of single-row vectors
            # and allows the LLM to understand the relational structure of the data.
            md_text = df.to_markdown(index=False)
            text_chunks = self.text_splitter.split_text(md_text)
            
            for i, chunk in enumerate(text_chunks):
                chunks.append({
                    "content": chunk,
                    "metadata": {
                        "source": file.name,
                        "chunk_index": i,
                        "type": "csv"
                    }
                })
        except Exception as e:
            logging.error(f"Error processing CSV {file.name}: {str(e)}")
            
        return chunks