"""
List History node: prints all turns.
"""
from state import MemoryChatState

COLOR_LIST = "\033[94m"
COLOR_RESET = "\033[0m"


def list_history(state: MemoryChatState) -> MemoryChatState:
    print(f"\n{COLOR_LIST}{'═' * 60}")
    print(f"[History] {len(state['history'])} turns")
    print(f"{'═' * 60}{COLOR_RESET}")

    for i, turn in enumerate(state["history"], start=1):
        print(f"\n{COLOR_LIST}Turn {i}:{COLOR_RESET}")
        print(f"  Q: {turn['query']}")
        response = turn["response"]
        if len(response) > 220:
            response = response[:220] + "..."
        print(f"  A: {response}")

    print(f"\n{COLOR_LIST}{'═' * 60}{COLOR_RESET}")
    return state
