#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ -x "${APP_DIR}/venv/bin/python" ]]; then
  PYTHON_BIN="${APP_DIR}/venv/bin/python"
elif [[ -x "${APP_DIR}/.venv/bin/python" ]]; then
  PYTHON_BIN="${APP_DIR}/.venv/bin/python"
else
  PYTHON_BIN="python3"
fi

cd "${APP_DIR}"
exec "${PYTHON_BIN}" "${APP_DIR}/main.py"
