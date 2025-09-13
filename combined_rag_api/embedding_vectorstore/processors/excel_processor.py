"""
Excel Document Processor Implementation.
"""
from typing import List, Dict, Any, Optional
import logging
import re
import os

# Import pandas and openpyxl for Excel processing
try:
    import pandas as pd
except ImportError:
    pd = None

from embedding_vectorstore.document_processor import DocumentProcessor, TextChunker

logger = logging.getLogger(__name__)

class ExcelProcessor(DocumentProcessor):
    """Excel document processor for XLS and XLSX files"""
    
    def __init__(self):
        if pd is None:
            logger.warning("pandas is not installed. Excel processing will not be available.")
    
    def supports_format(self, file_extension: str) -> bool:
        """Check if processor supports given file extension"""
        return file_extension.lower() in ['.xlsx', '.xls'] and pd is not None
    
    async def process(self, file_path: str, metadata: Optional[Dict[str, Any]] = None, 
                    chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Process Excel document and return list of text chunks"""
        if pd is None:
            raise ImportError("pandas is required for Excel processing")
            
        # Extract text
        text = await self._extract_text(file_path)
        
        # Extract metadata if not provided
        if metadata is None:
            metadata = {}
        excel_metadata = await self._extract_metadata(file_path)
        metadata.update(excel_metadata)
        
        # Clean text
        text = self._clean_text(text)
        
        # Chunk text
        chunker = TextChunker()
        chunks = chunker.chunk(text, chunk_size, chunk_overlap)
        
        return chunks
    
    async def _extract_text(self, file_path: str) -> str:
        """Extract text from Excel file"""
        try:
            # Get list of sheet names
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            all_sheets_text = []
            
            # Process each sheet
            for sheet_name in sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Convert DataFrame to markdown table
                markdown_table = f"## Sheet: {sheet_name}\n\n"
                markdown_table += df.to_markdown(index=False)
                markdown_table += "\n\n"
                
                all_sheets_text.append(markdown_table)
            
            return "\n".join(all_sheets_text)
            
        except Exception as e:
            logger.error(f"Error extracting text from Excel file: {str(e)}")
            raise
    
    async def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from Excel file"""
        metadata = {}
        
        try:
            # Get sheet names
            excel_file = pd.ExcelFile(file_path)
            metadata['sheet_names'] = excel_file.sheet_names
            metadata['sheet_count'] = len(excel_file.sheet_names)
            
            # Add file info
            file_stat = os.stat(file_path)
            metadata.update({
                'file_size': file_stat.st_size,
                'modified_time': file_stat.st_mtime,
                'created_time': file_stat.st_ctime
            })
            
        except Exception as e:
            logger.error(f"Error extracting metadata from Excel file: {str(e)}")
        
        return metadata
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()