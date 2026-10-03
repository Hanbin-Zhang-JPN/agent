#!/bin/sh
# Portable launcher; prefer the project's environment, then Codex's PDF-ready runtime.
set -eu
cd "$(dirname "$0")"
if [ -n "${RAG_PYTHON:-}" ]; then
  rag_python="$RAG_PYTHON"
elif [ -x .venv/bin/python3 ]; then
  rag_python=.venv/bin/python3
elif [ -x "$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3" ]; then
  rag_python="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
else
  rag_python=python3
fi
exec "$rag_python" server.py "$@"
