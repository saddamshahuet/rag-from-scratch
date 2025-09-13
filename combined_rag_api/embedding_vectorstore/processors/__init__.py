"""
Document Processors Package.
This package contains processors for various document formats.
"""
from embedding_vectorstore.processors.pdf_processor import PDFProcessor
from embedding_vectorstore.processors.docx_processor import DocxProcessor
from embedding_vectorstore.processors.text_processor import TextProcessor
from embedding_vectorstore.processors.html_processor import HtmlProcessor
from embedding_vectorstore.processors.excel_processor import ExcelProcessor

# Create a list of available processors
available_processors = [
    PDFProcessor(),
    DocxProcessor(),
    TextProcessor(),
    HtmlProcessor(),
    ExcelProcessor(),
]