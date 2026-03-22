"""
Take Prompt node: gets the initial question from the user.
"""
from state import ChatState

# Colors for output
COLOR_PROMPT = '\033[96m'       # Cyan
COLOR_RESET = '\033[0m'         # Reset


def take_prompt(state: ChatState) -> ChatState:
    """Prompts the user for their initial question."""
    question = input(f"\n{COLOR_PROMPT}Enter your question:{COLOR_RESET} ").strip()
    if not question:
        question = "What is LangGraph and how does it differ from LangChain?"

    print(f"{COLOR_PROMPT}[Prompt]{COLOR_RESET} Got question: {question}")
    return {**state, "query": question}
