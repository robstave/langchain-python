"""
Answerer node: generates an answer with file:line citations from retrieved chunks.
"""
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from state import QnAState, MODEL_NAME

# Colors for output
COLOR_ANSWERER = '\033[92m'     # Green
COLOR_RESET = '\033[0m'         # Reset

logger = logging.getLogger(__name__)


def _get_llm():
    """Lazy LLM instantiation to ensure env vars are loaded."""
    return ChatOpenAI(model=MODEL_NAME, temperature=0)


def answerer(state: QnAState) -> QnAState:
    """Generate an answer using only the retrieved chunks as context."""
    chunks = state["relevant_chunks"]

    if not chunks:
        answer = "I couldn't find any information about that in the loaded documents."
        print(f"{COLOR_ANSWERER}[Answerer]{COLOR_RESET}  No relevant chunks — returned empty answer")
        return {**state, "answer": answer}

    llm = _get_llm()

    # Format chunks with source info for the LLM
    context_parts = []
    for c in chunks:
        ref = f"[{c['filename']}:{c['start_line']}-{c['end_line']}]"
        context_parts.append(f"{ref}\n{c['text']}")

    context = "\n\n---\n\n".join(context_parts)

    system = SystemMessage(content=(
        "You are a helpful assistant that answers questions using ONLY the provided "
        "document context. Do not use outside knowledge.\n\n"
        "Each context chunk is labeled with [filename:start_line-end_line]. "
        "Cite your sources using this format, e.g. [git_commands.md:45-60].\n\n"
        "If the provided context does not contain enough information to answer "
        "the question, say so honestly."
    ))
    human = HumanMessage(content=(
        f"Question: {state['question']}\n\n"
        f"Context:\n{context}"
    ))

    response = llm.invoke([system, human])
    answer = response.content

    logger.info(
        "Answer generated",
        extra={"chunks_used": len(chunks), "answer_length": len(answer)},
    )
    print(f"{COLOR_ANSWERER}[Answerer]{COLOR_RESET}  Answer written ({len(chunks)} chunks used)")

    return {**state, "answer": answer}
