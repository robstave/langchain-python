"""
Chunker node: splits documents into overlapping chunks with line tracking.
"""
import logging

from state import QnAState, CHUNK_SIZE, CHUNK_OVERLAP

# Colors for output
COLOR_CHUNKER = '\033[93m'      # Yellow
COLOR_RESET = '\033[0m'         # Reset

logger = logging.getLogger(__name__)


def chunker(state: QnAState) -> QnAState:
    """Split each document into overlapping chunks, tracking line numbers."""
    all_chunks = []

    for doc in state["documents"]:
        lines = doc["content"].splitlines(keepends=True)
        chunks = _chunk_lines(lines, doc["filename"], doc["path"])
        all_chunks.extend(chunks)

    logger.info(
        "Chunks created",
        extra={
            "chunk_count": len(all_chunks),
            "file_count": len(state["documents"]),
        },
    )
    print(
        f"{COLOR_CHUNKER}[Chunker]{COLOR_RESET}   "
        f"Created {len(all_chunks)} chunks from {len(state['documents'])} files"
    )

    return {**state, "chunks": all_chunks}


def _chunk_lines(lines: list[str], filename: str, path: str) -> list[dict]:
    """
    Build chunks from lines of text.

    Strategy: accumulate lines until CHUNK_SIZE is reached, then start a new
    chunk with CHUNK_OVERLAP characters of overlap from the previous chunk.
    """
    chunks = []
    chunk_id = 0
    i = 0  # current line index

    while i < len(lines):
        chunk_text = ""
        start_line = i + 1  # 1-indexed

        # Accumulate lines up to CHUNK_SIZE
        while i < len(lines) and len(chunk_text) < CHUNK_SIZE:
            chunk_text += lines[i]
            i += 1

        end_line = i  # 1-indexed inclusive

        chunks.append({
            "source": path,
            "filename": filename,
            "chunk_id": chunk_id,
            "text": chunk_text.strip(),
            "start_line": start_line,
            "end_line": end_line,
        })
        chunk_id += 1

        # Back up for overlap
        if i < len(lines):
            overlap_chars = 0
            while i > 0 and overlap_chars < CHUNK_OVERLAP:
                i -= 1
                overlap_chars += len(lines[i])

    return chunks
