"""
State definition and configuration for the chat agent.
"""
from typing import TypedDict


class ChatState(TypedDict):
    """State passed between nodes in the chat graph."""
    query: str                          # current user question or refinement
    response: str                       # latest LLM response
    history: list[dict]                 # conversation turns [{query, response}, ...]
    action: str                         # user's chosen action (done/refine/summarize/list)
    summary: str                        # transient field for summary output


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_NAME = "gpt-4o-mini"              # LLM model to use for all nodes
