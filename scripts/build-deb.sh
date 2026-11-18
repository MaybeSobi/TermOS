#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_VERSION="${TERMOS_PACKAGE_VERSION:-0.3.0~dev1}"
STAGING_DIR="$ROOT_DIR/.build/deb-root"
PACKAGE_DIR="$ROOT_DIR/config/packages.chroot"
PACKAGE_FILE="$PACKAGE_DIR/termos_${PACKAGE_VERSION}_all.deb"

command -v dpkg-deb >/dev/null 2>&1 || {
    echo "ERROR: dpkg-deb is required to build the TermOS Debian package." >&2
    exit 1
}

[[ "$PACKAGE_VERSION" =~ ^[0-9A-Za-z.+:~_-]+$ ]] || {
    echo "ERROR: invalid Debian package version: $PACKAGE_VERSION" >&2
    exit 2
}

rm -rf "$STAGING_DIR"
mkdir -p \
    "$STAGING_DIR/DEBIAN" \
    "$STAGING_DIR/usr/lib/python3/dist-packages" \
    "$STAGING_DIR/usr/bin" \
    "$PACKAGE_DIR"

cp -a "$ROOT_DIR/src/termos" "$STAGING_DIR/usr/lib/python3/dist-packages/"

cat > "$STAGING_DIR/DEBIAN/control" <<EOF
Package: termos
Version: $PACKAGE_VERSION
Section: admin
Priority: optional
Architecture: all
Depends: python3 (>= 3.11)
Maintainer: TermOS contributors
Description: TermOS command-line tools
 A minimal CLI entry point for the Debian-based TermOS generation.
EOF

cat > "$STAGING_DIR/usr/bin/termos" <<'EOF'
#!/usr/bin/python3
from termos.cli import main

raise SystemExit(main())
EOF
chmod 0755 "$STAGING_DIR/usr/bin/termos"

dpkg-deb --build --root-owner-group "$STAGING_DIR" "$PACKAGE_FILE"
echo "Built Debian package: $PACKAGE_FILE"
