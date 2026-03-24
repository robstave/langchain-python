#!/usr/bin/env python3
"""
LangGraph Chat + Fast.io MCP memory (entry point).
"""
import asyncio
import os

from dotenv import load_dotenv

from graph import build_graph
from state import MemoryChatState


def _validate_env() -> None:
    missing = []
    for key in ("OPENAI_API_KEY", "FASTIO_API_KEY"):
        if not os.getenv(key):
            missing.append(key)
    if missing:
        keys = ", ".join(missing)
        raise RuntimeError(f"Missing required environment variable(s): {keys}")


async def main():
    load_dotenv()
    _validate_env()

    app = build_graph()

    print(f"\n{'═' * 60}")
    print("  LangGraph Chat + Fast.io MCP Memory")
    print("  Persistent facts/preferences across sessions")
    print(f"{'═' * 60}")
    print("Tips:")
    print("  /remember <text>  -> store fact/preference")
    print("  /recall or /memory -> recall saved memory")
    print("  /forget <text>    -> remove/mark a memory item")
    print("  /list             -> show conversation history")
    print("  /quit or quit     -> end session")
    print(f"{'═' * 60}")

    initial_state: MemoryChatState = {
        "query": "",
        "response": "",
        "history": [],
        "action": "",
        "memory_status": "",
    }

    config = {"configurable": {"thread_id": "fastio-memory-chat"}}
    await app.ainvoke(initial_state, config=config)


if __name__ == "__main__":
    asyncio.run(main())
