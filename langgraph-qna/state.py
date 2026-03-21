"""
State definition and configuration for the document Q&A pipeline.
"""
from typing import TypedDict


class QnAState(TypedDict):
    """State passed between nodes in the Q&A graph."""
    question: str                       # user's question
    doc_dir: str                        # path to documents directory
    documents: list[dict]               # loaded docs: {path, filename, content, line_count}
    chunks: list[dict]                  # {source, filename, chunk_id, text, start_line, end_line}
    relevant_chunks: list[dict]         # chunks selected by retriever
    answer: str                         # final answer with citations


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_NAME = "gpt-5.4-mini"            # LLM model for answering
DOC_DIR = "docs"                        # default directory to load documents from
CHUNK_SIZE = 500                        # target characters per chunk
CHUNK_OVERLAP = 50                      # overlap characters between chunks
RETRIEVAL_MODE = "keyword"              # "stuff" (all chunks) or "keyword" (top-K)
TOP_K = 5                               # chunks to retrieve in keyword mode
