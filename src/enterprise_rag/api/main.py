import logging
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import shutil
from pathlib import Path
import os
import asyncio
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    categories: Dict[str, List[Dict[str, Any]]]
    message: Optional[str] = None
    processing_time: Optional[float] = None

# Initialize components
try:
    from ..core.document_processor import DocumentProcessor
    from ..core.embedding_service import EmbeddingService
    from ..core.vector_store import VectorStore
    from ..core.rag_engine import RAGEngine

    doc_processor = DocumentProcessor()
    embedding_service = EmbeddingService()
    vector_store = VectorStore(
        collection_name="radiation_docs",
        persist_directory="data/vector_store"
    )
    rag_engine = RAGEngine(embedding_service, vector_store)
    logger.info("Components initialized successfully")
except Exception as e:
    logger.error(f"Error initializing components: {e}")
    raise

# Initialize FastAPI
app = FastAPI(title="RAG System")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates setup
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error serving template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# File upload endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file upload: {file.filename}")
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Create upload directory
        upload_dir = Path("data/documents")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file path
        file_path = upload_dir / file.filename
        logger.info(f"Saving file to: {file_path}")
        
        # Save uploaded file
        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            logger.info("File saved successfully")
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

        # Process document
        try:
            logger.info("Processing document...")
            chunks = doc_processor.process_document(str(file_path))
            logger.info(f"Document processed into {len(chunks)} chunks")

            # Generate embeddings
            logger.info("Generating embeddings...")
            texts = [chunk["text"] for chunk in chunks]
            embeddings = embedding_service.generate_embeddings(texts)
            logger.info(f"Generated embeddings of shape {embeddings.shape}")

            # Store in vector store
            logger.info("Storing in vector database...")
            vector_store.add_documents(chunks, embeddings)
            logger.info("Documents stored successfully")

            return {
                "message": f"Successfully processed {len(chunks)} chunks from {file.filename}",
                "status": "success",
                "chunks": len(chunks)
            }
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Query endpoint
@app.post("/query")
async def query_system(query_req: QueryRequest):
    try:
        logger.info(f"Processing query: {query_req.query}")
        
        # Check if vector store is empty
        if vector_store.is_empty():
            logger.warning("Vector store is empty")
            return {
                "message": "No documents have been processed yet. Please upload a document first.",
                "categories": {},
                "processing_time": 0
            }

        # Process query
        start_time = asyncio.get_event_loop().time()
        results = await rag_engine.process_query(query_req.query)
        processing_time = asyncio.get_event_loop().time() - start_time
        
        # Add processing time to results
        results["processing_time"] = processing_time
        
        logger.info(f"Query processed in {processing_time:.2f} seconds")
        logger.info(f"Results: {results}")
        
        return results

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )

# Query debug endpoint
@app.post("/query-debug")
async def query_debug(query_req: QueryRequest):
    """Debug endpoint to test query processing"""
    try:
        logger.info(f"Debug: Received query: {query_req.query}")
        
        # Check vector store status
        store_empty = vector_store.is_empty()
        logger.info(f"Debug: Vector store empty: {store_empty}")
        
        if not store_empty:
            # Get store stats
            stats = vector_store.get_stats()
            logger.info(f"Debug: Vector store stats: {stats}")
            
            # Generate query embedding
            query_embedding = embedding_service.generate_embeddings([query_req.query])[0]
            logger.info(f"Debug: Generated query embedding shape: {query_embedding.shape}")
            
            # Get results
            results = await rag_engine.process_query(query_req.query)
            logger.info(f"Debug: Query results: {results}")
            
            return {
                "status": "success",
                "vector_store_stats": stats,
                "embedding_shape": query_embedding.shape,
                "results": results
            }
        else:
            return {
                "status": "empty",
                "message": "Vector store is empty"
            }
            
    except Exception as e:
        logger.error(f"Debug: Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Clear database endpoint
@app.post("/clear-database")
async def clear_database():
    try:
        logger.info("Clearing vector database")
        vector_store.clear()
        return {"message": "Vector database cleared successfully"}
    except Exception as e:
        logger.error(f"Failed to clear database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Check components
        doc_processor_status = "healthy"
        
        # Check vector store
        vector_store_status = "healthy" if not vector_store.is_empty() else "empty"
        
        # Check embedding service
        try:
            test_embedding = embedding_service.generate_embeddings(["test"])[0]
            embedding_status = "healthy" if isinstance(test_embedding, np.ndarray) else "error"
        except:
            embedding_status = "error"
        
        return {
            "status": "healthy",
            "components": {
                "document_processor": doc_processor_status,
                "embedding_service": embedding_status,
                "vector_store": vector_store_status
            },
            "vector_store_empty": vector_store.is_empty()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Upload debug endpoint
@app.post("/upload-debug")
async def upload_debug(file: UploadFile = File(...)):
    """Debug endpoint to test file uploads"""
    try:
        logger.info(f"Debug: Received file: {file.filename}")
        logger.info(f"Debug: Content type: {file.content_type}")
        
        # Read first few bytes
        preview = await file.read(1024)
        await file.seek(0)  # Reset file pointer
        
        logger.info(f"Debug: File preview size: {len(preview)} bytes")
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(preview),
            "preview": preview[:100] if preview else None
        }
    except Exception as e:
        logger.error(f"Debug: Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return HTMLResponse(
        content="Internal server error",
        status_code=500
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")