"""Con node — argues AGAINST the proposition (Vinny persona)."""

import logging
from pathlib import Path
from langchain_openai import ChatOpenAI
from state import MODEL_NAME, CON_TEMPERATURE, C_CON, C_RESET

logger = logging.getLogger(__name__)

# Load persona from file
_PERSONA_PATH = Path(__file__).resolve().parent.parent / "personas" / "con_vinny.md"
_PERSONA = _PERSONA_PATH.read_text() if _PERSONA_PATH.exists() else ""

SYSTEM = (
    "You are arguing AGAINST the following proposition.\n"
    "Proposition: {proposition}\n\n"
    + _PERSONA + "\n\n"
    "Rules:\n"
    "- Directly counter your opponent's arguments from this round\n"
    "- Use common sense, real-world examples, and sharp questions\n"
    "- Stay fully in character throughout\n"
    "- Keep your rebuttal to 2-3 paragraphs"
)


def _get_llm():
    return ChatOpenAI(model=MODEL_NAME, temperature=CON_TEMPERATURE)


def con(state: dict) -> dict:
    """Generate the Con rebuttal for the current round."""
    rnd = state["current_round"]
    proposition = state["proposition"]
    pro_argument = state["pro_argument"]
    rounds = state.get("rounds", [])
    logger.info("Con rebutting — round %d", rnd)

    # Build context
    history = ""
    for r in rounds:
        history += f"\n--- Round {r['round']} ---\n"
        history += f"Pro argued: {r['pro']}\n"
        history += f"Con argued: {r['con']}\n"

    prompt = f"This is round {rnd}.\n\nPro's argument this round:\n{pro_argument}"
    if history:
        prompt += f"\n\nPrevious rounds:{history}"
    prompt += "\n\nDeliver your rebuttal."

    llm = _get_llm()
    response = llm.invoke([
        {"role": "system", "content": SYSTEM.format(proposition=proposition)},
        {"role": "user", "content": prompt},
    ])
    rebuttal = response.content.strip()

    print(f"{C_CON}[Con] Round {rnd}{C_RESET}")
    print(f"{C_CON}{rebuttal}{C_RESET}\n")

    return {**state, "con_argument": rebuttal}
