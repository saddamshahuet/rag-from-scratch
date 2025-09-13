"""
Text and Markdown Document Processor Implementation.
"""
from typing import List, Dict, Any, Optional
import logging
import re
import os

from embedding_vectorstore.document_processor import DocumentProcessor, TextChunker

logger = logging.getLogger(__name__)

class TextProcessor(DocumentProcessor):
    """Text and Markdown document processor"""
    
    def supports_format(self, file_extension: str) -> bool:
        """Check if processor supports given file extension"""
        return file_extension.lower() in ['.txt', '.md', '.markdown']
    
    async def process(self, file_path: str, metadata: Optional[Dict[str, Any]] = None, 
                    chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Process text document and return list of text chunks"""
        # Extract text
        text = await self._extract_text(file_path)
        
        # Extract basic metadata
        if metadata is None:
            metadata = {}
        file_stat = os.stat(file_path)
        metadata.update({
            'file_size': file_stat.st_size,
            'modified_time': file_stat.st_mtime,
            'created_time': file_stat.st_ctime
        })
        
        # Clean text
        text = self._clean_text(text)
        
        # Chunk text
        chunker = TextChunker()
        chunks = chunker.chunk(text, chunk_size, chunk_overlap)
        
        return chunks
    
    async def _extract_text(self, file_path: str) -> str:
        """Extract text from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encodings if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Error reading text file with latin-1 encoding: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error reading text file: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove carriage returns
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        
        # Normalize whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()