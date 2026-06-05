from langchain_groq import ChatGroq
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_core.tools import tool
from datetime import datetime
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg
import os
from psycopg.rows import dict_row

load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

system_prompt = SystemMessage(content="""
You are a helpful assistant with access to tools.

You can use these tools:
- web_search(query: str): Search the web for current information about events, news, or facts.
- get_current_datetime(): Get the current date and time.
- calculate_expression(expression: str): Calculate a math expression.

When you call a tool, always provide its parameters as a JSON object.
For example:
{"query": "latest AI news"}
{"expression": "2+2"}

Always be concise and accurate. Provide direct answers.
"""
)

DATABASE_URL = os.getenv("DATABASE_URL")

class chatState(TypedDict):
  messages:Annotated[list[BaseMessage],add_messages]

#-------TOOOLSS----------------

@tool
def web_search(query: str) -> str:
    """Search the web for information.
    
    Args:
        query: Search query string
    
    Returns:
        Search results
    """
    return DuckDuckGoSearchAPIWrapper().run(query)
    

@tool
def get_current_datetime() -> str:
    """Get current date and time.
    
    Returns:
        Current date and time in YYYY-MM-DD HH:MM:SS format
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@tool
def calculate_expression(expression: str) -> str:
    """Calculate a math expression.
    Args:
        expression: Math expression to calculate (e.g., 2+2, 10*5)
    Returns:
        Result of calculation
    """
    allowed_names = {"__builtins__": {}, "abs": abs, "round": round}
    result = eval(expression, allowed_names)
    return str(result)



tools=[web_search,calculate_expression,get_current_datetime]
llm_with_tools = llm.bind_tools(tools)



def chat_node(state:chatState):
  """Call tools instantly if needed. Respond beautifully using clear Markdown, headers, and bullet points. Greet the user warmly if they greet you. Keep sentences short and punchy.
"""
  messages = state['messages']
  # Ensure messages is always a list
  if not isinstance(messages, list):
    messages = [messages]

  # Include system instructions so the model knows how to use the tools correctly.
  messages = [system_prompt] + messages

  response = llm_with_tools.invoke(messages)
  return {"messages": [response]}



tool_node = ToolNode(tools)


graph = StateGraph(chatState)

graph.add_node("chat_node",chat_node)
graph.add_node('tools',tool_node)


graph.add_edge(START,"chat_node")
graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge("tools","chat_node")

_conn = psycopg.connect(DATABASE_URL, autocommit=True, row_factory=dict_row)
checkpointer = PostgresSaver(_conn)
checkpointer.setup()
chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
  all_threads = set()
  for checkpoint in checkpointer.list(None):
    all_threads.add(checkpoint.config['configurable']['thread_id'])
  return list(all_threads)