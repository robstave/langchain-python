"""
List History node: displays all conversation turns to the user.
"""
from state import ChatState

# Colors for output
COLOR_LIST = '\033[94m'         # Blue
COLOR_COMPRESSED = '\033[36m'   # Cyan
COLOR_RESET = '\033[0m'        # Reset


def list_history(state: ChatState) -> ChatState:
    """Prints each conversation turn numbered, with compressed entries marked."""
    print(f"\n{COLOR_LIST}{'═' * 60}")
    print(f"[History] Conversation so far ({len(state['history'])} entries)")
    print(f"{'═' * 60}{COLOR_RESET}")

    for i, turn in enumerate(state["history"]):
        if turn.get("compressed"):
            count = turn.get("compressed_count", "?")
            print(f"\n{COLOR_COMPRESSED}Turn {i+1} [compressed — {count} turns]:{COLOR_RESET}")
            print(f"  Original Q: {turn['query']}")
            print(f"  Summary: {turn['response']}")
        else:
            print(f"\n{COLOR_LIST}Turn {i+1}:{COLOR_RESET}")
            print(f"  Q: {turn['query']}")
            resp = turn["response"]
            if len(resp) > 200:
                resp = resp[:200] + "..."
            print(f"  A: {resp}")

    print(f"\n{COLOR_LIST}{'═' * 60}{COLOR_RESET}")
    return state
