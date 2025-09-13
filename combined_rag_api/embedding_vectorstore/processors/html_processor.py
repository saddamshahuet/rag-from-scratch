"""
HTML Document Processor Implementation.
"""
from typing import List, Dict, Any, Optional
import logging
import re
import os

# Import BeautifulSoup for HTML processing
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from embedding_vectorstore.document_processor import DocumentProcessor, TextChunker

logger = logging.getLogger(__name__)

class HtmlProcessor(DocumentProcessor):
    """HTML document processor"""
    
    def __init__(self):
        if BeautifulSoup is None:
            logger.warning("BeautifulSoup is not installed. HTML processing will not be available.")
    
    def supports_format(self, file_extension: str) -> bool:
        """Check if processor supports given file extension"""
        return file_extension.lower() in ['.html', '.htm'] and BeautifulSoup is not None
    
    async def process(self, file_path: str, metadata: Optional[Dict[str, Any]] = None, 
                    chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Process HTML document and return list of text chunks"""
        if BeautifulSoup is None:
            raise ImportError("BeautifulSoup is required for HTML processing")
            
        # Extract text
        text = await self._extract_text(file_path)
        
        # Extract metadata if not provided
        if metadata is None:
            metadata = {}
        html_metadata = await self._extract_metadata(file_path)
        metadata.update(html_metadata)
        
        # Clean text
        text = self._clean_text(text)
        
        # Chunk text
        chunker = TextChunker()
        chunks = chunker.chunk(text, chunk_size, chunk_overlap)
        
        return chunks
    
    async def _extract_text(self, file_path: str) -> str:
        """Extract text from HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
        except UnicodeDecodeError:
            # Try with different encodings if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    html_content = file.read()
            except Exception as e:
                logger.error(f"Error reading HTML file with latin-1 encoding: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error reading HTML file: {str(e)}")
            raise
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator='\n')
        
        # Clean text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    async def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from HTML file"""
        metadata = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as file:
                html_content = file.read()
                
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.string
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            if meta.get('name'):
                metadata[meta.get('name')] = meta.get('content')
            elif meta.get('property'):
                metadata[meta.get('property')] = meta.get('content')
        
        # Add file info
        file_stat = os.stat(file_path)
        metadata.update({
            'file_size': file_stat.st_size,
            'modified_time': file_stat.st_mtime,
            'created_time': file_stat.st_ctime
        })
        
        return metadata
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()