"""
Summarize node: sends the full conversation history to the LLM for summarization.
"""
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from state import ChatState, MODEL_NAME

# Colors for output
COLOR_SUMMARY = '\033[95m'      # Magenta
COLOR_RESET = '\033[0m'         # Reset

logger = logging.getLogger(__name__)


def _get_llm():
    """Lazy LLM instantiation to ensure env vars are loaded."""
    return ChatOpenAI(model=MODEL_NAME, temperature=0)


def summarize(state: ChatState) -> ChatState:
    """Summarizes the full conversation history using the LLM."""
    llm = _get_llm()

    # Build conversation text from history
    conversation_text = "\n\n".join(
        f"Turn {i+1}:\n  User: {turn['query']}\n  Assistant: {turn['response']}"
        for i, turn in enumerate(state["history"])
    )

    system = SystemMessage(content=(
        "You are a helpful assistant. Summarize the following conversation concisely, "
        "capturing the key questions asked, the main points covered, and any conclusions reached."
    ))
    human = HumanMessage(content=f"Conversation:\n{conversation_text}")

    response = llm.invoke([system, human])

    logger.info(
        "Conversation summarized",
        extra={"turns": len(state["history"]), "summary_length": len(response.content)}
    )

    print(f"\n{COLOR_SUMMARY}{'═' * 60}")
    print(f"[Summary] Conversation Summary")
    print(f"{'═' * 60}")
    print(f"{response.content}")
    print(f"{'═' * 60}{COLOR_RESET}")

    return {**state, "summary": response.content}
