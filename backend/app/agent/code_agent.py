import os
import asyncio
import time
import uuid
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from app.model.qwen import llm_deepseek
from app.tools.file_tools import file_tools
from app.tools.shell_tools import get_stdio_shell_tools
from app.tools.powershell_tools import get_stdio_powershell_tools
from app.tools.rag_tools import get_stdio_rag_tools
from langgraph.checkpoint.redis import AsyncRedisSaver
from langchain_core.prompts import PromptTemplate


def format_debug_output(step_name: str, content: str, is_tool_call=False) -> None:
    if is_tool_call:
        print(f"🔍[Tool]{step_name}")
        print("="*40)
        print(content)
        print("="*40)
    else:
        print(f"☁[{step_name}]")
        print("="*40)
        print(content)
        print("="*40)

async def agent_respond(user_message: str, thread_id: str = None):
    if thread_id is None:
        thread_id = str(uuid.uuid4())
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    async with AsyncRedisSaver.from_conn_string(redis_url) as memory:
        shell_tools = await get_stdio_shell_tools()
        powershell_tools = await get_stdio_powershell_tools()
        rag_tools = await get_stdio_rag_tools()
        
        tools = file_tools + shell_tools + powershell_tools + rag_tools
        prompt = PromptTemplate.from_template(template="""# Role
You are an excellent engineer, your name is {name}""")
        agent = create_react_agent(
            model=llm_deepseek,
            tools=tools,
            checkpointer=memory,
            debug=False,
            prompt=SystemMessage(content=prompt.format(name="Bot")),
        )
        
        config = RunnableConfig(configurable={"thread_id": thread_id}, recursion_limit=100)
        
        print(f"\n🤖 agent start thinking... (thread_id: {thread_id})")
        print("="*60)

        iteration_count = 0
        start_time = time.time()
        last_tool_time = start_time

        user_prompt = \
f"""# Requirements
You should first try to answer based on the chat history. If you cannot answer the question based on the chat history, then use the appropriate tools to help you complete the task.

When you need to use tools:
1. If the question is about knowledge or information, first use query_rag tool to search the knowledge base
2. If you need to perform file operations, use file_tools
3. If you need to execute shell commands, use shell_tools
4. If you need to execute PowerShell commands, use powershell_tools

# User Question
{user_message}"""
        messages = [
        HumanMessage(content=user_prompt)
        ]
        
        try:
            async for chunk in agent.astream(input={"messages": messages}, config=config):
                iteration_count += 1

                print(f"iteration {iteration_count}: {chunk}")
                print("="*30)

                for node_name, node_output in chunk.items():
                    if "messages" in node_output:
                        for msg in node_output["messages"]:
                            if isinstance(msg, AIMessage):
                                if msg.content:
                                    format_debug_output("AI thinking", msg.content)
                                elif hasattr(msg, 'tool_calls') and msg.tool_calls:
                                    for tool in msg.tool_calls:
                                        format_debug_output("Tool execution", f"Tool: {tool['name']}\nArgs: {tool['args']}")
                            elif isinstance(msg, ToolMessage):
                                tool_name = getattr(msg, "name", "unknown")
                                tool_content = msg.content
                                current_time = time.time()
                                tool_duration = current_time - last_tool_time
                                last_tool_time = current_time
                                tool_result = f"""🔍 Tool: {tool_name}
🤖Result: 
{tool_content}
🔍Time: {tool_duration:.2f}s"""
                                format_debug_output("Tool execution result", tool_result, is_tool_call=True)
                
                print(f"\n✅ All {iteration_count} iterations, time cost {time.time() - start_time:.2f}s")
                print()
                
                yield chunk
                
        except Exception as e:
            print(f"❌ Error in agent.astream: {e}")
            import traceback
            traceback.print_exc()


async def run_agent():
    thread_id = str(uuid.uuid4())
    print(f"Starting new session with thread_id: {thread_id}")
    
    while True:
        user_input = input("User: ")
        
        if user_input.lower() == "exit":
            break
            
        async for chunk in agent_respond(user_input, thread_id):
            pass  # Just consume the chunks for CLI mode


if __name__ == "__main__":
    asyncio.run(run_agent())