# RAG Agent with Long-Term Memory

An end-to-end Retrieval-Augmented Generation (RAG) system combined with a tool-using, memory-persistent agent, built with LangGraph and exposed as a REST API with FastAPI.

The agent can answer questions using a local knowledge base (Markdown documents), search the web when local knowledge isn't enough, remember facts about the user across conversations, avoid repeating expensive lookups for questions it has already answered, and automatically summarize long conversations to control token usage.

## Features

- **Hybrid retrieval**: combines dense (semantic) and sparse (BM25 keyword) search with Reciprocal Rank Fusion (RRF) for more accurate document retrieval.
- **Tool-using agent**: dynamically decides whether to query the local knowledge base, search the web, or answer directly from its own knowledge.
- **Short-term memory**: full conversation history persisted per thread via a LangGraph checkpointer.
- **Long-term memory**:
  - **User profile**: stable facts about the user (name, age, role), incrementally extracted and updated with Trustcall, persisted across all conversations regardless of thread.
  - **Semantic memory**: question/answer pairs stored and retrieved by meaning, so previously answered questions are served from memory instead of triggering new tool calls or LLM generations.
- **Automatic summarization**: conversations exceeding a message threshold are summarized and trimmed to keep the context window small.
- **REST API**: chat and document-ingestion endpoints with request validation, structured error handling, and interactive documentation.
- **Remote access**: the API can be tunneled with ngrok for testing from any device.

## Architecture

```
User message
     |
     v
[check_memory] --(match found)--> respond from memory --> [update_profile] --> END
     |
     (no match)
     v
[assistant] <--(tool call)--> [tools: call_rag | web_search]
     |
     (final answer)
     v
[update_memory] --> [update_profile] --> [summarizer] --> END
```

- **check_memory**: embeds the incoming question and searches long-term memory for a semantically similar, previously answered question. If a strong match is found, the stored answer is returned directly, skipping the LLM and any tool calls.
- **assistant**: the core LLM node (Gemini), aware of the user's profile and the running conversation summary, capable of invoking tools.
- **tools**: `call_rag` (queries the local Qdrant knowledge base) and `web_search` (queries Tavily via MCP).
- **update_memory**: stores the new question/answer pair in long-term memory for future reuse.
- **update_profile**: extracts and merges any new personal information the user shared, using Trustcall for incremental, non-destructive updates.
- **summarize_conversation**: once the conversation grows past a threshold, older messages are summarized into a running summary and removed from the active state.

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph |
| LLM | Google Gemini (`gemini-3.5-flash-lite`) |
| Embeddings | Google Gemini (`gemini-embedding-001`, 3072 dimensions) |
| Vector store | Qdrant (hybrid dense + BM25 sparse search) |
| Structured extraction | Trustcall |
| Web search | Tavily, integrated via MCP (Model Context Protocol) |
| API framework | FastAPI |
| Environment & dependency management | uv |

## Project Structure

```
.
├── ingestion/
│   ├── chunking.py       # Header-based Markdown chunking with a size-based fallback
│   ├── embedding.py      # Embedding generation via the Gemini API
│   └── vectorstore.py    # Qdrant collection management and point upserts
├── retrieval/
│   └── search.py         # Hybrid (dense + BM25) search with RRF fusion
├── brain/
│   └── graph.py              # Graph construction and compilation
│   └── resources/
│       ├── llm.py             # LLM and MCP client configuration
│       ├── profile.py          # User profile schema, Trustcall extractor, and update node
│       ├── memory.py           # Long-term semantic memory schema, search, and update nodes
│       ├── tools.py             # Agent tools (RAG lookup, web search)
│       ├── prompts.py           # System prompt and sumarization prompts
│       └── web_mcp_server.py     # MCP server exposing the Tavily web search tool
├── docs/                      # Markdown knowledge base ingested into the vector store
├── main.py                    # FastAPI application
└── .env                        # API keys (not committed)
```

## Development Phases

This project was built incrementally, validating each layer before building on top of it:

1. **Ingestion**: Markdown chunking, embedding generation, and storage in Qdrant.
2. **Retrieval**: hybrid dense + BM25 search with RRF fusion.
3. **Agent**: built up in stages — a basic LangGraph agent, tool integration (RAG + web search via MCP), short-term memory, long-term profile memory, long-term semantic memory with duplicate-question detection, and conversation summarization.
4. **API**: FastAPI endpoints wrapping the agent and the ingestion pipeline, with structured error handling.
5. **Remote access**: exposing the local API through an ngrok tunnel.

## Prerequisites

- Python 3.13+, managed with [uv](https://docs.astral.sh/uv/)
- [Docker](https://www.docker.com/), for running Qdrant locally
- A [Google Gemini API key](https://ai.google.dev/)
- A [Tavily API key](https://tavily.com/)
- [ngrok](https://ngrok.com/), for exposing the API remotely (optional)

## Setup

1. Clone the repository and install dependencies:

```bash
git clone <this-repo-url>
cd <project-folder>
uv sync
```

2. Create a `.env` file in the project root with your API keys:

```
GEMINI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

## Running the Project

### 1. Start Qdrant

```bash
docker run -d -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant
```

Verify it's running at `http://localhost:6333/dashboard`.

### 2. Start the API

```bash
uv run uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive documentation (Swagger UI) is available at `http://127.0.0.1:8000/docs`.

### 3. (Optional) Expose the API remotely with ngrok

```bash
ngrok http 8000
```

This prints a public HTTPS URL that forwards to your local server, allowing access from any device, including mobile.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/chat` | Send a message to the agent. Requires a `thread_id` to maintain conversation state. |
| `POST` | `/documents` | Upload a `.md` file to trigger chunking, embedding, and ingestion into the knowledge base. |

## Possible Future Improvements

- Reranking step after hybrid retrieval, for improved precision on the top results.
- Evaluation of retrieval quality using frameworks such as RAGAS.
- Endpoints to list and delete ingested documents by source.
- Exploring typed decision models (e.g., Jev) for cheaper, faster tool-routing and memory-match gating decisions.
- Deployment to a managed cloud environment (e.g., GCP Cloud Run) for persistent, production-grade hosting.
