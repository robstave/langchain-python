"""
Evaluator node: decides if we have enough information.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from state import ResearchState, MAX_ITERATIONS, MIN_RESULTS, LLM_EVALUATION, MODEL_NAME

# Colors for output
COLOR_EVALUATOR = '\033[96m'    # Cyan
COLOR_RESET = '\033[0m'         # Reset


def _get_llm():
    """Lazy LLM instantiation to ensure env vars are loaded."""
    return ChatOpenAI(model=MODEL_NAME, temperature=0)


def evaluator(state: ResearchState) -> ResearchState:
    """
    Decides whether we have enough information to write a final answer.
    
    If LLM_EVALUATION is True, uses an LLM to make the decision.
    Otherwise, uses simple heuristics (result count + iteration cap).
    """
    # Always check iteration cap first (safety)
    if state["iteration"] >= MAX_ITERATIONS:
        print(f"{COLOR_EVALUATOR}[Evaluator]{COLOR_RESET} Max iterations reached — forcing synthesis")
        return {**state, "_enough": True}
    
    if LLM_EVALUATION:
        # Use LLM to evaluate if we have enough information
        enough = _llm_evaluate(state)
    else:
        # Simple heuristic: minimum result count
        enough = len(state["results"]) >= MIN_RESULTS
    
    verdict = "yes" if enough else "no"
    print(f"{COLOR_EVALUATOR}[Evaluator]{COLOR_RESET} {len(state['results'])} results, iteration {state['iteration']} — enough? {verdict}")
    return {**state, "_enough": enough}


def _llm_evaluate(state: ResearchState) -> bool:
    """Use LLM to determine if we have enough information."""
    llm = _get_llm()
    
    # Summarize the results we have
    results_summary = "\n\n".join(
        f"[{i+1}] {r['title']}\n{r['content'][:300]}"
        for i, r in enumerate(state["results"][:10])  # Show first 10 results
    )
    
    system = SystemMessage(content=(
        "You are evaluating whether we have enough search results to answer a question. "
        "Reply with ONLY 'YES' if we have sufficient information, or 'NO' if we need more research."
    ))
    human = HumanMessage(content=(
        f"Question: {state['query']}\n\n"
        f"Search Results ({len(state['results'])} total):\n{results_summary}\n\n"
        "Do we have enough information to write a comprehensive answer?"
    ))
    
    response = llm.invoke([system, human])
    decision = response.content.strip().upper()
    
    # Debug: show what the LLM decided
    print(f"{COLOR_EVALUATOR}  → LLM evaluation: '{decision[:50]}'{COLOR_RESET}")
    
    # Check for YES/NO explicitly
    if decision.startswith("YES"):
        return True
    elif decision.startswith("NO"):
        return False
    else:
        # If unclear, default to needing more info
        print(f"{COLOR_EVALUATOR}  → Unexpected response, defaulting to NO{COLOR_RESET}")
        return False
