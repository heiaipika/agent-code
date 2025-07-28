import os
from typing import Annotated, List, Optional
import hashlib
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader, 
    PDFLoader, 
    Docx2txtLoader,
    UnstructuredMarkdownLoader,
    CSVLoader
)
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import uuid

from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP()

# Vector database configuration
VECTOR_DB_PATH = "./vector_db"
COLLECTION_NAME = "knowledge_base"
EMBEDDING_MODEL = "nomic-embed-text:latest"

class VectorDatabaseManager:
    def __init__(self, db_path: str = VECTOR_DB_PATH, collection_name: str = COLLECTION_NAME):
        self.db_path = db_path
        self.collection_name = collection_name
        self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        self.client = QdrantClient(path=db_path)
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Ensure the collection exists in the vector database"""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            # Create collection if it doesn't exist
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )
    
    def add_documents(self, documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200):
        """Add documents to the vector database"""
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        
        # Create vector store and add documents
        vectorstore = Qdrant.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            path=self.db_path,
            collection_name=self.collection_name,
        )
        
        return len(chunks)
    
    def similarity_search(self, query: str, k: int = 5):
        """Search for similar documents"""
        vectorstore = Qdrant(
            client=self.client,
            collection_name=self.collection_name,
            embeddings=self.embeddings,
        )
        
        results = vectorstore.similarity_search(query, k=k)
        return results
    
    def get_collection_info(self):
        """Get information about the collection"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": collection_info.name,
                "vectors_count": collection_info.vectors_count,
                "status": collection_info.status
            }
        except Exception as e:
            return {"error": str(e)}

# Global vector database manager
vector_db = VectorDatabaseManager()

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
            loader = PDFLoader(str(file_path))
        elif file_extension in ['.docx', '.doc']:
            loader = Docx2txtLoader(str(file_path))
        elif file_extension == '.md':
            loader = UnstructuredMarkdownLoader(str(file_path))
        elif file_extension == '.csv':
            loader = CSVLoader(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        documents = loader.load()
        return documents
    
    except Exception as e:
        raise Exception(f"Error loading document {file_path}: {str(e)}")

def calculate_md5(file_path: str) -> str:
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

@mcp.tool(name="query_rag", description="Query knowledge base using vector similarity search")
def query_rag(query: Annotated[str, Field(description="Query content to search in knowledge base", examples="terminal operation standards")]) -> str:
    """Query the knowledge base using vector similarity search"""
    try:
        print("-" * 60)
        print(f"[query_rag] Query: {query}")
        print("-" * 60)
        
        results = vector_db.similarity_search(query, k=5)
        
        if not results:
            return "No relevant documents found in the knowledge base."
        
        result_text = ""
        for i, doc in enumerate(results, 1):
            result_text += f"Document {i}:\n{doc.page_content}\n"
            result_text += "-" * 40 + "\n"
        
        print(f"Found {len(results)} relevant documents")
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
        
        # Load document
        documents = load_document(file_path)
        print(f"Loaded {len(documents)} document(s)")
        
        # Add to vector database
        chunks_count = vector_db.add_documents(documents)
        print(f"Added {chunks_count} chunks to vector database")
        
        # Get collection info
        info = vector_db.get_collection_info()
        print(f"Collection info: {info}")
        
        print("=" * 80)
        
        return f"Successfully uploaded file. Added {chunks_count} chunks. Collection now has {info.get('vectors_count', 'unknown')} vectors."
    
    except Exception as e:
        error_msg = f"Error uploading file: {str(e)}"
        print(error_msg)
        return error_msg

@mcp.tool(name="get_rag_status", description="Get vector database status and collection information")
def get_rag_status() -> str:
    """Get status of the vector database"""
    try:
        info = vector_db.get_collection_info()
        
        status_text = "Vector Database Status:\n"
        status_text += "=" * 40 + "\n"
        
        if "error" in info:
            status_text += f"Error: {info['error']}\n"
        else:
            status_text += f"Collection Name: {info['name']}\n"
            status_text += f"Vectors Count: {info['vectors_count']}\n"
            status_text += f"Status: {info['status']}\n"
        
        status_text += f"Database Path: {vector_db.db_path}\n"
        status_text += f"Embedding Model: {EMBEDDING_MODEL}\n"
        
        print(status_text)
        return status_text
    
    except Exception as e:
        error_msg = f"Error getting RAG status: {str(e)}"
        print(error_msg)
        return error_msg

@mcp.tool(name="clear_rag_database", description="Clear all data from the vector database")
def clear_rag_database() -> str:
    """Clear all data from the vector database"""
    try:
        print("Clearing vector database...")
        
        # Delete the collection
        vector_db.client.delete_collection(vector_db.collection_name)
        
        # Recreate the collection
        vector_db._ensure_collection_exists()
        
        result = "Vector database cleared successfully. Collection recreated."
        print(result)
        return result
    
    except Exception as e:
        error_msg = f"Error clearing vector database: {str(e)}"
        print(error_msg)
        return error_msg

if __name__ == '__main__':
    mcp.run(transport="stdio")

