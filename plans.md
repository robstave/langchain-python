# Roadmap & Learning Plan

This repo is a training ground for learning LangGraph and LangChain patterns.
The end goal is a local multi-agent personal assistant system — but to get there,
each exercise builds a specific skill that the real system will need.

---

## Purpose

> Build toward a personal multi-agent system that manages everyday life:
> todos, garden, fitness, recipes, collections, and finances.
> Each exercise below is a stepping stone toward that architecture.

---

## Phase 1 — Foundations ✅

These are implemented and working.

| Project | Key Skills Learned |
|---------|-------------------|
| `langgraph-research/` | Node-based graphs, conditional routing, iterative loops, Tavily search, state accumulation, user feedback, markdown export |
| `langgraph-qna/` | Local document loading, chunking, keyword retrieval, cited answers, multi-phase graph (load once, query many) |
| `langgraph-debate/` | Multiple LLM personas, round-based loops, structured output parsing, temperature tuning per agent, persona injection from files |

---

## Phase 2 — Core Skills 🔲

### Exercise 4 — Quiz Show (`langgraph-quiz/`)

**Goal:** A multi-node trivia game that produces interesting traces in LangGraph Studio.

**Why:** Teaches fan-out routing (one coordinator dispatching to multiple specialist nodes),
aggregating results, and scoring — patterns needed for a supervisor dispatching to
sub-agents.

**Design:**
- `host` node — picks a category, asks one of 5 specialist nodes to generate 3 questions
- Specialist nodes: `music`, `sports`, `history`, `literature`, `science`
- `scorer` node — evaluates answers and tallies scores
- 2 rounds, final score summary
- No external APIs — fully LLM-generated questions and answers
- Primary goal: produce a rich, branchy trace in LangGraph Studio to learn the UI

---

### Exercise 5 — Basic Chat Agent (`langgraph-chat/`) ✅

**Goal:** A conversational agent that maintains in-memory chat history across turns.

**Why:** Establishes the message history pattern used by almost every real agent.
Understanding `HumanMessage` / `AIMessage` lists and how to pass them through state
is foundational.

**Design:**
- Single node with a message list in state
- Loops back on each user turn
- `--topic` optional flag to set context (e.g., "cooking", "gardening")
- Colorful terminal output, structured logging already established

---

### Exercise 6 — Chat with Markdown Memory (`langgraph-chat-md/`)

**Goal:** Persist conversation history to a markdown file between sessions.

**Why:** Teaches external state persistence without a database. Also produces
a readable human log of every conversation — useful for personal assistant agents
that need a trail of what was discussed.

**Design:**
- Extends Exercise 5
- On session start: load previous history from `memory/<thread>.md`
- On each turn: append to the markdown log
- Markdown format: `## Session YYYY-MM-DD HH:MM`, then `**You:** / **Agent:**` pairs
- Multiple named "threads" selectable at startup (e.g., `--thread garden`)

---

### Exercise 7 — Persistent Multi-Thread Chat (`langgraph-chat-persist/`)

**Goal:** True multi-thread persistent memory using LangGraph's built-in checkpointing.

**Why:** LangGraph's `MemorySaver` / `SqliteSaver` checkpointers are the production
pattern for stateful agents. This exercise makes it concrete before it's needed in the
real system.

**Design:**
- Uses `langgraph.checkpoint.sqlite.SqliteSaver` (local, no server)
- Multiple named threads stored in `memory/chat.db`
- `--thread <name>` flag to pick or resume a conversation
- `--list` to show all saved threads with last message preview
- Demonstrates how the same graph can serve multiple independent conversation histories

---

### Exercise 8 — Vector RAG with PostgreSQL + pgvector (`langgraph-rag-pg/`)

**Goal:** Replace the langgraph-qna keyword retriever with real vector similarity search
backed by a local PostgreSQL + pgvector instance.

**Why:** The personal assistant agents (RecipeAgent, CollectorAgent, GardenGnome) all need
to search semi-structured notes and documents semantically, not just by keyword.
pgvector is self-hosted, free, and the production-grade path before considering
managed vector DBs.

**Design:**
- `embedder` node — calls OpenAI embeddings API, stores vectors in Postgres via `pgvector`
- `retriever` node — cosine similarity search, returns top-K chunks
- `answerer` node — same cited-answer pattern from langgraph-qna
- `ingest.py` — one-time script to chunk and embed docs into the DB
- `docker-compose.yml` — spins up `pgvector/pgvector:pg16` locally; no cloud needed
- Reuses the same `docs/` sample files from langgraph-qna for easy comparison
- Skills: OpenAI embeddings, pgvector SQL, connection pooling with `psycopg2`

---

### Exercise 9 — FastAPI Agent Server (`langgraph-api/`)

**Goal:** Expose a LangGraph agent as a REST API with per-session memory.

**Why:** The personal assistant will eventually need to be callable from other tools —
a phone, a home dashboard, a cron job. FastAPI is the standard Python path. This
exercise also demonstrates how HTTP becomes the session boundary for memory.

**Design:**
- FastAPI app with two endpoints:
  - `POST /chat` — `{ thread_id, message }` → `{ response }`
  - `GET /threads` — list active threads with last message
- Each `thread_id` maps to a separate LangGraph `SqliteSaver` checkpoint thread
- Returns streaming responses via `StreamingResponse` (learn SSE basics)
- `run.sh` starts uvicorn; a simple `test_client.py` exercises the endpoints
- Good target for a Lambda handler in the next exercise
- Skills: FastAPI, Pydantic request/response models, streaming, REST session management

