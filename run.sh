#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then
  uv venv
  uv pip install -r requirements.txt
fi
uv run generate_samples.py
exec uv run uvicorn server:app --host 127.0.0.1 --port 8000
