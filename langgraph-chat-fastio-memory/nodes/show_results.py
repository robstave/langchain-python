"""
Show Results node: prints the latest answer.
"""
from state import MemoryChatState

COLOR_RESULT = "\033[92m"
COLOR_RESET = "\033[0m"


def show_results(state: MemoryChatState) -> MemoryChatState:
    print(f"\n{'─' * 60}")
    print(f"{COLOR_RESULT}{state['response']}{COLOR_RESET}")
    print(f"{'─' * 60}")
    return state
