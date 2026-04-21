"""
FastAPI application for RAG Chat System.

Endpoints:
- POST /chat: Stream chat responses
- POST /documents/upload: Upload and index documents
- GET /documents: List documents
- DELETE /documents/{doc_id}: Remove document
- GET /health: Health check
- GET /metrics: System metrics
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
import logging
from typing import Optional
import asyncio
import json

from app.models import ChatRequest, ChatResponse, DocumentUpload, Document, HealthResponse, MetricsResponse
from app.config import settings
from app.rag_service import RAGService
from app.agent_service import AgentService
from app.llm_client import LLMClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
app = FastAPI(
    title="RAG Chat System",
    description="Retrieval-Augmented Generation Chat with Document Management",
    version="1.0.0"
)

# Global service instances
rag_service: Optional[RAGService] = None
agent_service: Optional[AgentService] = None
llm_client: Optional[LLMClient] = None

# Metrics
metrics = {
    "total_requests": 0,
    "total_tokens_used": 0,
    "avg_response_time_ms": 0,
    "errors": 0,
    "documents_indexed": 0
}


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global rag_service, agent_service, llm_client

    try:
        llm_client = LLMClient(api_key=settings.ANTHROPIC_API_KEY)
        rag_service = RAGService(
            chroma_host=settings.CHROMA_HOST,
            chroma_port=settings.CHROMA_PORT,
            embedding_model=settings.EMBEDDING_MODEL,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        agent_service = AgentService(llm_client=llm_client, rag_service=rag_service)

        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    if rag_service:
        rag_service.close()
    logger.info("Services shut down")


# ============================================================================
# Chat Endpoint
# ============================================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat request and return streaming response.

    - **message**: User question or prompt
    - **chat_id**: Unique conversation identifier
    - **temperature**: Sampling temperature (0.0-1.0)
    """
    metrics["total_requests"] += 1

    try:
        logger.info(f"Chat request from {request.chat_id}: {request.message[:100]}")

        # Use agent to process request (can call retrieval, calculation, etc.)
        response = await agent_service.process_message(
            message=request.message,
            chat_id=request.chat_id,
            temperature=request.temperature
        )

        # Update metrics
        metrics["total_tokens_used"] += response.tokens_used

        return response

    except Exception as e:
        metrics["errors"] += 1
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat response (Server-Sent Events).

    For real-time response streaming to client.
    """
    metrics["total_requests"] += 1

    async def generate():
        try:
            # Generate response with streaming
            async for chunk in agent_service.stream_message(
                message=request.message,
                chat_id=request.chat_id,
                temperature=request.temperature
            ):
                # Format as SSE
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

        except Exception as e:
            metrics["errors"] += 1
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ============================================================================
# Document Management Endpoints
# ============================================================================

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Upload and index a document for RAG retrieval.

    Supports TXT, PDF files.
    Processing happens in background.
    """
    try:
        logger.info(f"Document upload: {file.filename}")

        # Read file content
        content = await file.read()

        # Schedule indexing in background to not block request
        if background_tasks:
            background_tasks.add_task(
                rag_service.load_and_index_document,
                document_name=file.filename,
                content=content
            )
        else:
            # Fallback if background tasks unavailable
            rag_service.load_and_index_document(
                document_name=file.filename,
                content=content
            )

        metrics["documents_indexed"] += 1

        return {
            "status": "success",
            "message": f"Document '{file.filename}' uploaded and queued for indexing",
            "document_id": file.filename.split('.')[0]
        }

    except Exception as e:
        metrics["errors"] += 1
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/documents", response_model=list[Document])
async def list_documents():
    """
    List all indexed documents in the vector store.

    Returns metadata for each document.
    """
    try:
        documents = rag_service.list_documents()
        return documents

    except Exception as e:
        metrics["errors"] += 1
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """
    Remove document from vector store.

    Note: This removes embeddings, not original document.
    """
    try:
        logger.info(f"Deleting document: {doc_id}")

        success = rag_service.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

        return {"status": "success", "message": f"Document {doc_id} deleted"}

    except Exception as e:
        metrics["errors"] += 1
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Health & Monitoring Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Verifies all services are operational.
    """
    try:
        # Check ChromaDB connection
        rag_connected = rag_service.check_connection()

        # Check LLM connectivity (mock: always true in test)
        llm_connected = llm_client is not None

        status = "healthy" if (rag_connected and llm_connected) else "degraded"

        return HealthResponse(
            status=status,
            services={
                "vector_db": "connected" if rag_connected else "disconnected",
                "llm": "connected" if llm_connected else "disconnected"
            }
        )

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(status="unhealthy", services={})


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    System metrics endpoint.

    Returns usage statistics and performance metrics.
    """
    return MetricsResponse(
        total_requests=metrics["total_requests"],
        total_tokens_used=metrics["total_tokens_used"],
        avg_response_time_ms=metrics["avg_response_time_ms"],
        errors=metrics["errors"],
        documents_indexed=metrics["documents_indexed"]
    )


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint with API documentation.
    """
    return {
        "name": "RAG Chat System",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "chat": "POST /chat",
            "chat_stream": "POST /chat/stream",
            "upload_document": "POST /documents/upload",
            "list_documents": "GET /documents",
            "delete_document": "DELETE /documents/{doc_id}",
            "health": "GET /health",
            "metrics": "GET /metrics"
        }
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors."""
    metrics["errors"] += 1
    return HTTPException(status_code=400, detail=str(exc))


@app.exception_handler(Exception)
async def generic_error_handler(request, exc):
    """Handle unexpected errors."""
    metrics["errors"] += 1
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
