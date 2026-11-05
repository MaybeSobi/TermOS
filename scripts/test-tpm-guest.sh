#!/bin/sh
set -eu

TPM="${TPM:-/usr/bin/tpm}"
WORK="$(mktemp -d /tmp/termos-tpm-smoke.XXXXXX)"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT HUP INT TERM

fail() { echo "[FAIL] $*" >&2; exit 1; }
echo "===== TERMOS TPM GUEST SMOKE TEST ====="

"$TPM" --help >/dev/null || fail "TPM CLI did not start"
"$TPM" repo --help >/dev/null || fail "TPM repository CLI did not start"
command -v openssl >/dev/null 2>&1 || fail "OpenSSL CLI is missing"
openssl version
python3 -c 'import ssl, tarfile, hashlib, json; print("Python runtime modules: OK")' \
    || fail "Required Python runtime modules are missing"
[ -s /etc/termos/repository-ed25519.pub ] || fail "Trusted repository public key is missing"

mkdir -p "$WORK/v1/usr/bin" "$WORK/v2/usr/bin"
cat > "$WORK/v1/usr/bin/tpm-guest-smoke" <<'EOF'
#!/bin/sh
echo "TPM guest package version 1"
EOF
cat > "$WORK/v2/usr/bin/tpm-guest-smoke" <<'EOF'
#!/bin/sh
echo "TPM guest package version 2"
EOF
chmod 0755 "$WORK/v1/usr/bin/tpm-guest-smoke" "$WORK/v2/usr/bin/tpm-guest-smoke"

ARCH="$(uname -m)"
"$TPM" build "$WORK/v1" --name tpm-guest-smoke --version 1.0.0 \
    --arch "$ARCH" --description "TermOS VM smoke test" -o "$WORK/tpm-guest-smoke-1.0.0.tpk"
"$TPM" build "$WORK/v2" --name tpm-guest-smoke --version 1.1.0 \
    --arch "$ARCH" --description "TermOS VM smoke test" -o "$WORK/tpm-guest-smoke-1.1.0.tpk"

ROOT="$WORK/root"
"$TPM" init-root --root "$ROOT"
"$TPM" install "$WORK/tpm-guest-smoke-1.0.0.tpk" --root "$ROOT"
[ "$("$ROOT/usr/bin/tpm-guest-smoke")" = "TPM guest package version 1" ] || fail "Initial package execution failed"
"$TPM" upgrade "$WORK/tpm-guest-smoke-1.1.0.tpk" --root "$ROOT"
"$TPM" verify --root "$ROOT"
[ "$("$ROOT/usr/bin/tpm-guest-smoke")" = "TPM guest package version 2" ] || fail "Upgraded package execution failed"
"$TPM" remove tpm-guest-smoke --root "$ROOT"
"$TPM" verify --root "$ROOT"
[ ! -e "$ROOT/usr/bin/tpm-guest-smoke" ] || fail "Package file remained after removal"

echo "[PASS] Sandbox install, upgrade, verify, execution, and remove"
if [ "$(id -u)" = "0" ]; then
    "$TPM" --system list >/dev/null || fail "TermOS system-root read-only check failed"
    echo "[PASS] Guarded TermOS system-root read-only check"
else
    echo "[SKIP] System-root check requires root; sandbox tests passed"
fi

echo "TERMOS TPM GUEST SMOKE TEST PASSED"
