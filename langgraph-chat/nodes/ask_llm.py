"""
Ask LLM node: sends the current query (with conversation history) to the LLM.
"""
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from state import ChatState, MODEL_NAME

# Colors for output
COLOR_LLM = '\033[93m'          # Yellow
COLOR_RESET = '\033[0m'         # Reset

logger = logging.getLogger(__name__)


def _get_llm():
    """Lazy LLM instantiation to ensure env vars are loaded."""
    return ChatOpenAI(model=MODEL_NAME, temperature=0)


def ask_llm(state: ChatState) -> ChatState:
    """
    Builds a message list from system prompt + full history + current query,
    invokes the LLM, and appends the turn to history.
    """
    llm = _get_llm()

    messages = [
        SystemMessage(content=(
            "You are a helpful conversational assistant. Answer the user's question "
            "clearly and thoroughly. If this is a follow-up question, use the prior "
            "conversation context to give a more focused answer."
        ))
    ]

    # Replay conversation history as alternating Human/AI messages
    for turn in state["history"]:
        if turn.get("compressed"):
            # Compressed turns: send as context summary
            messages.append(HumanMessage(content=f"[Earlier conversation about: {turn['query']}]"))
            messages.append(AIMessage(content=f"[Summary of prior discussion: {turn['response']}]"))
        else:
            messages.append(HumanMessage(content=turn["query"]))
            messages.append(AIMessage(content=turn["response"]))

    # Current query
    messages.append(HumanMessage(content=state["query"]))

    response = llm.invoke(messages)

    # Append this turn to history
    new_history = state["history"] + [
        {"query": state["query"], "response": response.content}
    ]

    logger.info(
        "LLM responded",
        extra={
            "turn": len(new_history),
            "query_length": len(state["query"]),
            "response_length": len(response.content),
        }
    )

    print(f"\n{COLOR_LLM}[LLM]{COLOR_RESET} Response received (turn {len(new_history)})")
    return {**state, "response": response.content, "history": new_history}
