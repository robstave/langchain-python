"""
Search node: executes search queries with deduplication.
"""
import logging
from state import ResearchState
from tools import search_web

# Colors for output
COLOR_SEARCH = '\033[94m'       # Blue
COLOR_RESET = '\033[0m'         # Reset

logger = logging.getLogger(__name__)


def search(state: ResearchState) -> ResearchState:
    """Runs the planned queries and appends deduplicated results to state."""
    raw_results = search_web(state["search_queries"])
    seen_urls = set(state["seen_urls"])

    new_results = []
    for r in raw_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            new_results.append(r)

    dupes = len(raw_results) - len(new_results)
    dupe_msg = f" ({dupes} duplicates skipped)" if dupes else ""
    print(f"{COLOR_SEARCH}[Search]{COLOR_RESET}  Got {len(new_results)} new results{dupe_msg}")

    logger.info(
        "Search completed",
        extra={
            "iteration": state["iteration"] + 1,
            "new_results": len(new_results),
            "duplicates_skipped": dupes,
            "result_count": len(state["results"]) + len(new_results),
        }
    )

    return {
        **state,
        "results": state["results"] + new_results,
        "seen_urls": seen_urls,
        "iteration": state["iteration"] + 1,
    }
