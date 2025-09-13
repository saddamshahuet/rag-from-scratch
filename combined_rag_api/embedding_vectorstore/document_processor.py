"""
Document Processing Module.
This module provides functionality for processing various document formats.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
import re
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor(ABC):
    """Base abstract class for document processors"""
    
    @abstractmethod
    async def process(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """Process document and return list of text chunks"""
        pass
    
    @abstractmethod
    def supports_format(self, file_extension: str) -> bool:
        """Check if processor supports given file extension"""
        pass


class ProcessorFactory:
    """Factory for creating document processors"""
    
    def __init__(self):
        self.processors = []
    
    def register_processor(self, processor: DocumentProcessor):
        """Register a document processor"""
        self.processors.append(processor)
    
    def get_processor(self, file_path: str) -> Optional[DocumentProcessor]:
        """Get appropriate processor for file"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        for processor in self.processors:
            if processor.supports_format(file_extension):
                return processor
        
        return None


class TextChunker:
    """Split text into chunks for embedding"""
    
    def chunk(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []
        
        # Try to split on paragraph boundaries first
        paragraphs = self._split_paragraphs(text)
        
        # If paragraphs are too long, split them further
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size, store current chunk and start new
            if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Keep overlap from previous chunk
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + paragraph
            else:
                current_chunk += paragraph
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If any chunks are still too large, split them by sentences
        result = []
        for chunk in chunks:
            if len(chunk) <= chunk_size:
                result.append(chunk)
            else:
                result.extend(self._split_by_size(chunk, chunk_size, overlap))
        
        return result
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', text)
        # Ensure each paragraph ends with newline for joining
        return [p.strip() + '\n\n' for p in paragraphs if p.strip()]
    
    def _split_by_size(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text by size with overlap"""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            
            # If we're at the end, just take the rest
            if end >= text_len:
                chunks.append(text[start:])
                break
            
            # Try to find a sentence boundary
            boundary = text.rfind('.', start, end)
            if boundary != -1 and boundary > start:
                end = boundary + 1
            
            # Add chunk
            chunks.append(text[start:end].strip())
            
            # Move start position, accounting for overlap
            start = end - overlap
        
        return chunks