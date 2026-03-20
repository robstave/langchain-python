"""
State definition and configuration for the research agent.
"""
from typing import TypedDict


class ResearchState(TypedDict):
    """State passed between nodes in the research graph."""
    query: str                          # original user question
    search_queries: list[str]           # queries the planner wants to run
    results: list[dict]                 # accumulated search results
    seen_urls: set[str]                 # URLs already collected (for dedup)
    iteration: int                      # how many search rounds we've done
    final_answer: str                   # written by synthesizer at the end
    _enough: bool                       # whether we have enough info to synthesize
    feedback_hint: str                  # user feedback for planner (empty = none)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# MODEL_NAME = "gpt-5.4-nano"             # LLM model to use for all nodes
MODEL_NAME = "gpt-5.4-mini"             # LLM model to use for all nodes

MAX_ITERATIONS = 3                      # safety cap on search loops
MIN_RESULTS = 6                         # minimum results before considering done
LLM_EVALUATION = True                   # use LLM to evaluate or just iteration count
