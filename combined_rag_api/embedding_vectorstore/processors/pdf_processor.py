"""
PDF Document Processor Implementation.
"""
from typing import List, Dict, Any, Optional
import logging
import re

# Import PyPDF2 for PDF processing
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

from embedding_vectorstore.document_processor import DocumentProcessor, TextChunker

logger = logging.getLogger(__name__)

class PDFProcessor(DocumentProcessor):
    """PDF document processor"""
    
    def __init__(self):
        if PyPDF2 is None:
            logger.warning("PyPDF2 is not installed. PDF processing will not be available.")
    
    def supports_format(self, file_extension: str) -> bool:
        """Check if processor supports given file extension"""
        return file_extension.lower() in ['.pdf'] and PyPDF2 is not None
    
    async def process(self, file_path: str, metadata: Optional[Dict[str, Any]] = None, 
                    chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Process PDF document and return list of text chunks"""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 is required for PDF processing")
            
        # Extract text
        text = await self._extract_text(file_path)
        
        # Clean text
        text = self._clean_text(text)
        
        # Chunk text
        chunker = TextChunker()
        chunks = chunker.chunk(text, chunk_size, chunk_overlap)
        
        return chunks
    
    async def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common PDF extraction issues
        text = text.replace('- ', '')
        
        return text.strip()