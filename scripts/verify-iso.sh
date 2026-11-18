#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ISO="${1:-$ROOT_DIR/live-image-amd64.hybrid.iso}"

if [[ ! -s "$ISO" ]]; then
    echo "ERROR: ISO not found or empty: $ISO" >&2
    exit 1
fi

file "$ISO"
sha256sum "$ISO"
