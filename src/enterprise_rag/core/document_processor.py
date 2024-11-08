import fitz  # PyMuPDF
from typing import List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info("DocumentProcessor initialized")

    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process PDF document and return chunks"""
        try:
            logger.info(f"Processing document: {file_path}")
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise Exception(f"File not found: {file_path}")
                
            if not file_path.suffix.lower() == '.pdf':
                raise Exception(f"Unsupported file format: {file_path.suffix}")
            
            # Extract text from PDF
            text = self._extract_pdf_text(file_path)
            logger.info(f"Extracted {len(text)} characters from PDF")
            
            # Create chunks
            chunks = self._create_chunks(text, str(file_path))
            logger.info(f"Created {len(chunks)} chunks")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise

    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with fitz.open(str(file_path)) as doc:
                for page_num, page in enumerate(doc):
                    text += page.get_text() + "\n\n"
                    logger.info(f"Processed page {page_num + 1}/{len(doc)}")
            return text
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise

    def _create_chunks(self, text: str, source_path: str) -> List[Dict[str, Any]]:
        """Split text into chunks with overlap"""
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(paragraph) > self.chunk_size:
                if current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "metadata": {
                            "source": source_path,
                            "chunk_id": chunk_id,
                            "char_count": len(current_chunk)
                        }
                    })
                    chunk_id += 1
                    # Keep overlap for next chunk
                    current_chunk = current_chunk[-self.chunk_overlap:] if self.chunk_overlap > 0 else ""
                
            current_chunk += "\n" + paragraph if current_chunk else paragraph
        
        # Add the last chunk
        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": {
                    "source": source_path,
                    "chunk_id": chunk_id,
                    "char_count": len(current_chunk)
                }
            })
        
        return chunks