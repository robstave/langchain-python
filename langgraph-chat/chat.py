"""
LangGraph Chat Agent
--------------------
An interactive conversational chatbot that:
  1. Takes a user question
  2. Asks the LLM (with full conversation history for context)
  3. Shows the response
  4. Offers choices: Done, Refine, Summarize, List conversation
  5. Refine loops back to the LLM with the follow-up question
  6. Summarize produces an LLM summary of the full conversation
  7. List displays all conversation turns

Uses langgraph.checkpoint.memory.MemorySaver for in-memory state.

Install deps:
    pip install langgraph langchain-community langchain-openai python-dotenv

Set env vars (or create a .env file):
    OPENAI_API_KEY=...
"""

import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_community.callbacks import get_openai_callback

from state import ChatState
from graph import build_graph

# Load environment variables from .env file
load_dotenv()

# Colors for terminal output
COLOR_TOKENS = '\033[91m'       # Red
COLOR_RESET = '\033[0m'         # Reset


# Configure structured logging
class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logs."""
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Include extra fields if present
        if hasattr(record, 'turn'):
            log_data["turn"] = record.turn
        if hasattr(record, 'query_length'):
            log_data["query_length"] = record.query_length
        if hasattr(record, 'response_length'):
            log_data["response_length"] = record.response_length
        if hasattr(record, 'turns'):
            log_data["turns"] = record.turns
        if hasattr(record, 'summary_length'):
            log_data["summary_length"] = record.summary_length
        return json.dumps(log_data)


def setup_logging():
    """Configure logging to write structured logs to file."""
    os.makedirs("logs", exist_ok=True)

    file_handler = logging.FileHandler(
        f"logs/chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    file_handler.setFormatter(StructuredFormatter())
    file_handler.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    agent = build_graph()

    print(f"\n{'═' * 60}")
    print(f"  LangGraph Chat Agent")
    print(f"  Type your question, then refine or explore the conversation.")
    print(f"{'═' * 60}")

    logger.info("Chat session started")

    initial_state: ChatState = {
        "query": "",
        "response": "",
        "history": [],
        "action": "",
        "summary": "",
    }

    # MemorySaver requires a thread_id in the config
    config = {"configurable": {"thread_id": "chat-1"}}

    # Track token usage and cost
    with get_openai_callback() as cb:
        final_state = agent.invoke(initial_state, config=config)

        # Display token usage
        print(f"\n{'─' * 60}")
        print(f"{COLOR_TOKENS}Token Usage:{COLOR_RESET}")
        print(f"{COLOR_TOKENS}  Total Tokens: {cb.total_tokens:,}{COLOR_RESET}")
        print(f"{COLOR_TOKENS}  Prompt Tokens: {cb.prompt_tokens:,}{COLOR_RESET}")
        print(f"{COLOR_TOKENS}  Completion Tokens: {cb.completion_tokens:,}{COLOR_RESET}")
        print(f"{COLOR_TOKENS}  Total Cost: ${cb.total_cost:.4f}{COLOR_RESET}")
        print(f"{'─' * 60}")

        logger.info(
            "Chat session ended",
            extra={
                "total_turns": len(final_state["history"]),
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost": cb.total_cost,
            }
        )
