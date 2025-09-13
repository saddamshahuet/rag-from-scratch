"""
Document Processing API Routes.
This module provides FastAPI routes for document processing.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import os
import tempfile
import uuid
import shutil
import json
import logging
from datetime import datetime

from embedding_vectorstore.document_processor import ProcessorFactory, TextChunker
from embedding_vectorstore.processors import available_processors
from embedding_vectorstore.url_extractor import URLContentExtractor

# Create router
router = APIRouter(prefix="/api/documents", tags=["documents"])

# Setup logging
logger = logging.getLogger(__name__)

# Initialize processor factory
processor_factory = ProcessorFactory()
for processor in available_processors:
    processor_factory.register_processor(processor)

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    vector_store_id: int = Form(...),
    embedding_model: Optional[str] = Form(None),
    chunk_size: Optional[int] = Form(1000),
    chunk_overlap: Optional[int] = Form(200),
    metadata: Optional[str] = Form(None)
):
    """Upload and process a document file"""
    # Create temp file
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Check if we have a processor for this file type
        processor = processor_factory.get_processor(temp_file_path)
        if not processor:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format: {os.path.splitext(file.filename)[1]}"
            )
        
        # Process in background
        document_id = str(uuid.uuid4())
        background_tasks.add_task(
            process_document, 
            temp_file_path, 
            document_id,
            vector_store_id, 
            embedding_model,
            chunk_size,
            chunk_overlap,
            metadata
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "document_id": document_id,
                "original_name": file.filename,
                "status": "processing",
                "message": "Document processing started"
            }
        )
    
    except Exception as e:
        # Clean up
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        logger.error(f"Error processing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/url")
async def process_url(
    background_tasks: BackgroundTasks,
    url: str,
    vector_store_id: int,
    embedding_model: Optional[str] = None,
    chunk_size: Optional[int] = 1000,
    chunk_overlap: Optional[int] = 200,
    follow_links: Optional[bool] = False,
    max_depth: Optional[int] = 1,
    same_domain_only: Optional[bool] = True,
    metadata: Optional[Dict[str, Any]] = None
):
    """Process content from a URL"""
    try:
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Process in background
        background_tasks.add_task(
            extract_and_process_url,
            url,
            document_id,
            vector_store_id,
            embedding_model,
            chunk_size,
            chunk_overlap,
            follow_links,
            max_depth,
            same_domain_only,
            metadata or {}
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "document_id": document_id,
                "url": url,
                "status": "processing",
                "message": "URL processing started",
                "follow_links": follow_links,
                "max_depth": max_depth
            }
        )
    
    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}")
async def get_document_status(document_id: str):
    """Get status of document processing"""
    try:
        # This is a placeholder. In a real implementation, you would query the database.
        return {
            "document_id": document_id,
            "status": "processing",  # or "completed", "failed"
            "message": "Document is being processed"
        }
    except Exception as e:
        logger.error(f"Error getting document status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its embeddings"""
    try:
        # This is a placeholder. In a real implementation, you would delete from the database.
        return {
            "document_id": document_id,
            "status": "deleted",
            "message": "Document deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Background processing functions
async def process_document(
    file_path: str,
    document_id: str,
    vector_store_id: int,
    embedding_model: Optional[str],
    chunk_size: int,
    chunk_overlap: int,
    metadata_str: Optional[str]
):
    """Process document in background"""
    temp_dir = os.path.dirname(file_path)
    
    try:
        # Parse metadata
        metadata = json.loads(metadata_str) if metadata_str else {}
        
        # Get document processor
        processor = processor_factory.get_processor(file_path)
        
        if not processor:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        # Process document
        chunks = await processor.process(
            file_path,
            metadata=metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # In a real implementation, you would:
        # 1. Generate embeddings for chunks
        # 2. Store embeddings in vector store
        # 3. Update document status in database
        
        logger.info(f"Processed document {document_id} with {len(chunks)} chunks")
        
    except Exception as e:
        # Log error
        logger.error(f"Error processing document {document_id}: {str(e)}")
        # Update document status to failed
    
    finally:
        # Clean up
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

async def extract_and_process_url(
    url: str,
    document_id: str,
    vector_store_id: int,
    embedding_model: Optional[str],
    chunk_size: int,
    chunk_overlap: int,
    follow_links: bool,
    max_depth: int,
    same_domain_only: bool,
    metadata: Dict[str, Any]
):
    """Extract and process URL content in background"""
    try:
        # Extract content
        url_extractor = URLContentExtractor()
        content_data = await url_extractor.extract(
            url,
            follow_links=follow_links,
            max_depth=max_depth,
            same_domain_only=same_domain_only
        )
        
        # Add URL to metadata
        metadata['source_url'] = url
        metadata['extraction_time'] = datetime.now().isoformat()
        
        if 'title' in content_data:
            metadata['title'] = content_data['title']
            
        if 'metadata' in content_data:
            for key, value in content_data['metadata'].items():
                metadata[f'page_{key}'] = value
        
        # Process main content
        main_content = content_data['content']
        chunker = TextChunker()
        chunks = chunker.chunk(main_content, chunk_size, chunk_overlap)
        
        # Process linked content if available
        linked_chunks = []
        if follow_links and 'linked_content' in content_data:
            for linked_page in content_data.get('linked_content', []):
                linked_text = f"# {linked_page.get('title', 'Linked Page')}\n\n"
                linked_text += linked_page['content']
                page_chunks = chunker.chunk(linked_text, chunk_size, chunk_overlap)
                
                # Add source URL to each chunk's metadata
                for chunk in page_chunks:
                    linked_chunks.append({
                        'text': chunk,
                        'metadata': {
                            **metadata,
                            'source_url': linked_page['url'],
                            'linked_from': url
                        }
                    })
        
        logger.info(f"Processed URL {url} with {len(chunks)} main chunks and {len(linked_chunks)} linked chunks")
        
        # In a real implementation, you would:
        # 1. Generate embeddings for all chunks (main and linked)
        # 2. Store embeddings in vector store
        # 3. Update document status in database
        
    except Exception as e:
        # Log error
        logger.error(f"Error processing URL {url} (document {document_id}): {str(e)}")
        # Update document status to failed