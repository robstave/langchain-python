"""
Choose Action node for chat loop control.
"""
from state import MemoryChatState

COLOR_ACTION = "\033[33m"
COLOR_RESET = "\033[0m"


def choose_action(state: MemoryChatState) -> MemoryChatState:
    print(f"\n{COLOR_ACTION}{'─' * 60}")
    print("[Action] What next?")
    print("  1) Done — end session")
    print("  2) Refine — ask follow-up")
    print("  3) List — show conversation history")
    print("Tips:")
    print("  /remember <text>  -> store fact/preference")
    print("  /recall or /memory -> recall saved memory")
    print("  /forget <text>    -> remove/mark a memory item")
    print(f"{'─' * 60}{COLOR_RESET}")

    choice = input("\nYour choice (1/2/3): ").strip()

    if choice == "2":
        refinement = input(f"\n{COLOR_ACTION}Follow-up:{COLOR_RESET} ").strip()
        if not refinement:
            refinement = "Can you elaborate on that?"
        return {**state, "action": "refine", "query": refinement}
    if choice == "3":
        return {**state, "action": "list"}
    return {**state, "action": "done"}
