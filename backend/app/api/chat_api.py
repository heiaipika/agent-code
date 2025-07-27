import asyncio
import json
import time
import os
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, ToolMessage
from pydantic import BaseModel
from app.agent.code_agent import agent_respond

app = FastAPI(title="AI Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

async def stream_agent_response(user_message: str):
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

@app.post("/api/chat")
async def chat_endpoint(chat: ChatRequest):
    user_message = chat.message
    if not user_message:
        return {"error": "msg can't be empty"}
    async def generate():
        try:
            async for chunk in stream_agent_response(user_message):
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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Agent API is running"} 