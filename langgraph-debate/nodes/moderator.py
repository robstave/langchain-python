"""Moderator node — frames the topic as a debatable proposition."""

import logging
from langchain_openai import ChatOpenAI
from state import MODEL_NAME, C_MOD, C_RESET

logger = logging.getLogger(__name__)

SYSTEM = (
    "You are a debate moderator. Given a topic, frame it as a clear, "
    "concise, debatable proposition — a single declarative sentence that "
    "one side can argue FOR and the other AGAINST.\n"
    "Output ONLY the proposition, nothing else."
)


def _get_llm():
    return ChatOpenAI(model=MODEL_NAME, temperature=0)


def moderator(state: dict) -> dict:
    """Frame the topic as a debatable proposition."""
    topic = state["topic"]
    logger.info("Moderator framing topic: %s", topic)

    llm = _get_llm()
    response = llm.invoke([
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": topic},
    ])
    proposition = response.content.strip().strip('"')

    print(f"\n{C_MOD}[Moderator]{C_RESET} Proposition:")
    print(f'  "{proposition}"\n')
    logger.info("Proposition: %s", proposition)

    return {
        **state,
        "proposition": proposition,
        "current_round": 1,
        "rounds": [],
        "_done": False,
    }
