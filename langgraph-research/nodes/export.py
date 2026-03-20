"""
Export node: saves the final answer to a well-formatted Markdown file.
"""
import os
from datetime import datetime

from state import ResearchState

# Colors for output
COLOR_EXPORT = '\033[93m'       # Yellow
COLOR_RESET = '\033[0m'         # Reset

ANSWERS_DIR = "answers"


def export_markdown(state: ResearchState) -> ResearchState:
    """Writes the final answer to a timestamped Markdown file."""
    os.makedirs(ANSWERS_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Build a short slug from the question (first few words)
    slug = "_".join(state["query"].split()[:5]).lower()
    slug = "".join(c for c in slug if c.isalnum() or c == "_")
    filename = f"{ANSWERS_DIR}/{timestamp}_{slug}.md"

    # Collect unique sources in citation order
    sources = []
    seen = set()
    for r in state["results"]:
        if r["url"] not in seen:
            seen.add(r["url"])
            sources.append(r)

    # Build the markdown document
    lines = [
        f"# {state['query']}",
        "",
        f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} "
        f"| {state['iteration']} search iteration(s) "
        f"| {len(state['results'])} results gathered*",
        "",
        "---",
        "",
        state["final_answer"],
        "",
        "---",
        "",
        "## Sources",
        "",
    ]
    for i, r in enumerate(sources, 1):
        lines.append(f"{i}. [{r['title']}]({r['url']})")

    lines.append("")  # trailing newline

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"{COLOR_EXPORT}[Export]{COLOR_RESET}   Saved to {filename}")
    return state
