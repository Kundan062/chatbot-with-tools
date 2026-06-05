# ⬡ LangGraph AI Chatbot

A production-ready **agentic AI chatbot** built with LangGraph, Groq (gpt-oss-120b), and Streamlit — featuring real-time tool use, persistent multi-session memory via PostgreSQL, and a fully custom dark-mode UI.

> Not just a chatbot. An agent that reasons, uses tools, and remembers.

---


## ✨ Features

- 🧠 **Agentic Reasoning** — LangGraph `StateGraph` with conditional tool routing; the model decides when and which tool to call
- ⚡ **Groq Inference** — Ultra-fast gpt-oss-120b responses via Groq API
- 🌐 **Web Search** — Real-time DuckDuckGo search for current information
- 🧮 **Calculator** — Evaluates math expressions on the fly
- 🕐 **Date & Time** — Always knows the current datetime
- 💾 **Persistent Memory** — PostgreSQL checkpointing saves every conversation; resume any thread anytime
- 🎨 **Custom UI** — Fully styled Streamlit interface with thread management, live streaming, and dark mode

---

## 🏗️ Architecture

```
User Input
    │
    ▼
┌─────────────┐
│  chat_node  │  ←──────────────────────┐
│  (LLM)      │                         │
└──────┬──────┘                         │
       │                                │
  tools_condition                       │
  (needs tool?)                         │
       │                                │
   YES │          NO                    │
       ▼          ▼                     │
┌─────────────┐  END              ┌─────────────┐
│  tool_node  │ ─────────────────►│  chat_node  │
│  (executor) │                   │  (with tool │
└─────────────┘                   │   result)   │
                                  └─────────────┘
```

**LangGraph handles the loop automatically** — the agent calls a tool, gets the result, and continues reasoning until it has a final answer.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Agent Framework | [LangGraph](https://github.com/langchain-ai/langgraph) |
| LLM | gpt-oss-120b via [Groq](https://groq.com/) |
| Memory / Checkpointing | PostgreSQL + `PostgresSaver` |
| Web Search | DuckDuckGo (`langchain_community`) |
| Frontend | [Streamlit](https://streamlit.io/) |
| Language | Python 3.10+ |

---

## 📁 Project Structure

```
├── app.py               # Streamlit frontend — UI, chat rendering, session management
├── toolbackend.py       # LangGraph graph, tools, LLM, PostgreSQL checkpointer
├── .env                 # Environment variables (not committed)
├── requirements.txt     # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/langgraph-ai-chatbot.git
cd langgraph-ai-chatbot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root:

```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/your_db_name
```

- Get a free Groq API key at [console.groq.com](https://console.groq.com)
- Set up a PostgreSQL database locally or use a hosted provider like [Supabase](https://supabase.com/) or [Neon](https://neon.tech/)

### 4. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🧰 Available Tools

| Tool | Description |
|---|---|
| `web_search(query)` | Searches the web via DuckDuckGo for real-time information |
| `calculate_expression(expression)` | Safely evaluates math expressions (e.g. `2 ** 10`, `round(3.14159, 2)`) |
| `get_current_datetime()` | Returns the current date and time |

Adding a new tool is as simple as decorating a function with `@tool` and appending it to the `tools` list.

---

## 💡 How It Works

1. User sends a message → goes into LangGraph `StateGraph` as a `HumanMessage`
2. `chat_node` invokes the LLM (with tools bound)
3. LangGraph checks `tools_condition` — if the model called a tool, route to `tool_node`
4. `tool_node` executes the tool and returns a `ToolMessage`
5. Control loops back to `chat_node` with the result
6. When no more tools are needed, the final `AIMessage` is streamed to the UI
7. The full conversation state is checkpointed to PostgreSQL after every turn

---

## 📦 Requirements

```
streamlit
langchain
langchain-groq
langchain-community
langgraph
psycopg[binary]
python-dotenv
duckduckgo-search
```

Install `requirements.txt` with:

```bash
pip install -r requirements.txt
```

---

## 🔮 Roadmap

- [ ] Add more tools (Wikipedia, weather, code execution)
- [ ] Multi-user authentication
- [ ] Deploy to cloud (Railway / Render / Vercel)
- [ ] Conversation export (PDF / Markdown)
- [ ] Voice input support

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---


## 👤 Author

**Your Name**
- LinkedIn: [linkedin.com/in/your-profile](https://linkedin.com/in/your-profile)
- GitHub: [@your-username](https://github.com/your-username)

---

*Built with ❤️ using LangGraph, Groq, and Streamlit*
