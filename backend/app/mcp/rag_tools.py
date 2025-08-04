import os
import sys
from typing import Annotated, List, Optional
import hashlib
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader, 
    Docx2txtLoader,
    UnstructuredMarkdownLoader,
    CSVLoader,
    GitHubIssuesLoader
)
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import uuid

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from app.rag.knowledge_manager import kb_manager

mcp = FastMCP()

VECTOR_DB_PATH = "./vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

class VectorDatabaseManager:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.client = QdrantClient(host="localhost", port=6333)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self._ensure_collection_exists()
        self._init_vectorstore()
    
    def _ensure_collection_exists(self):
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                print(f"Created collection: {self.collection_name}")
            else:
                print(f"Collection {self.collection_name} already exists")
        except Exception as e:
            print(f"Error ensuring collection exists: {e}")
    
    def _init_vectorstore(self):
        try:
            self.vectorstore = Qdrant(
                client=self.client,
                collection_name=self.collection_name,
                embeddings=self.embeddings,
            )
        except Exception as e:
            print(f"Error initializing vectorstore: {e}")
    
    def add_documents(self, documents: List[Document]) -> int:
        try:
            texts = self.text_splitter.split_documents(documents)
            print(f"Split {len(documents)} documents into {len(texts)} chunks")

            self.vectorstore.add_documents(texts)
            
            return len(texts)
        except Exception as e:
            print(f"Error adding documents: {e}")
            raise e
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []
    
    def get_collection_info(self) -> dict:
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {"error": str(e)}

class RAGManager:
    
    def __init__(self):
        self.vector_managers = {}  
    
    def get_vector_manager(self, collection_name: str) -> VectorDatabaseManager:
        if collection_name not in self.vector_managers:
            self.vector_managers[collection_name] = VectorDatabaseManager(collection_name)
        return self.vector_managers[collection_name]
    
    def upload_to_knowledge_base(self, kb_id: str, file_path: str) -> dict:
        try:
            kb = kb_manager.get_knowledge_base(kb_id)
            if not kb:
                raise Exception(f"Knowledge base not found: {kb_id}")
            
            vector_manager = self.get_vector_manager(kb.collection_name)
            
            documents = load_document(file_path)
            
            chunks_count = vector_manager.add_documents(documents)
            
            collection_info = vector_manager.get_collection_info()
            kb_manager.update_kb_stats(
                kb_id, 
                file_count=kb.file_count + 1,
                vector_count=collection_info.get("vectors_count", 0)
            )
            
            return {
                "success": True,
                "kb_id": kb_id,
                "kb_name": kb.name,
                "chunks_count": chunks_count,
                "collection_info": collection_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def query_knowledge_base(self, kb_id: str, query: str, k: int = 5) -> dict:
        try:
            kb = kb_manager.get_knowledge_base(kb_id)
            if not kb:
                raise Exception(f"Knowledge base not found: {kb_id}")
            
            vector_manager = self.get_vector_manager(kb.collection_name)
            
            results = vector_manager.similarity_search(query, k=k)
            
            return {
                "success": True,
                "kb_id": kb_id,
                "kb_name": kb.name,
                "query": query,
                "results": [doc.page_content for doc in results],
                "total_documents": len(results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

rag_manager = RAGManager()

def load_document(file_path: str) -> List[Document]:
    """Load document from file path based on file extension"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_extension = file_path.suffix.lower()
    
    try:
        if file_extension == '.txt':
            loader = TextLoader(str(file_path), encoding='utf-8')
        elif file_extension == '.pdf':
            loader = PyPDFLoader(str(file_path))
        elif file_extension in ['.docx', '.doc']:
            loader = Docx2txtLoader(str(file_path))
        elif file_extension == '.md':
            loader = UnstructuredMarkdownLoader(str(file_path))
        elif file_extension == '.csv':
            loader = CSVLoader(str(file_path))
        elif file_extension == '.github':
            loader = GitHubIssuesLoader(repo_name="langchain-ai/langchain", access_token=os.getenv("access_token"), max_issues=10)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        documents = loader.load()
        return documents
    
    except Exception as e:
        raise Exception(f"Error loading document {file_path}: {str(e)}")

@mcp.tool(name="query_rag", description="Query knowledge base using vector similarity search")
def query_rag(query: Annotated[str, Field(description="Query content to search in knowledge base", examples="terminal operation standards")]) -> str:
    """Query the knowledge base using vector similarity search"""
    try:
        print("-" * 60)
        print(f"[query_rag] Query: {query}")
        print("-" * 60)
        
        active_kbs = kb_manager.get_active_knowledge_bases()
        if not active_kbs:
            return "No active knowledge bases found."
        
        default_kb = active_kbs[0]
        result = rag_manager.query_knowledge_base(default_kb.id, query, k=5)
        
        if not result["success"]:
            return f"Error querying knowledge base: {result['error']}"
        
        if not result["results"]:
            return "No relevant documents found in the knowledge base."
        
        result_text = f"Knowledge Base: {result['kb_name']}\n"
        result_text += "-" * 40 + "\n"
        
        for i, content in enumerate(result["results"], 1):
            result_text += f"Document {i}:\n{content}\n"
            result_text += "-" * 40 + "\n"
        
        print(f"Found {len(result['results'])} relevant documents")
        print(result_text)
        print("-" * 60)
        
        return result_text
    
    except Exception as e:
        error_msg = f"Error querying knowledge base: {str(e)}"
        print(error_msg)
        return error_msg

@mcp.tool(name="upload_file_to_rag", description="Upload local knowledge file to vector database")
def upload_file_to_rag(file_path: Annotated[str, Field(description="Path to local knowledge file", examples="./docs/terminal_guide.txt")]) -> str:
    """Upload a file to the vector database"""
    try:
        print("=" * 80)
        print(f"Uploading file: {file_path}")
        print("=" * 80)
        
        active_kbs = kb_manager.get_active_knowledge_bases()
        if not active_kbs:
            default_kb = kb_manager.create_knowledge_base("Default Knowledge Base", "默认知识库")
            print(f"Created default knowledge base: {default_kb.name}")
        else:
            default_kb = active_kbs[0]
        
        result = rag_manager.upload_to_knowledge_base(default_kb.id, file_path)
        
        if not result["success"]:
            return f"Error uploading file: {result['error']}"
        
        print(f"Successfully uploaded to knowledge base: {result['kb_name']}")
        print(f"Added {result['chunks_count']} chunks")
        print(f"Collection info: {result['collection_info']}")
        print("=" * 80)
        
        return f"Successfully uploaded file to knowledge base '{result['kb_name']}'. Added {result['chunks_count']} chunks."
    
    except Exception as e:
        error_msg = f"Error uploading file: {str(e)}"
        print(error_msg)
        return error_msg

if __name__ == '__main__':
    mcp.run(transport="stdio") 