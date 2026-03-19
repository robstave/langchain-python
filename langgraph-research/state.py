"""
State definition and configuration for the research agent.
"""
from typing import TypedDict


class ResearchState(TypedDict):
    """State passed between nodes in the research graph."""
    query: str                          # original user question
    search_queries: list[str]           # queries the planner wants to run
    results: list[dict]                 # accumulated search results
    iteration: int                      # how many search rounds we've done
    final_answer: str                   # written by synthesizer at the end
    _enough: bool                       # whether we have enough info to synthesize


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_NAME = "gpt-5.4-nano"             # LLM model to use for all nodes
MAX_ITERATIONS = 3                      # safety cap on search loops
MIN_RESULTS = 6                         # minimum results before considering done
LLM_EVALUATION = True                   # use LLM to evaluate or just iteration count
