"""
FastAPI application for RAG Chat Backend
Provides REST API endpoints for user management, chat functionality, and book uploads
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.routers import users, chats, messages, books

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chat Backend API",
    description="""
    A Retrieval-Augmented Generation (RAG) chat application that allows users to:
    - Upload and process PDF books
    - Chat with AI about the content of their uploaded books
    - Maintain conversation history
    - Retrieve contextual information from their document library

    The API uses:
    - OpenAI for language generation
    - Pinecone for vector storage and similarity search
    - Supabase for data persistence
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
# Allow all origins for development. In production, replace with specific domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(chats.router)
app.include_router(messages.router)
app.include_router(books.router)


@app.get("/")
async def root():
    """
    Root endpoint - API health check and information.

    Returns:
        JSON with API information and available endpoints
    """
    return {
        "message": "RAG Chat Backend API",
        "version": "1.0.0",
        "status": "running",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "users": "/api/users",
            "chats": "/api/chats",
            "messages": "/api/messages",
            "books": "/api/books"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        JSON with health status
    """
    return {
        "status": "healthy",
        "service": "rag-chat-backend"
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, _exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "Not Found",
            "detail": "The requested resource was not found",
            "path": str(request.url)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(_request, _exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later."
        }
    )


if __name__ == "__main__":
    # Run the application
    # Use reload=True for development, set to False in production
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
