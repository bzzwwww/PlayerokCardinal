#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_INSTALLER="${SCRIPT_DIR}/install-ubuntu.sh"

if [[ -f "${LOCAL_INSTALLER}" ]]; then
  exec bash "${LOCAL_INSTALLER}" "$@"
fi

INSTALL_URL="https://raw.githubusercontent.com/__GITHUB_REPO__/__GITHUB_REF__/install-ubuntu.sh"
TMP_FILE="$(mktemp)"
trap 'rm -f "${TMP_FILE}"' EXIT

if command -v curl >/dev/null 2>&1; then
  curl -fsSL "${INSTALL_URL}" -o "${TMP_FILE}"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "${TMP_FILE}" "${INSTALL_URL}"
else
  echo "curl or wget is required." >&2
  exit 1
fi

exec bash "${TMP_FILE}" "$@"
