"""
Take Prompt node: gets the next user message or slash command.
"""
from state import MemoryChatState

COLOR_PROMPT = "\033[96m"
COLOR_RESET = "\033[0m"

DEFAULT_QUESTION = "What do you remember about my preferences?"


def take_prompt(state: MemoryChatState) -> MemoryChatState:
    print(f"\n{COLOR_PROMPT}{'─' * 60}")
    print("Tips:")
    print("  /remember <text>  -> store fact/preference")
    print("  /recall or /memory -> recall saved memory")
    print("  /forget <text>    -> remove/mark a memory item")
    print("  /list             -> show conversation history")
    print("  /quit or quit     -> end the session")
    print(f"{'─' * 60}{COLOR_RESET}")

    question = input(f"\n{COLOR_PROMPT}Enter your message:{COLOR_RESET} ").strip()
    lower = question.lower()

    if not question:
        question = DEFAULT_QUESTION
        action = "ask"
    elif lower == "/list":
        action = "list"
    elif lower in {"/quit", "quit"}:
        action = "done"
    else:
        action = "ask"

    print(f"{COLOR_PROMPT}[Prompt]{COLOR_RESET} {question}")
    return {**state, "query": question, "action": action}
