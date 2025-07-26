import asyncio
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.redis import RedisSaver
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.prebuilt import create_react_agent

from app.code_agent.model.qwen import llm_deepseek
from app.code_agent.tools.file_tools import file_tools


def run_agent():
    memory = MemorySaver()

    with RedisSaver.from_conn_string("redis://192.168.64.2:6379") as memory:
        memory.setup()


    with MongoDBSaver.from_conn_string(RedisSaver) as memory:

        agent = create_react_agent(
            model=llm_deepseek,
            tools=file_tools,
            checkpointer=memory,
            debug=False,
        )

        config = RunnableConfig(configurable={"thread_id": 2})

        res = agent.invoke(input={"messages": [("user", "我是谁？")]}, config=config)
        print("=" * 60)
        print(res)
        print("=" * 60)

        memory.close()


if __name__ == "__main__":
    run_agent()