"""
LangGraph Document Q&A Pipeline
--------------------------------
Loads local documents, chunks them, and answers questions
with citations back to source file and line number.

Install deps:
    pip install langgraph langchain-openai python-dotenv

Set env vars (or create a .env file):
    OPENAI_API_KEY=...

Configuration:
    Edit state.py to configure:
    - MODEL_NAME: LLM model to use
    - DOC_DIR: directory to load documents from
    - CHUNK_SIZE / CHUNK_OVERLAP: chunking parameters
    - RETRIEVAL_MODE: "stuff" or "keyword"
    - TOP_K: number of chunks in keyword mode
"""

import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_community.callbacks import get_openai_callback

from state import QnAState, DOC_DIR
from graph import build_graph, build_question_graph

# Load environment variables from .env file
load_dotenv()

# Colors for terminal output
COLOR_ANSWER = '\033[97m'       # Bright white
COLOR_TOKENS = '\033[91m'       # Red
COLOR_PROMPT = '\033[94m'       # Blue
COLOR_RESET = '\033[0m'         # Reset


# ---------------------------------------------------------------------------
# Structured logging (same pattern as langgraph-research)
# ---------------------------------------------------------------------------

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logs."""
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Include any extra fields
        for key in ("file_count", "total_chars", "chunk_count",
                     "selected", "total", "mode", "chunks_used",
                     "answer_length", "question"):
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
        return json.dumps(log_data)


def setup_logging():
    """Configure logging to write structured logs to file."""
    os.makedirs("logs", exist_ok=True)
    file_handler = logging.FileHandler(
        f"logs/qna_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    file_handler.setFormatter(StructuredFormatter())
    file_handler.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    # --- Phase 1: Load and chunk documents (once) ---
    print(f"{'─' * 60}")
    print(f"Loading documents from: {DOC_DIR}/")
    print(f"{'─' * 60}")

    initial_state: QnAState = {
        "question": "",
        "doc_dir": DOC_DIR,
        "documents": [],
        "chunks": [],
        "relevant_chunks": [],
        "answer": "",
    }

    load_graph = build_graph()
    question_graph = build_question_graph()

    # Run the full pipeline once with a dummy question to load + chunk
    # We'll use a real question to also get an answer on the first pass
    print()
    question = input(f"{COLOR_PROMPT}Ask a question (or 'quit' to exit): {COLOR_RESET}").strip()
    if not question:
        question = "What is a list comprehension?"

    initial_state["question"] = question

    with get_openai_callback() as cb:
        state = load_graph.invoke(initial_state)

        print(f"\n{'─' * 60}")
        print(f"{COLOR_ANSWER}{state['answer']}{COLOR_RESET}")
        print(f"{'─' * 60}")

        logger.info("Question answered", extra={"question": question})

    # --- Phase 2: Interactive question loop (reuses chunks) ---
    while True:
        print()
        question = input(f"{COLOR_PROMPT}Ask another question (or 'quit' to exit): {COLOR_RESET}").strip()

        if not question or question.lower() in ("quit", "exit", "q"):
            break

        # Reuse the loaded docs/chunks, just swap the question
        follow_up_state: QnAState = {
            **state,
            "question": question,
            "relevant_chunks": [],
            "answer": "",
        }

        with get_openai_callback() as cb:
            state = question_graph.invoke(follow_up_state)

            print(f"\n{'─' * 60}")
            print(f"{COLOR_ANSWER}{state['answer']}{COLOR_RESET}")
            print(f"{'─' * 60}")

            logger.info("Question answered", extra={"question": question})

    print("\nDone!")
