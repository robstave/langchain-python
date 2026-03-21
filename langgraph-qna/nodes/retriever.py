"""
Retriever node: selects relevant chunks for the question.

Two modes:
  - "stuff": pass all chunks (works for small corpus)
  - "keyword": score chunks by keyword overlap, return top-K
"""
import logging
import re

from state import QnAState, RETRIEVAL_MODE, TOP_K

# Colors for output
COLOR_RETRIEVER = '\033[95m'    # Magenta
COLOR_RESET = '\033[0m'         # Reset

logger = logging.getLogger(__name__)

# Common words to ignore when scoring
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "about", "between",
    "through", "after", "before", "above", "below", "and", "or", "but",
    "not", "no", "if", "then", "than", "so", "that", "this", "it", "its",
    "what", "which", "who", "how", "when", "where", "why", "i", "me", "my",
}


def retriever(state: QnAState) -> QnAState:
    """Select relevant chunks based on the configured retrieval mode."""
    chunks = state["chunks"]

    if not chunks:
        print(f"{COLOR_RETRIEVER}[Retriever]{COLOR_RESET} No chunks to search")
        return {**state, "relevant_chunks": []}

    if RETRIEVAL_MODE == "stuff":
        selected = chunks
        mode_label = "stuff"
    else:
        selected = _keyword_retrieve(state["question"], chunks)
        mode_label = "keyword"

    logger.info(
        "Chunks retrieved",
        extra={
            "selected": len(selected),
            "total": len(chunks),
            "mode": mode_label,
        },
    )
    print(
        f"{COLOR_RETRIEVER}[Retriever]{COLOR_RESET} "
        f"Selected {len(selected)}/{len(chunks)} chunks ({mode_label} mode)"
    )

    return {**state, "relevant_chunks": selected}


def _extract_keywords(text: str) -> set[str]:
    """Extract meaningful words from text, filtering stop words."""
    words = set(re.findall(r"[a-z0-9]+", text.lower()))
    return words - STOP_WORDS


def _keyword_retrieve(question: str, chunks: list[dict]) -> list[dict]:
    """Score chunks by keyword overlap with the question, return top-K."""
    keywords = _extract_keywords(question)

    if not keywords:
        return chunks[:TOP_K]

    scored = []
    for chunk in chunks:
        chunk_words = _extract_keywords(chunk["text"])
        overlap = len(keywords & chunk_words)
        if overlap > 0:
            scored.append((overlap, chunk))

    # Sort by score descending, take top-K
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:TOP_K]]
