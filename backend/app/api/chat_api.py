import asyncio
import json
import time
import os
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, ToolMessage
from pydantic import BaseModel
from app.agent.code_agent import agent_respond

# Import RAG related modules
from app.rag.knowledge_manager import kb_manager

# Create router instead of FastAPI app
router = APIRouter(prefix="/api", tags=["Chat API"])

class ChatRequest(BaseModel):
    message: str
    kb_id: str = None  # Optional, select knowledge base ID

class ChatResponse(BaseModel):
    message: str
    kb_id: str = None
    kb_name: str = None

async def stream_agent_response(user_message: str, kb_id: str = None):
    async for chunk in agent_respond(user_message):
        for node_name, node_output in chunk.items():
            if "messages" in node_output:
                for msg in node_output["messages"]:
                    if isinstance(msg, AIMessage) and msg.content:
                        yield f"data: {{\"content\": {json.dumps(msg.content, ensure_ascii=False)}, \"type\": \"thinking\"}}\n\n"
                    elif isinstance(msg, ToolMessage):
                        tool_name = getattr(msg, "name", "unknown")
                        tool_content = msg.content
                        tool_result = f"🔍 Tool: {tool_name}\n🤖 Result: {tool_content}"
                        yield f"data: {{\"content\": {json.dumps(tool_result, ensure_ascii=False)}, \"type\": \"tool_result\"}}\n\n"

@router.post("/chat")
async def chat_endpoint(chat: ChatRequest):
    user_message = chat.message
    kb_id = chat.kb_id
    
    if not user_message:
        return {"error": "Message cannot be empty"}
    
    async def generate():
        try:
            if kb_id:
                kb = kb_manager.get_knowledge_base(kb_id)
                if kb:
                    yield f"data: {{\"content\": {json.dumps(f'Available knowledge base: {kb.name}', ensure_ascii=False)}, \"type\": \"kb_info\"}}\n\n"
                    enhanced_message = f"{user_message}\n\nnote: current has available knowledge base '{kb.name}', if there is no related information in the chat history, you can consider using the knowledge base to query."
                else:
                    enhanced_message = user_message
            else:
                enhanced_message = user_message
            
            async for chunk in stream_agent_response(enhanced_message, kb_id):
                yield chunk
            yield "data: [DONE]\n\n"
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            error_msg = f"data: {{\"error\": {json.dumps(str(e))}, \"trace\": {json.dumps(tb)} }}\n\n"
            yield error_msg
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.get("/knowledge-bases")
async def get_available_knowledge_bases():
    """Get available knowledge bases list"""
    try:
        knowledge_bases = kb_manager.get_active_knowledge_bases()
        return {
            "knowledge_bases": [
                {
                    "id": kb.id,
                    "name": kb.name,
                    "description": kb.description,
                    "file_count": kb.file_count,
                    "vector_count": kb.vector_count
                }
                for kb in knowledge_bases
            ]
        }
    except Exception as e:
        return {"error": f"Failed to get knowledge bases list: {str(e)}"}

@router.get("/health")
async def chat_health_check():
    return {"status": "healthy", "message": "AI Agent API is running"} 