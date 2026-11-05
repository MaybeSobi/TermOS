#!/bin/sh
set -eu

REPO_ROOT="${1:-}"
[ -n "$REPO_ROOT" ] || { echo "Usage: $0 /path/to/tpm-system-root-repo" >&2; exit 2; }
[ "$(id -u)" = "0" ] || { echo "Run this test as root inside the disposable TermOS VM." >&2; exit 1; }
[ -s /etc/termos-release ] || { echo "Not a TermOS system image." >&2; exit 1; }
[ -s /etc/termos/repository-ed25519.pub ] || { echo "Trusted repository public key missing." >&2; exit 1; }

V1="$REPO_ROOT/v1"
V2="$REPO_ROOT/v2"
P1="$(find "$V1" -maxdepth 1 -type f -name '*.tpk' | head -n 1)"
P2="$(find "$V2" -maxdepth 1 -type f -name '*.tpk' | head -n 1)"
[ -n "$P1" ] && [ -s "$P1" ] || { echo "v1 package missing" >&2; exit 1; }
[ -n "$P2" ] && [ -s "$P2" ] || { echo "v2 package missing" >&2; exit 1; }

TARGET="/usr/share/termos/tpm-system-root-smoke/installed.txt"
echo "This test writes only one disposable text file under /usr/share/termos."
echo "It installs v1, upgrades to v2, verifies, and then removes the test package."

/usr/bin/tpm install "$P1" --system --repo "$V1"
/usr/bin/tpm verify tpm-system-root-smoke --system
[ -s "$TARGET" ] || { echo "Installed payload missing" >&2; exit 1; }
grep -q 'Version 1' "$TARGET" || { echo "Unexpected v1 payload" >&2; exit 1; }

/usr/bin/tpm upgrade "$P2" --system --repo "$V2"
/usr/bin/tpm verify tpm-system-root-smoke --system
grep -q 'Version 2' "$TARGET" || { echo "Upgrade payload not present" >&2; exit 1; }

/usr/bin/tpm remove tpm-system-root-smoke --system
[ ! -e "$TARGET" ] || { echo "Package payload remains after removal" >&2; exit 1; }
/usr/bin/tpm verify --system

echo "TPM SYSTEM-ROOT INSTALL / UPGRADE / REMOVE TEST PASSED"
