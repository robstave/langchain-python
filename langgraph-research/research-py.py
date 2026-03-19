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
from dotenv import load_dotenv
from langchain_community.callbacks import get_openai_callback

from state import ResearchState
from graph import build_graph

# Load environment variables from .env file
load_dotenv()

# Colors for terminal output
COLOR_TOKENS = '\033[91m'       # Red
COLOR_RESET = '\033[0m'         # Reset


if __name__ == "__main__":
    agent = build_graph()

    question = input("Research question: ").strip()
    if not question:
        question = "What are the main differences between LangGraph and LangChain?"

    print(f"\nResearching: {question}\n{'─' * 60}")

    initial_state: ResearchState = {
        "query": question,
        "search_queries": [],
        "results": [],
        "iteration": 0,
        "final_answer": "",
        "_enough": False,
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
