from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

multi_chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant,solve any technical problems"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])