import os
import json
import uuid
from typing import List, Dict, Optional
from datetime import datetime
import redis
from pydantic import BaseModel

class KnowledgeBase(BaseModel):
    id: str
    name: str
    description: str
    collection_name: str
    created_at: str
    updated_at: str
    file_count: int = 0
    vector_count: int = 0
    status: str = "active"  # active, inactive, deleted

class KnowledgeBaseManager:
    
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(redis_url)
        self.kb_prefix = "knowledge_base:"
        self.kb_list_key = "knowledge_bases"
    
    def create_knowledge_base(self, name: str, description: str = "") -> KnowledgeBase:
        kb_id = str(uuid.uuid4())
        collection_name = f"kb_{kb_id[:8]}"
        now = datetime.now().isoformat()
        
        kb = KnowledgeBase(
            id=kb_id,
            name=name,
            description=description,
            collection_name=collection_name,
            created_at=now,
            updated_at=now
        )
        
        self.redis_client.hset(
            f"{self.kb_prefix}{kb_id}",
            mapping=kb.model_dump()
        )
        
        self.redis_client.lpush(self.kb_list_key, kb_id)
        
        return kb
    
    def get_knowledge_base(self, kb_id: str) -> Optional[KnowledgeBase]:
        data = self.redis_client.hgetall(f"{self.kb_prefix}{kb_id}")
        if not data:
            return None
        
        kb_data = {k.decode(): v.decode() for k, v in data.items()}
        return KnowledgeBase(**kb_data)
    
    def list_knowledge_bases(self) -> List[KnowledgeBase]:
        kb_ids = self.redis_client.lrange(self.kb_list_key, 0, -1)
        knowledge_bases = []
        
        for kb_id in kb_ids:
            kb_id_str = kb_id.decode()
            kb = self.get_knowledge_base(kb_id_str)
            if kb and kb.status != "deleted":
                knowledge_bases.append(kb)
        
        return knowledge_bases
    
    def update_knowledge_base(self, kb_id: str, **kwargs) -> Optional[KnowledgeBase]:
        kb = self.get_knowledge_base(kb_id)
        if not kb:
            return None
        
        for key, value in kwargs.items():
            if hasattr(kb, key):
                setattr(kb, key, value)
        
        kb.updated_at = datetime.now().isoformat()
        
        self.redis_client.hset(
            f"{self.kb_prefix}{kb_id}",
            mapping=kb.model_dump()
        )
        
        return kb
    
    def delete_knowledge_base(self, kb_id: str) -> bool:
        kb = self.get_knowledge_base(kb_id)
        if not kb:
            return False
        
        kb.status = "deleted"
        kb.updated_at = datetime.now().isoformat()
        
        self.redis_client.hset(
            f"{self.kb_prefix}{kb_id}",
            mapping=kb.model_dump()
        )
        
        return True
    
    def get_active_knowledge_bases(self) -> List[KnowledgeBase]:
        all_kbs = self.list_knowledge_bases()
        return [kb for kb in all_kbs if kb.status == "active"]
    
    def update_kb_stats(self, kb_id: str, file_count: int = None, vector_count: int = None):
        update_data = {}
        if file_count is not None:
            update_data["file_count"] = file_count
        if vector_count is not None:
            update_data["vector_count"] = vector_count
        
        if update_data:
            self.update_knowledge_base(kb_id, **update_data)
    
    def get_kb_by_name(self, name: str) -> Optional[KnowledgeBase]:
        all_kbs = self.list_knowledge_bases()
        for kb in all_kbs:
            if kb.name == name:
                return kb
        return None

kb_manager = KnowledgeBaseManager() 