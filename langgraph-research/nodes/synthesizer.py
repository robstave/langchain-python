"""
Synthesizer node: writes the final answer with citations.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from state import ResearchState, MODEL_NAME

# Colors for output
COLOR_SYNTHESIZER = '\033[92m'  # Green
COLOR_RESET = '\033[0m'         # Reset


def _get_llm():
    """Lazy LLM instantiation to ensure env vars are loaded."""
    return ChatOpenAI(model=MODEL_NAME, temperature=0)


def synthesizer(state: ResearchState) -> ResearchState:
    """Reads all gathered results and writes a final cited answer."""
    llm = _get_llm()
    
    sources_text = "\n\n".join(
        f"[{i+1}] {r['title']} ({r['url']})\n{r['content'][:400]}"
        for i, r in enumerate(state["results"])
    )

    system = SystemMessage(content=(
        "You are a research assistant. Write a clear, thorough answer to the user's "
        "question using the provided sources. Cite sources with [1], [2], etc. "
        "End with a 'Sources' section listing the URLs."
    ))
    human = HumanMessage(content=(
        f"Question: {state['query']}\n\n"
        f"Sources:\n{sources_text}"
    ))

    response = llm.invoke([system, human])
    print(f"{COLOR_SYNTHESIZER}[Synthesizer]{COLOR_RESET} Answer written.")
    return {**state, "final_answer": response.content}
