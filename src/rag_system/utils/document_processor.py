import os
import sys
from typing import List, Dict, Any
from pathlib import Path
import pypdf
from docx import Document
from bs4 import BeautifulSoup

# Try to import win32com for .doc support on Windows
try:
    import win32com.client
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

class DocumentProcessor:
    @staticmethod
    def read_text_file(file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    @staticmethod
    def read_pdf_file(file_path: str) -> str:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    @staticmethod
    def read_docx_file(file_path: str) -> str:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()

    @staticmethod
    def read_doc_file(file_path: str) -> str:
        # For old .doc files on Windows, use win32com to extract text
        if HAS_WIN32COM and sys.platform == 'win32':
            try:
                word = win32com.client.Dispatch("Word.Application")
                word.Visible = False
                doc = word.Documents.Open(os.path.abspath(file_path))
                text = doc.Content.Text
                doc.Close()
                word.Quit()
                return text.strip()
            except Exception as e:
                # If COM fails, try python-docx as fallback
                try:
                    return DocumentProcessor.read_docx_file(file_path)
                except:
                    raise ValueError(
                        f"Could not read .doc file using Word COM or python-docx: {str(e)}. "
                        "Please convert to .docx, .pdf, or .txt."
                    )
        else:
            # Try python-docx as fallback (sometimes works)
            try:
                return DocumentProcessor.read_docx_file(file_path)
            except Exception:
                raise ValueError(
                    "Old .doc format not fully supported on this platform. "
                    "Please convert to .docx, .pdf, or .txt. "
                    "You can use LibreOffice or MS Word to convert the file."
                )
    
    @staticmethod
    def read_html_file(file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            return soup.get_text(strip=True)
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        file_path = Path(file_path)
        file_extension = file_path.suffix.lower()

        try:
            if file_extension == '.txt':
                content = self.read_text_file(str(file_path))
            elif file_extension == '.pdf':
                content = self.read_pdf_file(str(file_path))
            elif file_extension in ['.docx', '.doc']:
                if file_extension == '.doc':
                    content = self.read_doc_file(str(file_path))
                else:
                    content = self.read_docx_file(str(file_path))
            elif file_extension in ['.html', '.htm']:
                content = self.read_html_file(str(file_path))
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")

            return {
                'content': content,
                'metadata': {
                    'source': str(file_path),
                    'file_type': file_extension,
                    'file_name': file_path.name
                }
            }
        except Exception as e:
            raise Exception(f"Error processing file {file_path}: {str(e)}")
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to end at a sentence boundary
            chunk = text[start:end]
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            
            if last_period > len(chunk) * 0.8:
                end = start + last_period + 1
            elif last_newline > len(chunk) * 0.8:
                end = start + last_newline + 1
            
            chunks.append(text[start:end])
            start = end - overlap
        
        return chunks
    
    def process_directory(self, directory_path: str, chunk_size: int = 1000) -> List[Dict[str, Any]]:
        directory_path = Path(directory_path)
        documents = []

        supported_extensions = {'.txt', '.pdf', '.docx', '.doc', '.html', '.htm'}

        for file_path in directory_path.rglob('*'):
            if file_path.suffix.lower() in supported_extensions:
                try:
                    doc_data = self.process_file(str(file_path))
                    chunks = self.chunk_text(doc_data['content'], chunk_size)
                    
                    for i, chunk in enumerate(chunks):
                        chunk_metadata = doc_data['metadata'].copy()
                        chunk_metadata['chunk_id'] = i
                        chunk_metadata['total_chunks'] = len(chunks)
                        
                        documents.append({
                            'content': chunk,
                            'metadata': chunk_metadata
                        })
                except Exception as e:
                    print(f"Warning: Failed to process {file_path}: {str(e)}")
                    continue
        
        return documents