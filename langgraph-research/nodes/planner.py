"""
Planner node: decides what to search for next.
"""
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from state import ResearchState, MODEL_NAME

# Colors for output
COLOR_PLANNER = '\033[95m'      # Magenta
COLOR_RESET = '\033[0m'         # Reset

logger = logging.getLogger(__name__)


def _get_llm():
    """Lazy LLM instantiation to ensure env vars are loaded."""
    return ChatOpenAI(model=MODEL_NAME, temperature=0)


def planner(state: ResearchState) -> ResearchState:
    """
    Looks at the original question + any results so far and decides
    what to search for next. Returns 1-3 search queries.
    """
    llm = _get_llm()
    
    prior_results_text = ""
    if state["results"]:
        snippets = "\n".join(
            f'- [{r["title"]}]: {r["content"][:200]}'
            for r in state["results"][-6:]   # last 6 results for context
        )
        prior_results_text = f"\n\nResults gathered so far:\n{snippets}"

    feedback_text = ""
    if state.get("feedback_hint"):
        feedback_text = f"\n\nUser feedback: {state['feedback_hint']}"

    system = SystemMessage(content=(
        "You are a research planner. Given a question and any prior search results, "
        "output 1-3 short, specific search queries (one per line) that will fill in "
        "missing information. Output ONLY the queries, nothing else."
    ))
    human = HumanMessage(content=(
        f"Question: {state['query']}"
        f"{prior_results_text}"
        f"{feedback_text}\n\n"
        "What should we search for next?"
    ))

    response = llm.invoke([system, human])
    queries = [
        line.strip().lstrip("-•1234567890. ")
        for line in response.content.strip().splitlines()
        if line.strip()
    ]

    # Structured log for analysis
    logger.info(
        "Planner generated queries",
        extra={
            "iteration": state['iteration'] + 1,
            "query_count": len(queries),
            "queries": queries,
            "result_count": len(state["results"])
        }
    )
    
    # Colorful output for humans
    print(f"\n{COLOR_PLANNER}[Planner]{COLOR_RESET} Iteration {state['iteration'] + 1} — queries: {queries}")
    return {**state, "search_queries": queries, "feedback_hint": ""}
