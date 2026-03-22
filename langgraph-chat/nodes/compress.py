"""
Compress node: condenses older conversation turns to save context window space.

Keeps the last 2 turns intact and compresses everything before them into a single
summary entry. The compressed entry retains the original question and is flagged
with compressed=True so other nodes can display it differently.
"""
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from state import ChatState, MODEL_NAME

# Colors for output
COLOR_COMPRESS = '\033[36m'     # Cyan
COLOR_RESET = '\033[0m'         # Reset

logger = logging.getLogger(__name__)

# Need at least 3 old turns before the last 2 to compress
MIN_COMPRESSIBLE = 3


def _get_llm():
    """Lazy LLM instantiation to ensure env vars are loaded."""
    return ChatOpenAI(model=MODEL_NAME, temperature=0)


def compress(state: ChatState) -> ChatState:
    """
    Compresses conversation turns that are 3+ positions from the end.

    Given history [1, 2, 3, 4, 5], keeps 4 and 5 intact and compresses
    1, 2, 3 into a single summary entry with the original question preserved.
    """
    history = state["history"]

    if len(history) < MIN_COMPRESSIBLE + 2:
        print(f"{COLOR_COMPRESS}[Compress]{COLOR_RESET} Not enough history to compress "
              f"(need {MIN_COMPRESSIBLE + 2}+ turns, have {len(history)})")
        return state

    to_compress = history[:-2]
    to_keep = history[-2:]

    # Already fully compressed
    if len(to_compress) == 1 and to_compress[0].get("compressed"):
        print(f"{COLOR_COMPRESS}[Compress]{COLOR_RESET} Already compressed — nothing to do.")
        return state

    # Build conversation text for summarization
    conversation_text = []
    for i, turn in enumerate(to_compress):
        if turn.get("compressed"):
            conversation_text.append(
                f"[Compressed summary of earlier turns]:\n  {turn['response']}"
            )
        else:
            conversation_text.append(
                f"Turn {i+1}:\n  User: {turn['query']}\n  Assistant: {turn['response']}"
            )

    llm = _get_llm()

    system = SystemMessage(content=(
        "You are a conversation compressor. Summarize the following conversation turns "
        "into a concise but informative summary. Preserve key facts, decisions, and "
        "important details. Keep the summary compact — aim for 2-4 sentences."
    ))
    human = HumanMessage(content="\n\n".join(conversation_text))

    response = llm.invoke([system, human])

    original_query = to_compress[0]["query"]

    compressed_entry = {
        "query": original_query,
        "response": response.content,
        "compressed": True,
        "compressed_count": len(to_compress),
    }

    new_history = [compressed_entry] + to_keep

    logger.info(
        "History compressed",
        extra={
            "compressed_turns": len(to_compress),
            "remaining_turns": len(new_history),
        }
    )

    print(f"\n{COLOR_COMPRESS}{'═' * 60}")
    print(f"[Compress] Compressed {len(to_compress)} turns into 1 summary")
    print(f"{'═' * 60}")
    print(f"  Original question: {original_query}")
    print(f"  Summary: {response.content}")
    print(f"{'═' * 60}{COLOR_RESET}")

    return {**state, "history": new_history}
