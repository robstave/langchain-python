"""
LangGraph Research Orchestration Agent
--------------------------------------
A multi-step research agent that:
  1. Plans what to search for
  2. Searches the web (via Tavily)
  3. Evaluates if it has enough info
  4. Loops back to search more if needed
  5. Synthesizes a final cited answer

Install deps:
    pip install langgraph langchain-community langchain-openai tavily-python python-dotenv

Set env vars (or create a .env file):
    OPENAI_API_KEY=...
    TAVILY_API_KEY=...   # free tier at tavily.com

Configuration:
    Edit state.py to configure:
    - MAX_ITERATIONS: safety cap on search loops (default: 3)
    - MIN_RESULTS: minimum results for simple evaluation (default: 6)
    - LLM_EVALUATION: use LLM to evaluate vs simple count (default: True)
"""

import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_community.callbacks import get_openai_callback

from state import ResearchState
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
        if hasattr(record, 'iteration'):
            log_data["iteration"] = record.iteration
        if hasattr(record, 'query_count'):
            log_data["query_count"] = record.query_count
        if hasattr(record, 'queries'):
            log_data["queries"] = record.queries
        if hasattr(record, 'result_count'):
            log_data["result_count"] = record.result_count
        return json.dumps(log_data)


def setup_logging():
    """Configure logging to write structured logs to file."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # File handler with structured JSON logs
    file_handler = logging.FileHandler(
        f"logs/research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    file_handler.setFormatter(StructuredFormatter())
    file_handler.setLevel(logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    
    # Suppress noisy third-party loggers on console
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    
    agent = build_graph()

    question = input("Research question: ").strip()
    if not question:
        question = "What are the main differences between LangGraph and LangChain?"

    print(f"\nResearching: {question}\n{'─' * 60}")
    
    logger.info("Research started", extra={"question": question})

    initial_state: ResearchState = {
        "query": question,
        "search_queries": [],
        "results": [],
        "seen_urls": set(),
        "iteration": 0,
        "final_answer": "",
        "_enough": False,
        "feedback_hint": "",
    }

    # Track token usage and cost
    with get_openai_callback() as cb:
        final_state = agent.invoke(initial_state)

        print(f"\n{'─' * 60}\n{final_state['final_answer']}")
        
        # Display token usage in red
        print(f"\n{'─' * 60}")
        print(f"{COLOR_TOKENS}Token Usage:{COLOR_RESET}")
        print(f"{COLOR_TOKENS}  Total Tokens: {cb.total_tokens:,}{COLOR_RESET}")
        print(f"{COLOR_TOKENS}  Prompt Tokens: {cb.prompt_tokens:,}{COLOR_RESET}")
        print(f"{COLOR_TOKENS}  Completion Tokens: {cb.completion_tokens:,}{COLOR_RESET}")
        print(f"{COLOR_TOKENS}  Total Cost: ${cb.total_cost:.4f}{COLOR_RESET}")
        print(f"{'─' * 60}")
        
        # Log final metrics
        logger.info(
            "Research completed",
            extra={
                "question": question,
                "iterations": final_state["iteration"],
                "total_results": len(final_state["results"]),
                "total_tokens": cb.total_tokens,
                "prompt_tokens": cb.prompt_tokens,
                "completion_tokens": cb.completion_tokens,
                "total_cost": cb.total_cost,
            }
        )
