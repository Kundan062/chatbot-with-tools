import streamlit as st
from toolbackend import chatbot,retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid
 #== for generating unique thread id for new conversations

## ***********Utility Functions*********

def generate_thread_id():
  thread_id = uuid.uuid4()
  return thread_id

def reset_chat():
  thread_id = generate_thread_id()
  st.session_state['thread_id']=thread_id
  add_thread(st.session_state['thread_id'])
  st.session_state['message_history']=[]

def add_thread(thread_id):
  if thread_id not in st.session_state['chat_threads']:
    st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

#***********session setup ***********

if 'message_history' not in st.session_state:
  st.session_state['message_history']=[]

if 'thread_id' not in st.session_state:
  st.session_state['thread_id']=generate_thread_id()

if 'chat_threads' not in st.session_state:
  st.session_state['chat_threads']=retrieve_all_threads()


add_thread(st.session_state['thread_id'])


#***************** Side Bar UI***********

st.sidebar.title('LangGraph ChatBot')

if st.sidebar.button('New Chat'):
  reset_chat()

st.sidebar.header('My Conversations')

for thread_id in reversed(st.session_state['chat_threads']):
  if st.sidebar.button(str(thread_id)):
    st.session_state['thread_id']=thread_id
    messages = load_conversation(thread_id)

    temp_messages =[]

    for msg in messages:
        if isinstance(msg,HumanMessage):
          role='user'
        else:
          role = 'assistant'
        temp_messages.append({'role':role,'content':msg.content})
    st.session_state['message_history']=temp_messages

# ****************** Main UI***************
  config1 = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {
            "thread_id": st.session_state["thread_id"]
        },
        "run_name": "chat_turn",
    }



for message in st.session_state['message_history']:
  with st.chat_message(message['role']):
    st.text(message['content'])
user_input  = st.chat_input("Enter your query Sir")

if user_input:
  st.session_state['message_history'].append({'role':"user",'content':user_input})
  with st.chat_message("user"):
    st.text(user_input)


  # response = chatbot.invoke({'messages':[HumanMessage(content=user_input)]},config = config1)
  # ai_message = response['messages'][-1].content

  with st.chat_message("assistant"):
        # Use a mutable holder so the generator can set/modify it
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config1,
                stream_mode="messages",
            ):
                # Lazily create & update the SAME status container when any tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Finalize only if a tool was actually used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )

    # Save assistant message
  st.session_state["message_history"].append({"role": "assistant", "content": ai_message})