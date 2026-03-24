"""
Take Prompt node: gets the next user message.
"""
from state import MemoryChatState

COLOR_PROMPT = "\033[96m"
COLOR_RESET = "\033[0m"


def take_prompt(state: MemoryChatState) -> MemoryChatState:
    question = input(
        f"\n{COLOR_PROMPT}Enter your message (/list, /quit):{COLOR_RESET} "
    ).strip()
    if not question:
        question = "What do you remember about my preferences?"

    print(f"{COLOR_PROMPT}[Prompt]{COLOR_RESET} {question}")
    return {**state, "query": question}
