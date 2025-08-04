import os
import shutil
import logging
import time
import uuid
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse
import git
from git import Repo
from git.remote import RemoteProgress

# Import document processing modules
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredMarkdownLoader,
    CSVLoader,
    Docx2txtLoader
)
from langchain_community.document_loaders.pdf import PyPDFLoader

# Import vector store and knowledge base modules
from app.rag.knowledge_manager import kb_manager
from app.mcp.rag_tools import VectorDatabaseManager

logger = logging.getLogger(__name__)

class GitRepositoryAnalyzer:
    """Git repository analyzer for cloning repositories and parsing files into knowledge bases"""
    
    def __init__(self):
        timestamp = int(time.time())
        random_id = str(uuid.uuid4())[:8]
        self.local_path = f"./git-cloned-repo-{timestamp}-{random_id}"
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        self.supported_extensions = {
            '.txt', '.md', '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', 
            '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', 
            '.scala', '.r', '.m', '.sql', '.sh', '.bat', '.ps1', '.yml', 
            '.yaml', '.json', '.xml', '.html', '.css', '.scss', '.less',
            '.pdf', '.docx', '.doc', '.csv'
        }
        
        self.ignore_patterns = {
            '.git', '.gitignore', '.gitattributes', '.DS_Store', 'Thumbs.db',
            '__pycache__', 'node_modules', '.venv', 'venv', 'env', '.env',
            'target', 'build', 'dist', 'out', 'bin', 'obj', '.idea', '.vscode',
            '*.log', '*.tmp', '*.temp', '*.cache', '*.lock'
        }
    
    def extract_project_name(self, repo_url: str) -> str:
        parsed_url = urlparse(repo_url)
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) >= 2:
            project_name = path_parts[-1]
            return project_name.replace('.git', '')
        else:
            return repo_url.split('/')[-1].replace('.git', '')
    
    def should_ignore_file(self, file_path: Path) -> bool:
        file_name = file_path.name
        file_path_str = str(file_path)
        
        if file_name in self.ignore_patterns:
            return True
        
        for pattern in self.ignore_patterns:
            if pattern in file_path_str:
                return True
        
        if file_path.suffix.lower() not in self.supported_extensions:
            return True
        
        return False
    
    def load_document(self, file_path: Path) -> List[Document]:
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension == '.txt':
                loader = TextLoader(str(file_path), encoding='utf-8')
            elif file_extension == '.md':
                loader = UnstructuredMarkdownLoader(str(file_path))
            elif file_extension == '.pdf':
                loader = PyPDFLoader(str(file_path))
            elif file_extension in ['.docx', '.doc']:
                loader = Docx2txtLoader(str(file_path))
            elif file_extension == '.csv':
                loader = CSVLoader(str(file_path))
            elif file_extension in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', 
                                   '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', 
                                   '.kt', '.scala', '.r', '.m', '.sql', '.sh', '.bat', 
                                   '.ps1', '.yml', '.yaml', '.json', '.xml', '.html', 
                                   '.css', '.scss', '.less']:
                loader = TextLoader(str(file_path), encoding='utf-8')
            else:
                logger.warning(f"Unsupported file type: {file_extension} for file: {file_path}")
                return []
            
            documents = loader.load()
            return documents
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            return []
    
    def analyze_repository(self, repo_url: str, username: str, token: str, kb_id: str) -> Dict[str, Any]:
        repo_project_name = self.extract_project_name(repo_url)
        local_path = Path(self.local_path)
        
        logger.info(f"start clone repository: {repo_url}")
        logger.info(f"clone path: {local_path.absolute()}")
        
        self._clean_directory(local_path)
        
        try:
            clone_url = repo_url
            if username and token and '@' not in repo_url:
                parsed_url = urlparse(repo_url)
                clone_url = f"{parsed_url.scheme}://{username}:{token}@{parsed_url.netloc}{parsed_url.path}"
            
            git_repo = Repo.clone_from(
                url=clone_url,
                to_path=local_path,
                progress=GitProgress()
            )
            
            logger.info(f"repository clone completed: {repo_url}")
            
            kb = kb_manager.get_knowledge_base(kb_id)
            if not kb:
                raise Exception(f"Knowledge base not found: {kb_id}")
            
            vector_db_manager = VectorDatabaseManager(kb.collection_name)
            
            files_processed = 0
            total_documents = 0
            
            for file_path in local_path.rglob('*'):
                if file_path.is_file() and not self.should_ignore_file(file_path):
                    try:
                        logger.info(f"processing file: {file_path.name}")
                        
                        documents = self.load_document(file_path)
                        if not documents:
                            continue
                        
                        for doc in documents:
                            doc.metadata.update({
                                "knowledge": repo_project_name,
                                "source": str(file_path),
                                "file_type": file_path.suffix.lower(),
                                "kb_id": kb_id
                            })
                        
                        split_documents = self.text_splitter.split_documents(documents)
                        
                        for doc in split_documents:
                            doc.metadata.update({
                                "knowledge": repo_project_name,
                                "source": str(file_path),
                                "file_type": file_path.suffix.lower(),
                                "kb_id": kb_id
                            })
                        
                        vector_db_manager.add_documents(split_documents)
                        
                        files_processed += 1
                        total_documents += len(split_documents)
                        
                        logger.info(f"file processing completed: {file_path.name}, document count: {len(split_documents)}")
                        
                    except Exception as e:
                        logger.error(f"failed to process file {file_path.name}: {str(e)}")
                        continue
            
            kb_manager.update_kb_stats(kb_id, file_count=files_processed, vector_count=total_documents)
            
            self.add_knowledge_tag_to_redis(repo_project_name)
            
            logger.info(f"repository analysis completed: {repo_url}, file count: {files_processed}, total document count: {total_documents}")
            
            return {
                "files_processed": files_processed,
                "total_documents": total_documents,
                "collection_info": {
                    "collection_name": kb.collection_name,
                    "status": "completed"
                }
            }
            
        except Exception as e:
            logger.error(f"仓库分析失败: {str(e)}")
            raise
        finally:
            self._clean_directory(local_path)
            logger.info(f"clean clone directory: {local_path}")
    
    def _clean_directory(self, directory_path: Path):
        """Clean directory safely"""
        if not directory_path.exists():
            return
        
        try:
            shutil.rmtree(directory_path)
            logger.info(f"successfully deleted directory: {directory_path}")
        except PermissionError as e:
            logger.warning(f"permission error, try to force delete: {e}")
            try:
                import stat
                import time
                
                def on_rm_error(func, path, exc_info):
                    try:
                        os.chmod(path, stat.S_IWRITE)
                        os.unlink(path)
                    except:
                        pass
                
                shutil.rmtree(directory_path, onerror=on_rm_error)
                logger.info(f"successfully force deleted directory: {directory_path}")
            except Exception as e2:
                logger.error(f"failed to delete directory {directory_path}: {e2}")
        except Exception as e:
            logger.error(f"error deleting directory {directory_path}: {e}")
    
    def add_knowledge_tag_to_redis(self, repo_project_name: str):
        try:
            redis_client = kb_manager.redis_client
            
            rag_tag_key = "ragTag"
            if not redis_client.exists(rag_tag_key):
                redis_client.lpush(rag_tag_key, repo_project_name)
            else:
                existing_tags = redis_client.lrange(rag_tag_key, 0, -1)
                existing_tags = [tag.decode() if isinstance(tag, bytes) else tag for tag in existing_tags]
                
                if repo_project_name not in existing_tags:
                    redis_client.lpush(rag_tag_key, repo_project_name)
            
            logger.info(f"knowledge base tag added to Redis: {repo_project_name}")
            
        except Exception as e:
            logger.error(f"failed to add knowledge base tag to Redis: {str(e)}")


class GitProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        if message:
            logger.info(f"Git operation: {message}")
        if max_count:
            percentage = (cur_count / max_count) * 100
            logger.info(f"progress: {percentage:.1f}% ({cur_count}/{max_count})") 