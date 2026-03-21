"""Debate state definition and configuration."""

from typing import TypedDict

# ── Config ───────────────────────────────────────────────
MODEL_NAME = "gpt-5.4-mini"
MAX_ROUNDS = 3
PRO_TEMPERATURE = 0.7
CON_TEMPERATURE = 0.7
JUDGE_TEMPERATURE = 0

# ── Colors ───────────────────────────────────────────────
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_MOD = "\033[1m"        # Moderator — bold white
C_PRO = "\033[92m"       # Pro — green
C_CON = "\033[91m"       # Con — red
C_JUDGE = "\033[96m"     # Judge — cyan
C_DIM = "\033[90m"       # dim for separators


class DebateState(TypedDict):
    topic: str                  # raw topic from user
    proposition: str            # framed by moderator
    rounds: list[dict]          # [{round, pro, con, score_pro, score_con, judgment}]
    current_round: int
    max_rounds: int
    pro_argument: str           # current round's pro argument
    con_argument: str           # current round's con rebuttal
    judgment: str               # judge's scoring for current round
    final_verdict: str          # overall winner + reasoning
    _done: bool
