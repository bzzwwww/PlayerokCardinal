#!/usr/bin/env bash
set -euo pipefail

APP_NAME="PlayerokCardinal"
APP_VERSION="__APP_VERSION__"
DEFAULT_REPO="__GITHUB_REPO__"
DEFAULT_REF="__GITHUB_REF__"

GITHUB_REPO="${DEFAULT_REPO}"
GITHUB_REF="${DEFAULT_REF}"
BOT_USER=""
INSTALL_DIR=""
SKIP_SERVICE="0"

usage() {
  cat <<EOF
Usage: sudo bash install-ubuntu.sh [options]

Options:
  --repo owner/repo   GitHub repository slug.
  --ref ref           Git tag or release ref, for example v${APP_VERSION}.
  --user username     Linux user for the bot.
  --dir path          Custom installation directory.
  --skip-service      Do not install or start systemd service.
  --help              Show this help.
EOF
}

info() {
  printf '[INFO] %s\n' "$1"
}

fail() {
  printf '[ERROR] %s\n' "$1" >&2
  exit 1
}

run_as_bot_user() {
  runuser -u "${BOT_USER}" -- "$@"
}

run_as_bot_shell() {
  runuser -u "${BOT_USER}" -- bash -lc "$1"
}

download_file() {
  local url="$1"
  local output="$2"

  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$url" -o "$output"
    return $?
  fi

  if command -v wget >/dev/null 2>&1; then
    wget -qO "$output" "$url"
    return $?
  fi

  return 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      GITHUB_REPO="${2:-}"
      shift 2
      ;;
    --ref)
      GITHUB_REF="${2:-}"
      shift 2
      ;;
    --user)
      BOT_USER="${2:-}"
      shift 2
      ;;
    --dir)
      INSTALL_DIR="${2:-}"
      shift 2
      ;;
    --skip-service)
      SKIP_SERVICE="1"
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      fail "Unknown argument: $1"
      ;;
  esac
done

if [[ "${EUID}" -ne 0 ]]; then
  fail "Run this installer as root: wget -qO- ... | sudo bash"
fi

if [[ -z "${GITHUB_REPO}" || "${GITHUB_REPO}" == "__GITHUB_REPO__" ]]; then
  fail "GitHub repository is not set. Pass --repo owner/repo or build release assets first."
fi

if [[ -z "${GITHUB_REF}" || "${GITHUB_REF}" == "__GITHUB_REF__" ]]; then
  GITHUB_REF="v${APP_VERSION}"
fi

if [[ -z "${BOT_USER}" ]]; then
  read -r -p "Linux user for ${APP_NAME} [playerok]: " BOT_USER
  BOT_USER="${BOT_USER:-playerok}"
fi

if ! id "${BOT_USER}" >/dev/null 2>&1; then
  info "Creating user ${BOT_USER}"
  useradd -m -s /bin/bash "${BOT_USER}"
fi

HOME_DIR="$(eval echo "~${BOT_USER}")"
INSTALL_DIR="${INSTALL_DIR:-${HOME_DIR}/${APP_NAME}}"
VENV_DIR="${HOME_DIR}/pyvenv"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

info "Installing system packages"
apt-get update
apt-get install -y python3 python3-venv python3-pip curl wget tar

ASSET_URL="https://github.com/${GITHUB_REPO}/releases/download/${GITHUB_REF}/${APP_NAME}-${APP_VERSION}-linux.tar.gz"
TAG_ARCHIVE_URL="https://github.com/${GITHUB_REPO}/archive/refs/tags/${GITHUB_REF}.tar.gz"
ARCHIVE_PATH="${TMP_DIR}/${APP_NAME}.tar.gz"

info "Downloading release package"
if ! download_file "${ASSET_URL}" "${ARCHIVE_PATH}"; then
  info "Release asset not found, trying tag archive"
  download_file "${TAG_ARCHIVE_URL}" "${ARCHIVE_PATH}" || fail "Failed to download release package."
fi

mkdir -p "${TMP_DIR}/extract"
tar -xzf "${ARCHIVE_PATH}" -C "${TMP_DIR}/extract"
SRC_DIR="$(find "${TMP_DIR}/extract" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
[[ -n "${SRC_DIR}" ]] || fail "Failed to unpack release package."

info "Installing files to ${INSTALL_DIR}"
rm -rf "${INSTALL_DIR}"
mkdir -p "$(dirname "${INSTALL_DIR}")"
cp -R "${SRC_DIR}" "${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}/configs" "${INSTALL_DIR}/logs" "${INSTALL_DIR}/storage/cache" "${INSTALL_DIR}/storage/products" "${INSTALL_DIR}/plugins"
: > "${INSTALL_DIR}/configs/auto_delivery.cfg"
: > "${INSTALL_DIR}/configs/auto_response.cfg"
chown -R "${BOT_USER}:${BOT_USER}" "${INSTALL_DIR}"

if [[ ! -d "${VENV_DIR}" ]]; then
  info "Creating Python virtual environment"
  run_as_bot_user python3 -m venv "${VENV_DIR}"
fi

info "Installing Python dependencies"
run_as_bot_user "${VENV_DIR}/bin/python" -m pip install --upgrade pip setuptools wheel
run_as_bot_user "${VENV_DIR}/bin/python" -m pip install -r "${INSTALL_DIR}/requirements.txt"

if [[ ! -f "${INSTALL_DIR}/configs/_main.cfg" ]]; then
  info "Launching first setup"
  run_as_bot_shell "cd '${INSTALL_DIR}' && '${VENV_DIR}/bin/python' main.py"
fi

if [[ "${SKIP_SERVICE}" != "1" ]]; then
  info "Installing systemd service"
  ln -sf "${INSTALL_DIR}/PlayerokCardinal@.service" /etc/systemd/system/PlayerokCardinal@.service
  systemctl daemon-reload
  systemctl enable "PlayerokCardinal@${BOT_USER}.service"
  systemctl restart "PlayerokCardinal@${BOT_USER}.service"
  info "Service started: PlayerokCardinal@${BOT_USER}.service"
  info "Logs: journalctl -u PlayerokCardinal@${BOT_USER}.service -f"
else
  info "Service installation skipped"
  info "Manual start: sudo -u ${BOT_USER} ${VENV_DIR}/bin/python ${INSTALL_DIR}/main.py"
fi
