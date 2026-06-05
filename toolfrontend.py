import streamlit as st
from toolbackend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid
from datetime import datetime

# ─────────────────────────────────────────────
# Page config  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LangGraph AI",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Global CSS
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    /* ── Root variables ── */
    :root {
        --bg:        #0d0f14;
        --surface:   #13161e;
        --border:    #1e2330;
        --accent:    #5cffe4;
        --accent2:   #ff6b6b;
        --text:      #e2e8f0;
        --muted:     #64748b;
        --user-bg:   #1a2540;
        --ai-bg:     #111520;
        --radius:    14px;
    }

    /* ── Base ── */
    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
        padding-top: 0 !important;
    }

    /* ── Hide default Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }

    /* ── Sidebar header ── */
    .sidebar-brand {
        padding: 24px 20px 16px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 8px;
    }
    .sidebar-brand h1 {
        font-family: 'Syne', sans-serif !important;
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        color: var(--accent) !important;
        letter-spacing: -0.03em;
        margin: 0 !important;
    }
    .sidebar-brand p {
        font-family: 'DM Mono', monospace !important;
        font-size: 0.65rem !important;
        color: var(--muted) !important;
        margin: 4px 0 0 !important;
        letter-spacing: 0.08em;
    }

    /* ── New Chat button ── */
    [data-testid="stSidebar"] .stButton:first-of-type > button {
        width: 100% !important;
        background: linear-gradient(135deg, #1a3a52, #0d2035) !important;
        border: 1px solid var(--accent) !important;
        color: var(--accent) !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.06em !important;
        border-radius: var(--radius) !important;
        padding: 10px 16px !important;
        margin: 8px 16px !important;
        width: calc(100% - 32px) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton:first-of-type > button:hover {
        background: linear-gradient(135deg, #1f4a68, #122840) !important;
        box-shadow: 0 0 20px rgba(92, 255, 228, 0.2) !important;
    }

    /* ── Thread buttons ── */
    [data-testid="stSidebar"] .stButton > button {
        width: calc(100% - 24px) !important;
        background: transparent !important;
        border: 1px solid var(--border) !important;
        color: var(--muted) !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.7rem !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        margin: 3px 12px !important;
        text-align: left !important;
        transition: all 0.15s ease !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        background: rgba(92,255,228,0.05) !important;
    }

    /* ── Sidebar section header ── */
    .sidebar-section {
        font-family: 'DM Mono', monospace;
        font-size: 0.6rem;
        letter-spacing: 0.12em;
        color: var(--muted);
        text-transform: uppercase;
        padding: 16px 20px 6px;
    }

    /* ── Main area ── */
    [data-testid="stMainBlockContainer"] {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* ── Page header ── */
    .page-header {
        padding: 28px 40px 20px;
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        gap: 14px;
        background: var(--surface);
    }
    .page-header .icon {
        font-size: 1.6rem;
        line-height: 1;
    }
    .page-header h2 {
        font-family: 'Syne', sans-serif !important;
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        color: var(--text) !important;
        margin: 0 !important;
    }
    .page-header span {
        font-family: 'DM Mono', monospace;
        font-size: 0.65rem;
        color: var(--muted);
        letter-spacing: 0.08em;
    }

    /* ── Chat container ── */
    .chat-wrapper {
        padding: 24px 40px;
        max-width: 860px;
        margin: 0 auto;
    }

    /* ── Message bubbles ── */
    .msg {
        display: flex;
        gap: 14px;
        margin-bottom: 20px;
        animation: fadeUp 0.25s ease both;
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .msg-avatar {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        flex-shrink: 0;
        margin-top: 2px;
    }
    .msg.user .msg-avatar  { background: var(--user-bg); border: 1px solid #2a3a60; }
    .msg.ai   .msg-avatar  { background: #0d1f1c;        border: 1px solid #1a3a30; }
    .msg-body { flex: 1; min-width: 0; }
    .msg-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.62rem;
        letter-spacing: 0.1em;
        color: var(--muted);
        margin-bottom: 6px;
        text-transform: uppercase;
    }
    .msg-text {
        background: var(--user-bg);
        border: 1px solid #1e2d50;
        border-radius: 4px 14px 14px 14px;
        padding: 12px 16px;
        font-size: 0.9rem;
        line-height: 1.65;
        color: var(--text);
        white-space: pre-wrap;
        word-break: break-word;
    }
    .msg.ai .msg-text {
        background: var(--ai-bg);
        border-color: var(--border);
        border-radius: 14px 4px 14px 14px;
    }

    /* ── Tool badge ── */
    .tool-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #111a10;
        border: 1px solid #2a4a25;
        border-radius: 20px;
        padding: 5px 12px;
        font-family: 'DM Mono', monospace;
        font-size: 0.7rem;
        color: #7eff78;
        margin-bottom: 8px;
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 80px 20px;
    }
    .empty-state .hex {
        font-size: 3.5rem;
        margin-bottom: 20px;
        filter: drop-shadow(0 0 30px rgba(92,255,228,0.3));
    }
    .empty-state h3 {
        font-family: 'Syne', sans-serif !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: var(--text) !important;
        margin-bottom: 10px !important;
    }
    .empty-state p {
        color: var(--muted);
        font-size: 0.9rem;
        max-width: 380px;
        margin: 0 auto 32px;
        line-height: 1.6;
    }
    .capability-grid {
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
        max-width: 480px;
        margin: 0 auto;
    }
    .cap-pill {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 7px 16px;
        font-size: 0.75rem;
        font-family: 'DM Mono', monospace;
        color: var(--muted);
        letter-spacing: 0.04em;
    }

    /* ── Chat input ── */
    [data-testid="stChatInput"] > div {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        transition: border-color 0.2s !important;
        color: black ;
    }
    [data-testid="stChatInput"] > div:focus-within {
        border-color: var(--accent) !important;
        color: black ;
        box-shadow: 0 0 0 3px rgba(92,255,228,0.08) !important;
    }
    [data-testid="stChatInputTextArea"] {
        color: black ;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stChatInputTextArea"]::placeholder {
        color: #888 !important;
    }
    [data-testid="stChatInputSubmitButton"] svg { fill: var(--accent) !important; }

    /* ── Status expander (tool running) ── */
    [data-testid="stExpander"] {
        background: #0c1a12 !important;
        border: 1px solid #1e3a22 !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────

def generate_thread_id() -> str:
    return str(uuid.uuid4())


def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []


def add_thread(thread_id: str):
    thread_id = str(thread_id)
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(thread_id: str):
    thread_id = str(thread_id)
    state = chatbot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )
    raw = state.values.get("messages", [])
    out = []
    for msg in raw:
        if isinstance(msg, HumanMessage):
            out.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage) and msg.content:
            out.append({"role": "assistant", "content": msg.content})
    return out


def short_id(tid: str) -> str:
    """Return a compact label for a thread id."""
    tid = str(tid)
    return f"⬡ {tid[:8]}…"


# ─────────────────────────────────────────────
# Session state bootstrap
# ─────────────────────────────────────────────
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = [str(t) for t in retrieve_all_threads()]

add_thread(st.session_state["thread_id"])

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <h1>⬡ LangGraph AI</h1>
            <p>POWERED BY GROQ · LLAMA 3.1</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("＋  New Conversation", key="new_chat"):
        reset_chat()
        st.rerun()

    st.markdown(
        '<div class="sidebar-section">Recent Threads</div>',
        unsafe_allow_html=True,
    )

    for tid in reversed(st.session_state["chat_threads"]):
        label = short_id(tid)
        if tid == st.session_state["thread_id"]:
            label = "▸ " + label          # mark active thread
        if st.button(label, key=f"thread_{tid}"):
            st.session_state["thread_id"] = tid
            st.session_state["message_history"] = load_conversation(tid)
            st.rerun()

# ─────────────────────────────────────────────
# LangGraph config
# ─────────────────────────────────────────────
config1 = {
    "configurable": {"thread_id": st.session_state["thread_id"]},
    "metadata": {"thread_id": st.session_state["thread_id"]},
    "run_name": "chat_turn",
}

# ─────────────────────────────────────────────
# Page header
# ─────────────────────────────────────────────
st.markdown(
    f"""
    <div class="page-header">
        <div class="icon">⬡</div>
        <div>
            <h2>LangGraph Chat</h2>
            <span>THREAD · {st.session_state["thread_id"][:16]}…</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Chat history or empty state
# ─────────────────────────────────────────────
st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

if not st.session_state["message_history"]:
    st.markdown(
        """
        <div class="empty-state">
            <div class="hex">⬡</div>
            <h3>What can I help with?</h3>
            <p>Ask me anything — I can search the web, crunch numbers,
               check the time, or just have a conversation.</p>
            <div class="capability-grid">
                <span class="cap-pill">🌐 Web Search</span>
                <span class="cap-pill">🧮 Calculator</span>
                <span class="cap-pill">🕐 Date & Time</span>
                <span class="cap-pill">💬 General Chat</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    for msg in st.session_state["message_history"]:
        role = msg["role"]
        content = msg["content"]
        if not content:
            continue

        if role == "user":
            st.markdown(
                f"""
                <div class="msg user">
                    <div class="msg-avatar">🧑</div>
                    <div class="msg-body">
                        <div class="msg-label">You</div>
                        <div class="msg-text">{content}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="msg ai">
                    <div class="msg-avatar">⬡</div>
                    <div class="msg-body">
                        <div class="msg-label">Assistant</div>
                        <div class="msg-text">{content}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Chat input & streaming
# ─────────────────────────────────────────────
user_input = st.chat_input("Ask me anything…")

if user_input:
    # Append user bubble immediately
    st.session_state["message_history"].append(
        {"role": "user", "content": user_input}
    )

    # Render user bubble
    st.markdown(
        f"""
        <div class="chat-wrapper">
        <div class="msg user">
            <div class="msg-avatar">🧑</div>
            <div class="msg-body">
                <div class="msg-label">You</div>
                <div class="msg-text">{user_input}</div>
            </div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Stream assistant response ──
    assistant_response = ""
    active_tools: list[str] = []

    with st.container():
        st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="msg ai">
                <div class="msg-avatar">⬡</div>
                <div class="msg-body">
                    <div class="msg-label">Assistant</div>
            """,
            unsafe_allow_html=True,
        )

        status_holder: dict = {"box": None}
        response_placeholder = st.empty()

        for message_chunk, metadata in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config1,
            stream_mode="messages",
        ):
            # ── Tool use indicator ──
            if isinstance(message_chunk, ToolMessage):
                tool_name = getattr(message_chunk, "name", "tool")
                if tool_name not in active_tools:
                    active_tools.append(tool_name)
                if status_holder["box"] is None:
                    status_holder["box"] = st.status(
                        f"🔧 Running `{tool_name}` …", expanded=True
                    )
                else:
                    status_holder["box"].update(
                        label=f"🔧 Running `{tool_name}` …",
                        state="running",
                        expanded=True,
                    )

            # ── Accumulate text ──
            if isinstance(message_chunk, AIMessage) and message_chunk.content:
                assistant_response += message_chunk.content
                response_placeholder.markdown(
                    f'<div class="msg-text">{assistant_response}▌</div>',
                    unsafe_allow_html=True,
                )

        # Finalise tool status
        if status_holder["box"] is not None:
            tools_used = ", ".join(f"`{t}`" for t in active_tools)
            status_holder["box"].update(
                label=f"✅ Used {tools_used}",
                state="complete",
                expanded=False,
            )

        # Final render (remove cursor)
        response_placeholder.markdown(
            f'<div class="msg-text">{assistant_response}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("</div></div></div>", unsafe_allow_html=True)

    # Persist
    st.session_state["message_history"].append(
        {"role": "assistant", "content": assistant_response}
    )