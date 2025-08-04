import os
import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import RAG related modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from app.rag.knowledge_manager import kb_manager, KnowledgeBase
from app.mcp.rag_tools import rag_manager

# Create router instead of FastAPI app
router = APIRouter(prefix="/rag", tags=["RAG System"])

# Configure upload directory
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class QueryRequest(BaseModel):
    query: str
    kb_id: str = None  # Optional, if not provided use default knowledge base
    k: int = 5

class UploadRequest(BaseModel):
    kb_id: str = None  # Optional, if not provided use default knowledge base or create new

class GitRepositoryRequest(BaseModel):
    repo_url: str
    username: str
    token: str
    kb_id: str = None  # Optional, if not provided use default knowledge base or create new

class UploadResponse(BaseModel):
    message: str
    file_path: str
    kb_id: str
    kb_name: str
    chunks_count: int
    collection_info: dict

class GitRepositoryResponse(BaseModel):
    message: str
    repo_url: str
    kb_id: str
    kb_name: str
    files_processed: int
    collection_info: dict

class QueryResponse(BaseModel):
    kb_id: str
    kb_name: str
    query: str
    results: List[str]
    total_documents: int

class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    description: str
    file_count: int
    vector_count: int
    created_at: str
    updated_at: str
    status: str

class CreateKnowledgeBaseRequest(BaseModel):
    name: str
    description: str = ""

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    kb_id: str = Form(None)
):
    """
    Upload file to RAG system
    """
    try:
        # Check file type
        allowed_extensions = {'.txt', '.pdf', '.docx', '.doc', '.md', '.csv'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Supported types: {allowed_extensions}"
            )
        
        # Save file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Determine knowledge base
        if kb_id:
            kb = kb_manager.get_knowledge_base(kb_id)
            if not kb:
                raise HTTPException(status_code=404, detail=f"Knowledge base not found: {kb_id}")
        else:
            # Use default knowledge base or create new
            active_kbs = kb_manager.get_active_knowledge_bases()
            if not active_kbs:
                kb = kb_manager.create_knowledge_base("Default Knowledge Base", "Default knowledge base")
            else:
                kb = active_kbs[0]
        
        # Process file through RAG manager
        try:
            result = rag_manager.upload_to_knowledge_base(kb.id, str(file_path))
            
            if result["success"]:
                return UploadResponse(
                    message="File uploaded and processed successfully",
                    file_path=str(file_path),
                    kb_id=kb.id,
                    kb_name=kb.name,
                    chunks_count=result["chunks_count"],
                    collection_info=result["collection_info"]
                )
            else:
                raise HTTPException(status_code=500, detail=f"File processing failed: {result['error']}")
                
        except Exception as e:
            # If RAG processing fails, still return success for file upload
            return UploadResponse(
                message=f"File uploaded successfully but processing failed: {str(e)}",
                file_path=str(file_path),
                kb_id=kb.id,
                kb_name=kb.name,
                chunks_count=0,
                collection_info={"status": "error", "error": str(e)}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query RAG system
    """
    try:
        # Determine knowledge base
        if request.kb_id:
            kb = kb_manager.get_knowledge_base(request.kb_id)
            if not kb:
                raise HTTPException(status_code=404, detail=f"Knowledge base not found: {request.kb_id}")
        else:
            # Use default knowledge base
            active_kbs = kb_manager.get_active_knowledge_bases()
            if not active_kbs:
                raise HTTPException(status_code=404, detail="No available knowledge bases")
            kb = active_kbs[0]
        
        # Query through RAG manager
        try:
            result = rag_manager.query_knowledge_base(kb.id, request.query, k=request.k)
            
            if result["success"]:
                return QueryResponse(
                    kb_id=kb.id,
                    kb_name=kb.name,
                    query=request.query,
                    results=result["results"],
                    total_documents=result["total_documents"]
                )
            else:
                raise HTTPException(status_code=500, detail=f"Query failed: {result['error']}")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/knowledge-bases", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases():
    """
    List all knowledge bases
    """
    try:
        knowledge_bases = kb_manager.get_active_knowledge_bases()
        return [
            KnowledgeBaseResponse(
                id=kb.id,
                name=kb.name,
                description=kb.description,
                file_count=kb.file_count,
                vector_count=kb.vector_count,
                created_at=kb.created_at,
                updated_at=kb.updated_at,
                status="active"
            ) 
            for kb in knowledge_bases
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge bases list: {str(e)}")

@router.post("/knowledge-bases", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(request: CreateKnowledgeBaseRequest):
    """
    Create new knowledge base
    """
    try:
        # Check if name already exists
        existing_kb = kb_manager.get_kb_by_name(request.name)
        if existing_kb:
            raise HTTPException(status_code=400, detail=f"Knowledge base name already exists: {request.name}")
        
        kb = kb_manager.create_knowledge_base(request.name, request.description)
        return KnowledgeBaseResponse(**kb.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create knowledge base: {str(e)}")

@router.get("/knowledge-bases/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(kb_id: str):
    """
    Get knowledge base details
    """
    try:
        kb = kb_manager.get_knowledge_base(kb_id)
        if not kb:
            raise HTTPException(status_code=404, detail=f"Knowledge base not found: {kb_id}")
        return KnowledgeBaseResponse(**kb.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge base details: {str(e)}")

@router.delete("/knowledge-bases/{kb_id}")
async def delete_knowledge_base(kb_id: str):
    """
    Delete knowledge base
    """
    try:
        success = kb_manager.delete_knowledge_base(kb_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Knowledge base not found: {kb_id}")
        return {"message": "Knowledge base deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete knowledge base: {str(e)}")

@router.get("/health")
async def rag_health_check():
    """
    RAG system health check
    """
    try:
        active_kbs = kb_manager.get_active_knowledge_bases()
        return {
            "status": "healthy",
            "active_knowledge_bases": len(active_kbs),
            "total_knowledge_bases": len(kb_manager.list_knowledge_bases())
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/files")
async def list_uploaded_files():
    """
    List uploaded files
    """
    try:
        files = []
        for file_path in UPLOAD_DIR.iterdir():
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "path": str(file_path)
                })
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get files list: {str(e)}")

@router.post("/analyze-git-repository", response_model=GitRepositoryResponse)
async def analyze_git_repository(request: GitRepositoryRequest):
    """
    Analyze Git repository and add to knowledge base
    """
    try:
        from app.rag.git_repository import GitRepositoryAnalyzer
        
        # Determine knowledge base
        if request.kb_id:
            kb = kb_manager.get_knowledge_base(request.kb_id)
            if not kb:
                raise HTTPException(status_code=404, detail=f"Knowledge base not found: {request.kb_id}")
        else:
            # Use default knowledge base or create new
            active_kbs = kb_manager.get_active_knowledge_bases()
            if not active_kbs:
                kb = kb_manager.create_knowledge_base("Default Knowledge Base", "Default knowledge base")
            else:
                kb = active_kbs[0]
        
        # Create analyzer and process repository
        analyzer = GitRepositoryAnalyzer()
        result = analyzer.analyze_repository(
            repo_url=request.repo_url,
            username=request.username,
            token=request.token,
            kb_id=kb.id
        )
        
        return GitRepositoryResponse(
            message="Git repository analyzed successfully",
            repo_url=request.repo_url,
            kb_id=kb.id,
            kb_name=kb.name,
            files_processed=result["files_processed"],
            collection_info=result["collection_info"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git repository analysis failed: {str(e)}")
