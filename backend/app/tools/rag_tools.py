from app.utils.mcp import create_mcp_stdio_client


async def get_stdio_rag_tools():
    params = {
        "command": "python",
        "args": ["app/mcp/rag_tools.py"]
    }

    client, tools = await create_mcp_stdio_client("rag_tools", params)

    return tools