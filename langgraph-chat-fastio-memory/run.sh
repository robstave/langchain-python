#!/usr/bin/env bash
set -euo pipefail

VENV_DIR="venv"

echo "LangGraph Chat + Fast.io MCP Memory"
echo "==================================="

if [ ! -f .env ]; then
  echo "No .env file found."
  echo "Copy .env.example to .env and set at least:"
  echo "  OPENAI_API_KEY=..."
  echo "  FASTIO_API_KEY=..."
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
python chat_fastio_memory.py
