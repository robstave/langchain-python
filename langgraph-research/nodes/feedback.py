"""
Feedback node: asks the user if the answer is satisfactory.

Options:
  - Done (accept the answer)
  - Keep going (search for more information automatically)
  - Refine (user provides additional queries or focus areas)
"""
from state import ResearchState

# Colors for output
COLOR_FEEDBACK = '\033[33m'     # Dark yellow
COLOR_RESET = '\033[0m'         # Reset


def feedback(state: ResearchState) -> ResearchState:
    """
    Presents the answer and asks the user what to do next.
    
    Returns state with _enough=True to finish, or _enough=False
    to loop back to the planner for more research.
    """
    print(f"\n{'─' * 60}")
    print(state["final_answer"])
    print(f"{'─' * 60}")

    print(f"\n{COLOR_FEEDBACK}{'─' * 60}")
    print(f"[Feedback] Are you satisfied with this answer?")
    print(f"  1) Done — accept the answer")
    print(f"  2) Keep going — search for more information")
    print(f"  3) Refine — add your own search guidance")
    print(f"{'─' * 60}{COLOR_RESET}")

    choice = input("\nYour choice (1/2/3): ").strip()

    if choice == "2":
        hint = input("Any guidance for the next search? (press Enter to skip): ").strip()
        if hint:
            print(f"{COLOR_FEEDBACK}[Feedback]{COLOR_RESET} Continuing with hint: {hint}")
        else:
            hint = "The user was not satisfied with the answer. Try different search angles and look for information not already covered."
            print(f"{COLOR_FEEDBACK}[Feedback]{COLOR_RESET} Continuing with different search angles...")
        return {**state, "_enough": False, "feedback_hint": hint}

    elif choice == "3":
        refinement = input("Additional search query: ").strip()
        if refinement:
            print(f"{COLOR_FEEDBACK}[Feedback]{COLOR_RESET} Adding query: {refinement}")
            return {
                **state,
                "_enough": False,
                "search_queries": state["search_queries"] + [refinement],
            }
        else:
            print(f"{COLOR_FEEDBACK}[Feedback]{COLOR_RESET} No query given, continuing automatically...")
            return {**state, "_enough": False, "feedback_hint": ""}

    else:
        # Default: done (choice "1" or anything else)
        print(f"{COLOR_FEEDBACK}[Feedback]{COLOR_RESET} Answer accepted.")
        return {**state, "_enough": True}