---

### Exercise 10 — S3 Storage + AWS Lambda (`langgraph-aws/`)

**Goal:** Connect an agent to S3 for document storage, and wrap it in a Lambda handler
so the whole thing is invocable from AWS.

**Why:** The personal assistant agents need somewhere to store notes, images, and logs
that survives restarts and is accessible from anywhere. S3 is the simplest durable store.
A Lambda wrapper makes the agent a proper cloud function — callable from EventBridge
(scheduled nudges), API Gateway, or SNS.

**Design:**
- `s3_loader` node — pulls `.md` / `.txt` files from a configured S3 bucket prefix,
  replaces the local `docs/` folder from langgraph-qna
- `s3_writer` node — saves agent outputs (answers, notes) back to S3
- `lambda_handler.py` — thin wrapper: deserializes the Lambda event, runs the graph,
  returns a structured response; works with both API Gateway and direct invocation
- `deploy/` — minimal SAM/CDK template to package and deploy the Lambda
- Local testing via `aws lambda invoke` with `--endpoint-url http://localhost:3001`
  using AWS SAM CLI
- Skills: `boto3`, S3 get/put, Lambda event shapes, SAM local testing,
  IAM least-privilege role for S3 access

---

### Exercise 11 — MCP Cloud Memory Chat (`langgraph-chat-fastio-memory/`) ✅

**Goal:** Build a chat agent that persists user facts/preferences in cloud files via MCP
and reloads that memory at the start of every session.

**Why:** Teaches remote-tool memory patterns where the agent uses MCP to read/write durable
state instead of local files or local DB checkpointers.

**Design:**
- LangGraph loop similar to `langgraph-chat`
- Startup bootstrap node to initialize/read memory file
- Prompt conventions for `/remember`, `/recall`, and `/forget`
- Fast.io MCP connection (`https://mcp.fast.io/mcp`) via API key
- Memory stored as a durable markdown file in a dedicated workspace

---

## Phase 3 — Personal Assistant System 🔲

Once Phase 2 is complete, combine the learned patterns into a local multi-agent
personal system. Each agent is a LangGraph subgraph; a Supervisor routes queries.

```
                        ┌─────────────┐
                        │  Supervisor │
                        └──────┬──────┘
          ┌──────────┬─────────┼──────────┬──────────┬──────────┐
          ▼          ▼         ▼          ▼          ▼          ▼
      Planner    GardenGnome  Fitness   Recipe   Collector  Accountant
```

### Agents

| Agent | Responsibilities | Key Skills Needed |
|-------|-----------------|-------------------|
| **Supervisor** | Routes incoming requests to the right agent; synthesizes multi-agent responses | Fan-out routing (Quiz), multi-thread memory (Chat 3) |
| **Planner** | Tracks todos and ideas; proactively surfaces reminders, elevator pitches, next actions | Persistent memory (Chat 3), proactive scheduling |
| **GardenGnome** | Garden progress notes and image tracking; seasonal reminders; what-to-plant suggestions | Document storage (QnA patterns), image metadata |
| **FitnessAgent** | Logs workouts and metrics; tracks trends; motivates | Persistent memory, simple data viz summaries |
| **RecipeAgent** | Answers "what's for dinner?"; manages recipes; suggests meals based on pantry | Document retrieval (QnA patterns), user preference memory |
| **CollectorAgent** | Inventory of parts/components; proposes projects from available inventory | Document retrieval, structured data, project generation |
| **AccountantAgent** | Tracks bills, balances, tax reminders; spending summaries | Persistent state, scheduled nudges, structured data |

### Prerequisites Before Building Phase 3

- [ ] LangGraph Studio tracing in practice (Quiz exercise)
- [ ] Reliable multi-turn conversation history (Chat exercises 5–7)
- [ ] SQLite checkpointing working locally (Chat 3)
- [ ] Vector similarity search with pgvector (RAG exercise)
- [ ] FastAPI as a stateful agent server (API exercise)
- [ ] S3 read/write and Lambda invocation working (AWS exercise)
- [ ] Understand subgraph composition in LangGraph
- [ ] Decide on storage strategy per agent (SQLite / pgvector / S3 / JSON)

---

## Skills Checklist

| Skill | Learned In |
|-------|-----------|
| Node functions + StateGraph | Research ✅ |
| Conditional routing | Research ✅ |
| Iterative loops with termination | Research ✅, Debate ✅ |
| Multiple LLM personas | Debate ✅ |
| External file I/O (docs, export) | QnA ✅, Research ✅ |
| Structured output parsing | Debate ✅ |
| Fan-out to specialist nodes | Quiz 🔲 |
| LangGraph Studio / tracing | Quiz 🔲 |
| In-memory chat history | Chat 5 🔲 |
| Markdown-persisted memory | Chat 6 🔲 |
| SQLite checkpointing + threads | Chat 7 🔲 |
| OpenAI embeddings + pgvector | RAG 🔲 |
| Vector similarity search (SQL) | RAG 🔲 |
| FastAPI + streaming responses | API 🔲 |
| REST session / thread management | API 🔲 |
| boto3 S3 read/write | AWS 🔲 |
| Lambda handler + SAM local | AWS 🔲 |
| MCP remote tool integration | MCP Chat ✅ |
| Cloud file memory via MCP | MCP Chat ✅ |
| Supervisor + subgraph routing | Phase 3 🔲 |
| Proactive / scheduled agents | Phase 3 🔲 |



other
---------

https://github.com/aws-samples/sample-mcp-server-s3/tree/main