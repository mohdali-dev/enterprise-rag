import fitz
import pdfplumber
from docx import Document
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict


class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def process_file(self, uploaded_file) -> List[Dict]:
        """Process uploaded file and return chunks with metadata"""
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
            return []
    
    def _process_pdf(self, file) -> List[Dict]:
        chunks = []
        try:
            with pdfplumber.open(file) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text and text.strip():
                        page_chunks = self.text_splitter.split_text(text)
                        for chunk in page_chunks:
                            chunks.append({
                                "content": chunk,
                                "metadata": {
                                    "source": file.name,
                                    "page": page_num,
                                    "type": "pdf"
                                }
                            })
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
        
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
            print(f"Error processing DOCX: {str(e)}")
        
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
            print(f"Error processing TXT: {str(e)}")
        
        return chunks
    
    def _process_csv(self, file) -> List[Dict]:
        chunks = []
        try:
            df = pd.read_csv(file)
            for i, row in df.iterrows():
                row_text = " | ".join([f"{col}: {val}" for col, val in row.items()])
                chunks.append({
                    "content": row_text,
                    "metadata": {
                        "source": file.name,
                        "row": i,
                        "type": "csv"
                    }
                })
        except Exception as e:
            print(f"Error processing CSV: {str(e)}")
        
        return chunks