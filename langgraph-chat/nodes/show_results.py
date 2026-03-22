"""
Show Results node: displays the LLM response to the user.
"""
from state import ChatState

# Colors for output
COLOR_RESULT = '\033[92m'       # Green
COLOR_RESET = '\033[0m'         # Reset


def show_results(state: ChatState) -> ChatState:
    """Prints the latest LLM response with formatting."""
    print(f"\n{'─' * 60}")
    print(f"{COLOR_RESULT}{state['response']}{COLOR_RESET}")
    print(f"{'─' * 60}")
    return state
