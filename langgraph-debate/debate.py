#!/usr/bin/env python3
"""Multi-Agent Debate — main entry point."""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from state import DebateState, MAX_ROUNDS, C_BOLD, C_RESET, C_DIM
from graph import build_graph

# ── Logging setup ────────────────────────────────────────

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "ts": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        })


def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    fh = logging.FileHandler(log_dir / "debate.log")
    fh.setFormatter(StructuredFormatter())
    fh.setLevel(logging.DEBUG)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(fh)


# ── Main ─────────────────────────────────────────────────

def main():
    load_dotenv()
    setup_logging()

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set. Check your .env file.")
        sys.exit(1)

    # Get topic from args or prompt
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input(f"{C_BOLD}Enter a debate topic: {C_RESET}").strip()
        if not topic:
            print("No topic given. Exiting.")
            return

    print(f"\n{C_DIM}{'─' * 60}{C_RESET}")
    print(f"{C_BOLD}Debate: {topic}{C_RESET}")
    print(f"{C_DIM}Max rounds: {MAX_ROUNDS}{C_RESET}")
    print(f"{C_DIM}{'─' * 60}{C_RESET}")

    graph = build_graph()

    initial_state: DebateState = {
        "topic": topic,
        "proposition": "",
        "rounds": [],
        "current_round": 0,
        "max_rounds": MAX_ROUNDS,
        "pro_argument": "",
        "con_argument": "",
        "judgment": "",
        "final_verdict": "",
        "_done": False,
    }

    result = graph.invoke(initial_state)

    # Summary
    print(f"{C_DIM}{'─' * 60}{C_RESET}")
    print(f"{C_BOLD}Debate complete.{C_RESET}")
    total_rounds = len(result.get("rounds", []))
    print(f"  Rounds: {total_rounds}")
    for r in result.get("rounds", []):
        print(f"  Round {r['round']}: Pro {r['score_pro']}/10, Con {r['score_con']}/10")


if __name__ == "__main__":
    main()
