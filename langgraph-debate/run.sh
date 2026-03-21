#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"

# ── Create venv if needed ──────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# ── Install deps ───────────────────────────────────────
pip install -q -r requirements.txt

# ── Check .env ─────────────────────────────────────────
if [ ! -f .env ]; then
    echo "⚠  No .env file found. Create one with:"
    echo "   OPENAI_API_KEY=sk-..."
    exit 1
fi

# ── Run ────────────────────────────────────────────────
python debate.py "$@"
