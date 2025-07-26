import asyncio
import time
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from app.model.qwen import llm_deepseek
from app.tools.file_tools import file_tools
from app.tools.shell_tools import get_stdio_shell_tools
from app.tools.powershell_tools import get_stdio_powershell_tools
from langgraph.checkpoint.memory import MemorySaver


def format_debug_output(step_name: str, content: str,is_tool_call=False)-> None:
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

async def run_agent():
    memory = MemorySaver()
    
    shell_tools = await get_stdio_shell_tools()
    powershell_tools = await get_stdio_powershell_tools()
    
    tools = file_tools + shell_tools + powershell_tools
    
    agent = create_react_agent(
        model=llm_deepseek,
        tools=tools,
        checkpointer=memory,
        debug=False,
    )
    
    config = RunnableConfig(configurable={"thread_id": 2})
    
    while True:
        user_input = input("user: ")
        
        if user_input.lower() == "exit":
            break
            
        print("\n🤖 agent start thinking...")
        print("="*60)

        iteration_count = 0
        start_time=time.time()
        last_tool_time=start_time
        async for chunk in agent.astream(input={"messages": user_input}, config=config):
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

asyncio.run(run_agent())