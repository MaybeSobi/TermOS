#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '\r\n' < "$ROOT_DIR/tpm/VERSION")"
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "Invalid TPM version: $VERSION" >&2; exit 1; }
OUT="$ROOT_DIR/dist"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
NAME="TermOS-TPM-$VERSION"
mkdir -p "$STAGE/$NAME/tpm" "$STAGE/$NAME/docs"
cp -a "$ROOT_DIR/tpm/tpm"/*.py "$STAGE/$NAME/tpm/"
cp -a "$ROOT_DIR/tpm/README.md" "$ROOT_DIR/tpm/pyproject.toml" "$ROOT_DIR/tpm/VERSION" "$STAGE/$NAME/"
cp -a "$ROOT_DIR/docs/TPK_FORMAT.md" "$STAGE/$NAME/docs/"

mkdir -p "$STAGE/$NAME/tests"
find "$ROOT_DIR/tpm/tests" -maxdepth 1 -type f -name '*.py' \
  -exec cp -a {} "$STAGE/$NAME/tests/" \;

cp -a "$ROOT_DIR/LICENSE" "$STAGE/$NAME/"
mkdir -p "$OUT"
tar -czf "$OUT/$NAME.tar.gz" -C "$STAGE" "$NAME"
(
  cd "$OUT"
  sha256sum "$NAME.tar.gz" > "$NAME.tar.gz.sha256"
)
echo "Created: $OUT/$NAME.tar.gz"
cat "$OUT/$NAME.tar.gz.sha256"
