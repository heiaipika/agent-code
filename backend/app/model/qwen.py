import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.environ.get("SILICONFLOW_API_KEY", "")

from langchain_openai import ChatOpenAI

llm_deepseek = ChatOpenAI(
    model="Qwen/QwQ-32B",
    base_url="https://api.siliconflow.cn/v1",
    api_key=os.environ.get("SILICONFLOW_API_KEY"),
    streaming=True,
)