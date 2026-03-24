# LangGraph Chat + Fast.io MCP Memory — Plan

## Goal

Create a chat exercise that keeps long-term user memory in Fast.io via MCP.

## Core Behavior

1. On startup, bootstrap memory from Fast.io workspace/file.
2. During chat, read from memory when needed.
3. On memory instructions, write updates back to Fast.io.
4. Keep normal chat loop UX similar to `langgraph-chat`.

## Node Flow

- `bootstrap_memory` → `take_prompt`
- `take_prompt` routes:
  - normal prompt → `ask_agent` → `show_results` → `take_prompt`
  - `/list` → `list_history` → `take_prompt`
  - `/quit` or `quit` → `END`

## Configuration

- `OPENAI_API_KEY` (required)
- `FASTIO_API_KEY` (required)
- `FASTIO_MCP_URL` (default `https://mcp.fast.io/mcp`)
- `FASTIO_MCP_TRANSPORT` (default `streamable_http`)
- `FASTIO_MEMORY_WORKSPACE` (default `langgraph-chat-memory`)
- `FASTIO_MEMORY_FILE` (default `facts_and_preferences.md`)
