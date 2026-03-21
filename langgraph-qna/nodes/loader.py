"""
Loader node: reads .md and .txt files from a directory.
"""
import os
import logging

from state import QnAState

# Colors for output
COLOR_LOADER = '\033[96m'       # Cyan
COLOR_RESET = '\033[0m'         # Reset

logger = logging.getLogger(__name__)

SKIP_DIRS = {"venv", "__pycache__", ".git", "node_modules", ".venv"}


def loader(state: QnAState) -> QnAState:
    """Walk the doc_dir and load all .md and .txt files."""
    doc_dir = state["doc_dir"]
    documents = []
    total_chars = 0

    for root, dirs, files in os.walk(doc_dir):
        # Skip hidden and unwanted directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]

        for fname in sorted(files):
            if not fname.endswith((".md", ".txt")):
                continue
            path = os.path.join(root, fname)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            documents.append({
                "path": path,
                "filename": fname,
                "content": content,
                "line_count": content.count("\n") + 1,
            })
            total_chars += len(content)

    logger.info(
        "Documents loaded",
        extra={"file_count": len(documents), "total_chars": total_chars},
    )
    print(f"{COLOR_LOADER}[Loader]{COLOR_RESET}    Loaded {len(documents)} files ({total_chars:,} chars total)")

    return {**state, "documents": documents}
