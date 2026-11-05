#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PRIVATE_KEY="$ROOT_DIR/keys/termos-repo-private.pem"
[[ -s "$PRIVATE_KEY" ]] || { echo "Missing private repository signing key: $PRIVATE_KEY" >&2; exit 1; }
command -v openssl >/dev/null 2>&1 || { echo "Host openssl is required" >&2; exit 1; }
mkdir -p "$ROOT_DIR/dist"
REPO_ROOT="$(mktemp -d "$ROOT_DIR/dist/tpm-system-root-repo.XXXXXX")"
mkdir -p "$REPO_ROOT/v1" "$REPO_ROOT/v2"
ARCH="$(uname -m)"

for spec in "1.0.0:Version 1" "1.1.0:Version 2"; do
    version="${spec%%:*}"
    label="${spec#*:}"
    source="$(mktemp -d)"
    mkdir -p "$source/usr/share/termos/tpm-system-root-smoke"
    printf 'TermOS TPM system-root integration test: %s\n' "$label" \
        > "$source/usr/share/termos/tpm-system-root-smoke/installed.txt"
    output="$REPO_ROOT/v${version%%.*}/tpm-system-root-smoke-${version}-${ARCH}.tpk"
    # v1 and v2 are stored in separate signed indexes for an unambiguous upgrade test.
    if [[ "$version" == "1.0.0" ]]; then output="$REPO_ROOT/v1/tpm-system-root-smoke-${version}-${ARCH}.tpk"; repo="$REPO_ROOT/v1";
    else output="$REPO_ROOT/v2/tpm-system-root-smoke-${version}-${ARCH}.tpk"; repo="$REPO_ROOT/v2"; fi
    python3 -m tpm.tpm build "$source" \
        --name tpm-system-root-smoke --version "$version" --arch "$ARCH" \
        --description "Disposable TermOS system-root integration test" \
        --output "$output"
    rm -rf "$source"
    python3 -m tpm.tpm repo index "$repo" \
        --name "TermOS TPM System Root Test $version"
    python3 -m tpm.tpm repo sign "$repo/repository.json" --private-key "$PRIVATE_KEY"
    python3 -m tpm.tpm repo verify "$repo/repository.json" \
        --public-key "$ROOT_DIR/keys/termos-repo-public.pem"
done

echo "Signed system-root test repositories created:"
echo "  v1: $REPO_ROOT/v1"
echo "  v2: $REPO_ROOT/v2"
echo "Copy the whole directory to a disposable TermOS QEMU/VMware guest."
echo "The private key was used on the host only and is not included in either repository."
