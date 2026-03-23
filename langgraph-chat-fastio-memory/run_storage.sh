#!/usr/bin/env bash
set -euo pipefail

VENV_DIR="venv"

if [ ! -f .env ]; then
  echo "No .env file found. Copy .env.example and fill in your credentials."
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Virtual environment not found. Run run.sh first to set it up."
  exit 1
fi

echo "Running storage debug..."
echo ""

"$VENV_DIR/bin/python" debug_storage.py
