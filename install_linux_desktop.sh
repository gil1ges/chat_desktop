#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
DESKTOP_DIR="${HOME}/.local/share/applications"
ICON_DIR="${HOME}/.local/share/icons/hicolor/scalable/apps"

mkdir -p "${DESKTOP_DIR}" "${ICON_DIR}"
cp "${APP_DIR}/gpt-desktop.desktop" "${DESKTOP_DIR}/gpt-desktop.desktop"
cp "${APP_DIR}/assets/chatgpt-icon.svg" "${ICON_DIR}/gpt-desktop.svg"
chmod +x "${APP_DIR}/run.sh"

sed -i "s|/home/viktor/Projects/gpt-desktop|${APP_DIR}|g" "${DESKTOP_DIR}/gpt-desktop.desktop"

chmod +x "${DESKTOP_DIR}/gpt-desktop.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "${DESKTOP_DIR}" || true
fi

echo "Installed desktop entry: ${DESKTOP_DIR}/gpt-desktop.desktop"
