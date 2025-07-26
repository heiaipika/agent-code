from langchain_community.agent_toolkits.file_management import FileManagementToolkit
import os

file_tools = FileManagementToolkit(root_dir=os.getcwd()).get_tools()