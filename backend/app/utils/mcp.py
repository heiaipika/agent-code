from langchain_mcp_adapters.client import MultiServerMCPClient

async def create_mcp_stdio_client(name, params):
    config = {
        name: {
            "transport": "stdio",
            **params,
        }
    }
    
    print(config)
    client = MultiServerMCPClient(config)
    
    tools = await client.get_tools()
    
    return client, tools
