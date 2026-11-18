#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ "${EUID}" -ne 0 ]]; then
    if ! command -v sudo >/dev/null 2>&1; then
        echo "ERROR: live-build must run as root; install sudo or run as root." >&2
        exit 1
    fi
    exec sudo -E "$0" "$@"
fi

command -v lb >/dev/null 2>&1 || {
    echo "ERROR: live-build is not installed. See docs/BUILDING.md." >&2
    exit 1
}

lb config
lb build

ISO="$ROOT_DIR/live-image-amd64.hybrid.iso"
if [[ ! -s "$ISO" ]]; then
    echo "ERROR: live-build completed but expected ISO was not found: $ISO" >&2
    exit 1
fi

sha256sum "$ISO" | tee "$ISO.sha256"
echo "Build completed: $ISO"
