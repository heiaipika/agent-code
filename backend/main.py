
import sys
import os
import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all API routers
from app.api.chat_api import router as chat_router
from app.api.upload_api import router as upload_router

# Create main app
app = FastAPI(
    title="AI Agent & RAG System API",
    description="AI Agent Chat System and RAG Document Retrieval System - Support Multi-Knowledge Base Management and Intelligent Tool Calling",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(chat_router)
app.include_router(upload_router)

@app.get("/")
async def root():
    """Root path, display API information"""
    return {
        "message": "AI Agent & RAG System API",
        "version": "1.0.0",
        "docs": "/docs",
        "features": {
            "multi_knowledge_base": "Support multi-knowledge base management",
            "rag_tools": "RAG tools integrated into Agent",
            "smart_answering": "Smart answering: first based on chat history, then use tools if unable to answer",
            "tool_integration": "Integrate file, Shell, PowerShell, RAG and other tools",
            "git_repository": "Git repository analysis and knowledge base integration"
        },
        "endpoints": {
            "chat": {
                "description": "AI Agent chat functionality (integrated RAG tools)",
                "endpoints": {
                    "chat": "POST /api/chat",
                    "knowledge_bases": "GET /api/knowledge-bases",
                    "health": "GET /api/health"
                }
            },
            "rag": {
                "description": "RAG document retrieval system",
                "endpoints": {
                    "upload": "POST /rag/upload",
                    "query": "POST /rag/query",
                    "analyze_git_repository": "POST /rag/analyze-git-repository",
                    "knowledge_bases": "GET /rag/knowledge-bases",
                    "create_kb": "POST /rag/knowledge-bases",
                    "get_kb": "GET /rag/knowledge-bases/{kb_id}",
                    "delete_kb": "DELETE /rag/knowledge-bases/{kb_id}",
                    "health": "GET /rag/health",
                    "files": "GET /rag/files"
                }
            }
        }
    }

@app.get("/health")
async def health_check():
    """Global health check"""
    return {
        "status": "healthy",
        "message": "AI Agent & RAG System API is running",
        "services": {
            "chat_api": "running",
            "rag_api": "running"
        },
        "integrations": {
            "rag_tools": "integrated",
            "file_tools": "integrated", 
            "shell_tools": "integrated",
            "powershell_tools": "integrated"
        }
    }

def main():
    parser = argparse.ArgumentParser(description="AI Agent & RAG System API Server")
    parser.add_argument(
        "--host", 
        default="0.0.0.0",
        help="API service host address (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="API service port (default: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true",
        help="Enable hot reload"
    )
    
    args = parser.parse_args()
    
    print("🚀 Start AI Agent & RAG System API Server...")
    print(f"API service will start at http://{args.host}:{args.port}")
    print("API documentation: http://localhost:8000/docs")
    print("=" * 80)
    print("🎯 Core Features:")
    print("  • Multi-knowledge base management (Redis storage)")
    print("  • RAG tools integrated into Agent")
    print("  • Smart answering strategy: chat history → tool calling")
    print("  • Multiple tool integration: file, Shell, PowerShell, RAG")
    print("=" * 80)
    print("📝 Chat API (Integrated RAG Tools):")
    print("  - POST /api/chat - AI Agent chat")
    print("  - GET  /api/knowledge-bases - Get available knowledge bases")
    print("  - GET  /api/health - Chat API health check")
    print("")
    print("📚 RAG System:")
    print("  - POST /rag/upload - Upload file to knowledge base")
    print("  - POST /rag/query - Query knowledge base")
    print("  - GET  /rag/knowledge-bases - List all knowledge bases")
    print("  - POST /rag/knowledge-bases - Create new knowledge base")
    print("  - GET  /rag/knowledge-bases/{kb_id} - Get knowledge base details")
    print("  - DELETE /rag/knowledge-bases/{kb_id} - Delete knowledge base")
    print("  - GET  /rag/health - RAG system health check")
    print("  - GET  /rag/files - View uploaded files")
    print("")
    print("🌐 Global:")
    print("  - GET  /health - Global health check")
    print("=" * 80)
    print("💡 Usage Instructions:")
    print("  1. Chat will first answer based on chat history")
    print("  2. If unable to answer, automatically call relevant tools")
    print("  3. Knowledge-related questions will prioritize RAG tools")
    print("  4. Support selecting specific knowledge base for conversation")
    print("=" * 80)
    
    try:
        import uvicorn
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 API service has stopped")
    except Exception as e:
        print(f"❌ API service startup failed: {e}")

if __name__ == "__main__":
    main() 