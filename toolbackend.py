from langchain_groq import ChatGroq
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_core.tools import tool
from datetime import datetime


load_dotenv()
llm = ChatGroq(model = "llama-3.1-8b-instant")
# llm2 = ChatGroq(model = "llama-3.3-70b-versatile")
#-------TOOOLSS----------------
@tool
def web_search(query: str) -> str:
    """Search the web for a given query string to find live or current information."""
    search = DuckDuckGoSearchRun()
    return search.run(query)

@tool
def get_current_datetime()->str:
  """Returns the current date and time.Always Use this when there is mention of any time realted things like 'today','tommorow',or 'schedule',time or date"""
  return f"The current date and time is: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

@tool
def calculate_expression(expression: str) -> str:
    """Evaluates a basic mathematical expression safely. Use this whenever the user asks for math or calculations."""
    try:
        # Using a restricted dictionary for safe evaluation of basic math
        allowed_names = {"__builtins__": None, "abs": abs, "round": round}
        result = eval(expression, allowed_names, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"



tools=[web_search,calculate_expression,get_current_datetime]
llm_with_tools = llm.bind_tools(tools)

class chatState(TypedDict):
  messages:Annotated[list[BaseMessage],add_messages]



def chat_node(state:chatState):
  """LLM Node that may answer or request a tool call.And It always Provide a Very structured and Beatiful response"""
  messages = state['messages']
  response = llm_with_tools.invoke(messages)
  return {"messages":[response]}

# def structured(state: chatState) -> chatState:
#     """
#     Enhances raw conversation output into a structured, professional,
#     and user-friendly response.
#     """

#     # Extract message history
#     messages = state.get("messages", [])

#     # Convert messages into readable text
#     conversation_history = "\n".join(
#         [
#             f"{msg.type.upper()}: {msg.content}"
#             if hasattr(msg, "content")
#             else str(msg)
#             for msg in messages
#         ]
#     )

#     # Professional structuring prompt
#     prompt = f"""
# You are a senior AI communication expert.

# Your task is to transform the message into a highly structured,
# professional, polished, and easy-to-read response.
# Message:
# {state['messages']}
# """

#     # Invoke secondary LLM
#     response = llm2.invoke(prompt)

#     # Return updated state
#     return {"messages": [response]}

tool_node = ToolNode(tools)

conn=sqlite3.connect(database='chatbot.db',check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(chatState)

graph.add_node("chat_node",chat_node)
graph.add_node('tools',tool_node)
# graph.add_node('structured',structured)


graph.add_edge(START,"chat_node")
graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge("tools","chat_node")
# graph.add_edge("chat_node","structured")

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
  all_threads = set()
  for checkpoint in checkpointer.list(None):
    all_threads.add(checkpoint.config['configurable']['thread_id'])
  return list(all_threads)