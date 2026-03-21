"""Judge node — scores the round, decides whether to continue, gives final verdict (Judge Judy persona)."""

import logging
import re
from pathlib import Path
from langchain_openai import ChatOpenAI
from state import MODEL_NAME, JUDGE_TEMPERATURE, C_JUDGE, C_RESET, C_BOLD

logger = logging.getLogger(__name__)

# Load persona from file
_PERSONA_PATH = Path(__file__).resolve().parent.parent / "personas" / "judge_judy.md"
_PERSONA = _PERSONA_PATH.read_text() if _PERSONA_PATH.exists() else ""

ROUND_SYSTEM = (
    "You are a debate judge evaluating a single round.\n\n"
    + _PERSONA + "\n\n"
    "Score each side from 1 to 10 on: argument strength, evidence quality, "
    "rebuttal effectiveness, and rhetorical skill.\n\n"
    "You MUST include these exact lines somewhere in your response:\n"
    "PRO_SCORE: <number>\n"
    "CON_SCORE: <number>\n"
    "COMMENTARY: <one-sentence summary>\n\n"
    "You may add Judge Judy commentary around them, but those three lines must appear exactly."
)

VERDICT_SYSTEM = (
    "You are a debate judge delivering a final verdict.\n\n"
    + _PERSONA + "\n\n"
    "Based on all rounds below, declare a winner and explain your reasoning.\n\n"
    "You MUST include these exact lines somewhere in your response:\n"
    "WINNER: <Pro or Con>\n"
    "REASON: <explanation>\n\n"
    "Deliver the verdict with full Judge Judy attitude."
)


def _get_llm():
    return ChatOpenAI(model=MODEL_NAME, temperature=JUDGE_TEMPERATURE)


def _parse_scores(text: str) -> tuple[int, int, str]:
    """Extract PRO_SCORE, CON_SCORE, COMMENTARY from judge response."""
    pro_m = re.search(r"PRO_SCORE:\s*(\d+)", text)
    con_m = re.search(r"CON_SCORE:\s*(\d+)", text)
    com_m = re.search(r"COMMENTARY:\s*(.+)", text)

    pro_score = int(pro_m.group(1)) if pro_m else 5
    con_score = int(con_m.group(1)) if con_m else 5
    commentary = com_m.group(1).strip() if com_m else text.strip()
    return pro_score, con_score, commentary


def judge(state: dict) -> dict:
    """Score the current round and decide whether the debate continues."""
    rnd = state["current_round"]
    max_rnd = state["max_rounds"]
    proposition = state["proposition"]
    pro_arg = state["pro_argument"]
    con_arg = state["con_argument"]
    rounds = list(state.get("rounds", []))
    llm = _get_llm()

    logger.info("Judge evaluating round %d", rnd)

    # ── Score this round ─────────────────────────────────
    round_prompt = (
        f"Proposition: {proposition}\n\n"
        f"Round {rnd}:\n"
        f"PRO argument:\n{pro_arg}\n\n"
        f"CON rebuttal:\n{con_arg}"
    )
    response = llm.invoke([
        {"role": "system", "content": ROUND_SYSTEM},
        {"role": "user", "content": round_prompt},
    ])
    pro_score, con_score, commentary = _parse_scores(response.content)

    round_record = {
        "round": rnd,
        "pro": pro_arg,
        "con": con_arg,
        "score_pro": pro_score,
        "score_con": con_score,
        "judgment": commentary,
    }
    rounds.append(round_record)

    print(f"{C_JUDGE}[Judge] Round {rnd}: Pro {pro_score}/10, Con {con_score}/10{C_RESET}")
    print(f"{C_JUDGE}  {commentary}{C_RESET}\n")

    # ── Decide: continue or final verdict? ───────────────
    if rnd >= max_rnd:
        done = True
    else:
        done = False

    new_state = {
        **state,
        "rounds": rounds,
        "judgment": commentary,
        "current_round": rnd + 1,
        "_done": done,
    }

    if done:
        # Produce final verdict
        all_rounds_text = ""
        total_pro = 0
        total_con = 0
        for r in rounds:
            all_rounds_text += (
                f"\n--- Round {r['round']} ---\n"
                f"Pro ({r['score_pro']}/10): {r['pro'][:200]}...\n"
                f"Con ({r['score_con']}/10): {r['con'][:200]}...\n"
            )
            total_pro += r["score_pro"]
            total_con += r["score_con"]

        verdict_prompt = (
            f"Proposition: {proposition}\n"
            f"Total scores — Pro: {total_pro}, Con: {total_con}\n"
            f"{all_rounds_text}"
        )
        verdict_resp = llm.invoke([
            {"role": "system", "content": VERDICT_SYSTEM},
            {"role": "user", "content": verdict_prompt},
        ])
        verdict = verdict_resp.content.strip()
        new_state["final_verdict"] = verdict

        print(f"{C_BOLD}{'═' * 60}{C_RESET}")
        print(f"{C_JUDGE}[Judge] Final Verdict (Pro {total_pro} vs Con {total_con}):{C_RESET}")
        print(f"{C_JUDGE}{verdict}{C_RESET}\n")
        logger.info("Debate ended. Pro %d, Con %d", total_pro, total_con)
    else:
        logger.info("Round %d complete — continuing to round %d", rnd, rnd + 1)

    return new_state
