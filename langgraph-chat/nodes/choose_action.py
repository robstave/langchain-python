"""
Choose Action node: presents the user with options after seeing the LLM response.
"""
from state import ChatState

# Colors for output
COLOR_ACTION = '\033[33m'       # Dark yellow
COLOR_RESET = '\033[0m'         # Reset


def choose_action(state: ChatState) -> ChatState:
    """
    Displays action menu and sets state['action'] for the router.
    On 'refine', also prompts for the follow-up query.
    """
    print(f"\n{COLOR_ACTION}{'─' * 60}")
    print(f"[Action] What would you like to do?")
    print(f"  1) Done — end the conversation")
    print(f"  2) Refine — ask a follow-up question")
    print(f"  3) Summarize — summarize the conversation so far")
    print(f"  4) List — show all conversation turns")
    print(f"  5) Compress — condense older turns to save context")
    print(f"{'─' * 60}{COLOR_RESET}")

    choice = input("\nYour choice (1/2/3/4/5): ").strip()

    if choice == "2":
        refinement = input(f"\n{COLOR_ACTION}Follow-up question:{COLOR_RESET} ").strip()
        if not refinement:
            refinement = "Can you elaborate on that?"
        print(f"{COLOR_ACTION}[Action]{COLOR_RESET} Refining with: {refinement}")
        return {**state, "action": "refine", "query": refinement}

    elif choice == "3":
        print(f"{COLOR_ACTION}[Action]{COLOR_RESET} Summarizing conversation...")
        return {**state, "action": "summarize"}

    elif choice == "4":
        print(f"{COLOR_ACTION}[Action]{COLOR_RESET} Listing conversation history...")
        return {**state, "action": "list"}

    elif choice == "5":
        print(f"{COLOR_ACTION}[Action]{COLOR_RESET} Compressing older turns...")
        return {**state, "action": "compress"}

    else:
        # Default: done (choice "1" or anything else)
        print(f"{COLOR_ACTION}[Action]{COLOR_RESET} Ending conversation.")
        return {**state, "action": "done"}
