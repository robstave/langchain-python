# Multi-Agent Debate — Implementation Plan

## Overview

A LangGraph-based debate simulation where multiple LLM "agents" argue for and against
a proposition across multiple rounds. A judge scores each round and declares a winner.
Pure conversation — zero external APIs beyond OpenAI.

## Why This Project

- Teaches: multiple LLM personas, message passing between agents, state accumulation across rounds
- LangGraph concepts: conditional routing (judge decides if more rounds needed), round-based loops
- Reuses patterns from `langgraph-research`: state management, node functions, colorful output, logging
- Fun to watch — very visual output with different colors per debater

## Architecture

```
Topic
  │
  ▼
┌───────────┐     ┌──────┐     ┌──────┐     ┌──────┐
│ Moderator │────▶│ Pro  │────▶│ Con  │────▶│Judge │
│ (once)    │     │      │     │      │     │      │
└───────────┘     └──────┘     └──────┘     └──────┘
                    ▲                          │
                    └──── (more rounds) ───────┘
                                               │
                                          (_done=true)
                                               │
                                               ▼
                                             END
```

## Project Structure

```
langgraph-debate/
├── debate.py             # Main entry point
├── state.py              # DebateState + config
├── graph.py              # Graph construction and round routing
├── nodes/
│   ├── __init__.py
│   ├── moderator.py      # Frames the topic as a debatable proposition
│   ├── pro.py            # Argues FOR the proposition
│   ├── con.py            # Argues AGAINST the proposition
│   └── judge.py          # Scores rounds, decides continue/done, final verdict
├── requirements.txt
├── run.sh
├── .env                  # API keys (not committed)
└── README.md
```

## State Definition

```python
class DebateState(TypedDict):
    topic: str                   # raw topic from user
    proposition: str             # framed by moderator as a debatable statement
    rounds: list[dict]           # [{round, pro, con, score}]
    current_round: int           # which round we're on
    max_rounds: int              # safety cap
    pro_argument: str            # current round's pro argument
    con_argument: str            # current round's con rebuttal
    judgment: str                # judge's scoring for current round
    final_verdict: str           # judge's overall winner + reasoning
    _done: bool                  # whether debate is over
```

## Configuration (`state.py`)

```python
MODEL_NAME = "gpt-5.4-mini"
MAX_ROUNDS = 3
PRO_TEMPERATURE = 0.7          # slightly creative for variety
CON_TEMPERATURE = 0.7
JUDGE_TEMPERATURE = 0           # deterministic scoring
```

## Node Details

### 1. Moderator (`nodes/moderator.py`)

Runs once at the start. Takes the raw topic and uses an LLM to frame it as a clear,
debatable proposition.

Example: "Python vs JavaScript" → "Python is a better choice than JavaScript for
backend web development."

- System prompt: "Frame this topic as a clear, debatable proposition. Output ONLY the proposition."
- Print: `[Moderator] Proposition: "Python is better than JavaScript for backend development"`

### 2. Pro (`nodes/pro.py`)

Argues FOR the proposition. Gets the proposition, round number, and all previous rounds
so it can build on earlier points and rebut Con's arguments.

- System prompt: "You are a passionate, articulate debater arguing FOR the proposition..."
- On round 1: pure opening argument
- On round 2+: must address Con's previous points
- Temperature 0.7 for variety
- Print: `[Pro] Round 1 argument written.`

### 3. Con (`nodes/con.py`)

Argues AGAINST the proposition. Gets Pro's current argument so it can directly counter it.

- System prompt: "You are a sharp, critical debater arguing AGAINST the proposition..."
- Must directly address Pro's argument from the current round
- Temperature 0.7
- Print: `[Con] Round 1 rebuttal written.`

### 4. Judge (`nodes/judge.py`)

Evaluates the round. Scores both sides. Decides if more rounds are needed.

- System prompt: "Score this debate round 1-10 for each side. Consider: argument strength,
  evidence quality, rebuttal effectiveness, rhetorical skill."
- If not the last round and arguments are still evolving: `_done = False`
- If max rounds reached or clear winner: `_done = True`, write `final_verdict`
- Temperature 0 for consistent scoring
- Print: `[Judge] Round 1: Pro 7/10, Con 8/10 — continuing`
- Print: `[Judge] Final verdict: Con wins (24 vs 21 total points)`

## Color Scheme

- **Moderator**: Bold White (`\033[1m`)
- **Pro**: Green (`\033[92m`) — arguing for
- **Con**: Red (`\033[91m`) — arguing against
- **Judge**: Cyan (`\033[96m`) — neutral

## Graph Flow

```
Moderator → Pro → Con → Judge ──┐
              ▲                  │
              └── (next round) ──┘
              │
         (_done=true) → END
```

Conditional routing from Judge:
- `_done = False` → back to Pro (next round begins)
- `_done = True` → END

## Implementation Order

1. `state.py` — state + config
2. `requirements.txt`, `run.sh`
3. `nodes/moderator.py`
4. `nodes/pro.py`
5. `nodes/con.py`
6. `nodes/judge.py`
7. `nodes/__init__.py`, `graph.py`, `debate.py`
8. `README.md`

## Sample Output

```
Debate topic: Should AI be used to grade student essays?

[Moderator] Proposition: "AI should be the primary tool for grading student essays
in educational institutions."

═══ Round 1 ═══
[Pro] Opening argument...
  AI grading offers consistency, instant feedback, and scalability...

[Con] Rebuttal...
  AI lacks the nuance to evaluate creativity, voice, and critical thinking...

[Judge] Round 1: Pro 7/10, Con 8/10 — continuing

═══ Round 2 ═══
[Pro] ...
[Con] ...
[Judge] Round 2: Pro 7/10, Con 7/10 — continuing

═══ Round 3 ═══
[Pro] ...
[Con] ...
[Judge] Final verdict: Con wins (22 vs 21). While Pro made compelling efficiency
arguments, Con effectively demonstrated that essay grading requires human judgment...
```
