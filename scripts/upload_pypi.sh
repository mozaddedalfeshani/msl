#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TOKEN_FILE="$ROOT_DIR/.pypi-token"

if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
else
  PYTHON_BIN="python3"
fi

if [[ -z "${TWINE_PASSWORD:-}" ]]; then
  if [[ -f "$TOKEN_FILE" ]]; then
    TWINE_PASSWORD="$(tr -d '[:space:]' < "$TOKEN_FILE")"
    export TWINE_PASSWORD
  else
    echo "Missing PyPI token. Set TWINE_PASSWORD or create $TOKEN_FILE" >&2
    exit 1
  fi
fi

export TWINE_NON_INTERACTIVE=1
export TWINE_USERNAME="${TWINE_USERNAME:-__token__}"

cd "$ROOT_DIR"

if ! compgen -G 'dist/*' > /dev/null; then
  echo "No distribution files found in dist/. Build the package first." >&2
  exit 1
fi

"$PYTHON_BIN" -m twine check dist/*
"$PYTHON_BIN" -m twine upload dist/*
