# Multi-Agent Debate

A LangGraph application where multiple LLM agents argue for and against a proposition
across multiple rounds, with a judge scoring each round and declaring a winner.

## What You'll Learn

- Running multiple LLM personas with different system prompts and temperatures
- Round-based looping with conditional routing (judge decides when to stop)
- Accumulating state across iterations (round history, scores)
- Structured output parsing (extracting scores from judge responses)

## Project Structure

```
langgraph-debate/
├── debate.py             # Main entry point
├── state.py              # DebateState + config constants
├── graph.py              # Graph wiring + round routing
├── nodes/
│   ├── moderator.py      # Frames topic as a debatable proposition
│   ├── pro.py            # Argues FOR the proposition
│   ├── con.py            # Argues AGAINST the proposition
│   └── judge.py          # Scores rounds, decides continue/done, final verdict
├── requirements.txt
├── run.sh
└── README.md
```

## Workflow

```mermaid
graph TD
    A[Moderator] --> B[Pro]
    B --> C[Con]
    C --> D[Judge]
    D -->|more rounds| B
    D -->|done| E[END]
```

1. **Moderator** — Runs once. Takes the raw topic and frames it as a clear, debatable proposition.
2. **Pro** — Argues FOR the proposition. In later rounds, addresses Con's previous points.
3. **Con** — Argues AGAINST. Directly rebuts Pro's current argument.
4. **Judge** — Scores both sides 1-10, writes commentary. After the last round, produces a final verdict with winner and reasoning.

## Node Details

### Moderator (`nodes/moderator.py`)
- Converts a vague topic into a crisp proposition
- Example: "AI in schools" → "AI should be the primary tool for grading student essays"
- Runs once at the start, then the graph moves to the debate loop

### Pro (`nodes/pro.py`)
- Temperature 0.7 for creative variety
- Round 1: delivers an opening argument
- Round 2+: builds on earlier points and counters Con's previous arguments
- Gets full history of previous rounds for context

### Con (`nodes/con.py`)
- Temperature 0.7
- Always sees Pro's current-round argument to directly counter it
- Has access to the full round history
- Focuses on dismantling Pro's specific claims

### Judge (`nodes/judge.py`)
- Temperature 0 for consistent, deterministic scoring
- Parses structured output: `PRO_SCORE`, `CON_SCORE`, `COMMENTARY`
- After the final round, produces `WINNER` and `REASON` via a separate LLM call
- Routing: `_done=True` → END, otherwise → back to Pro for next round

## Configuration

Edit `state.py` to adjust:

| Setting | Default | Description |
|---------|---------|-------------|
| `MODEL_NAME` | `gpt-4.1-mini` | OpenAI model |
| `MAX_ROUNDS` | `3` | Maximum debate rounds |
| `PRO_TEMPERATURE` | `0.7` | Creativity for Pro agent |
| `CON_TEMPERATURE` | `0.7` | Creativity for Con agent |
| `JUDGE_TEMPERATURE` | `0` | Deterministic judge scoring |

## Setup

```bash
# From this directory:
./run.sh "Python vs JavaScript for backend development"

# Or interactively:
./run.sh
# → Enter a debate topic: AI replacing teachers
```

Requires a `.env` file:
```
OPENAI_API_KEY=sk-...
```

## Example Output

```
────────────────────────────────────────────────────────────
Debate: Python vs JavaScript for backend development
Max rounds: 3
────────────────────────────────────────────────────────────

[Moderator] Proposition:
  "Python is a superior choice to JavaScript for backend web development."

════════════════════════════════════════════════════════════
[Pro] Round 1
Python's rich ecosystem of frameworks like Django and FastAPI, combined with
its clean syntax, makes it the clear winner for backend development...

[Con] Round 1
While Python has excellent frameworks, JavaScript's Node.js offers unmatched
performance for I/O-heavy applications and enables full-stack development...

[Judge] Round 1: Pro 7/10, Con 8/10
  Con effectively countered with Node.js performance advantages.

════════════════════════════════════════════════════════════
[Pro] Round 2
...

[Con] Round 2
...

[Judge] Round 2: Pro 8/10, Con 7/10
  Pro made strong data science ecosystem arguments.

════════════════════════════════════════════════════════════
[Pro] Round 3
...

[Con] Round 3
...

[Judge] Final Verdict (Pro 22 vs Con 22):
WINNER: Con
REASON: While the scores are tied, Con demonstrated stronger practical arguments
about full-stack consistency and the npm ecosystem breadth...

────────────────────────────────────────────────────────────
Debate complete.
  Rounds: 3
  Round 1: Pro 7/10, Con 8/10
  Round 2: Pro 8/10, Con 7/10
  Round 3: Pro 7/10, Con 7/10
```

## Ideas to Extend

- **Audience node** — A fourth agent that votes after each round
- **Fact-checker** — Use Tavily search to verify claims made by debaters
- **Export** — Save debate transcript to markdown (like langgraph-research)
- **Dynamic rounds** — Let the judge end early if one side is clearly winning
- **Multiple debaters** — 2v2 panel format with different specialist personas
