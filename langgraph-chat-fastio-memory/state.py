"""
State definition and configuration for Fast.io MCP memory chat.
"""
import os
from typing import TypedDict

from dotenv import load_dotenv

load_dotenv()


class MemoryChatState(TypedDict):
    query: str
    response: str
    history: list[dict]
    action: str
    memory_status: str


MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5.4-mini")

FASTIO_MCP_URL = os.getenv("FASTIO_MCP_URL", "https://mcp.fast.io/mcp")
FASTIO_MCP_TRANSPORT = os.getenv("FASTIO_MCP_TRANSPORT", "streamable_http")

MEMORY_WORKSPACE_NAME = os.getenv("FASTIO_MEMORY_WORKSPACE", "general")
MEMORY_FILE_NAME = os.getenv("FASTIO_MEMORY_FILE", "preferences.md")
