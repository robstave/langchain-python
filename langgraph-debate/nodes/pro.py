"""Pro node — argues FOR the proposition (Southern Lawyer persona)."""

import logging
from pathlib import Path
from langchain_openai import ChatOpenAI
from state import MODEL_NAME, PRO_TEMPERATURE, C_PRO, C_RESET, C_DIM

logger = logging.getLogger(__name__)

# Load persona from file
_PERSONA_PATH = Path(__file__).resolve().parent.parent / "personas" / "pro_southern_lawyer.md"
_PERSONA = _PERSONA_PATH.read_text() if _PERSONA_PATH.exists() else ""

SYSTEM = (
    "You are arguing FOR the following proposition.\n"
    "Proposition: {proposition}\n\n"
    + _PERSONA + "\n\n"
    "Rules:\n"
    "- Build clear, evidence-based arguments\n"
    "- If this is not the first round, directly address your opponent's previous points\n"
    "- Stay fully in character throughout\n"
    "- Keep your argument to 2-3 paragraphs"
)


def _get_llm():
    return ChatOpenAI(model=MODEL_NAME, temperature=PRO_TEMPERATURE)


def pro(state: dict) -> dict:
    """Generate the Pro argument for the current round."""
    rnd = state["current_round"]
    proposition = state["proposition"]
    rounds = state.get("rounds", [])
    logger.info("Pro arguing — round %d", rnd)

    # Build context from previous rounds
    history = ""
    for r in rounds:
        history += f"\n--- Round {r['round']} ---\n"
        history += f"Pro argued: {r['pro']}\n"
        history += f"Con argued: {r['con']}\n"

    prompt = f"This is round {rnd}."
    if history:
        prompt += f"\n\nPrevious rounds:{history}\n\nBuild on your earlier points and counter Con's arguments."
    else:
        prompt += " Deliver your opening argument."

    llm = _get_llm()
    response = llm.invoke([
        {"role": "system", "content": SYSTEM.format(proposition=proposition)},
        {"role": "user", "content": prompt},
    ])
    argument = response.content.strip()

    print(f"{C_DIM}{'═' * 60}{C_RESET}")
    print(f"{C_PRO}[Pro] Round {rnd}{C_RESET}")
    print(f"{C_PRO}{argument}{C_RESET}\n")

    return {**state, "pro_argument": argument}
