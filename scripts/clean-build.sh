#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ "${EUID}" -ne 0 ]]; then
    exec sudo -E "$0" "$@"
fi

command -v lb >/dev/null 2>&1 || {
    echo "ERROR: live-build is not installed." >&2
    exit 1
}

lb clean --purge
