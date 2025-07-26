from app.utils.mcp import create_mcp_stdio_client

async def get_stdio_powershell_tools():
    params = {
        "command": "python",
        "args": ["app/mcp/powershell_tools.py"]
    }
    
    client, tools = await create_mcp_stdio_client("powershell_tools", params)
    
    return tools
