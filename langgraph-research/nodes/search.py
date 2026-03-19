"""
Search node: executes search queries.
"""
from state import ResearchState
from tools import search_web

# Colors for output
COLOR_SEARCH = '\033[94m'       # Blue
COLOR_RESET = '\033[0m'         # Reset


def search(state: ResearchState) -> ResearchState:
    """Runs the planned queries and appends results to state."""
    new_results = search_web(state["search_queries"])
    print(f"{COLOR_SEARCH}[Search]{COLOR_RESET}  Got {len(new_results)} new results")
    return {
        **state,
        "results": state["results"] + new_results,
        "iteration": state["iteration"] + 1,
    }
