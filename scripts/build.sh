#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

# Prevent Git from detecting the parent TermOS repository as Buildroot.
export GIT_CEILING_DIRECTORIES="$ROOT_DIR"

BR_VERSION="2025.02.19"
SRC_DIR="$ROOT_DIR/src"
BR_DIR="$SRC_DIR/buildroot-$BR_VERSION"
DOWNLOAD_DIR="$ROOT_DIR/downloads"
BUILD_DIR="$ROOT_DIR/build"

ARCHIVE="$DOWNLOAD_DIR/buildroot-$BR_VERSION.tar.xz"
PARTIAL_ARCHIVE="$ARCHIVE.part"
URL="https://buildroot.org/downloads/buildroot-$BR_VERSION.tar.xz"

JOBS_COUNT="${JOBS:-$(nproc)}"
if [[ ! "$JOBS_COUNT" =~ ^[1-9][0-9]*$ ]]; then
    echo "ERROR: JOBS must be a positive integer; received: $JOBS_COUNT" >&2
    exit 2
fi

mkdir -p "$SRC_DIR" "$DOWNLOAD_DIR" "$BUILD_DIR"

# A previous interrupted download must never be mistaken for a valid archive.
if [[ -f "$ARCHIVE" ]] && ! xz -t "$ARCHIVE" >/dev/null 2>&1; then
    echo "WARNING: Existing Buildroot archive is corrupt; downloading it again." >&2
    rm -f "$ARCHIVE"
fi

if [[ ! -f "$BR_DIR/Makefile" ]]; then
    if [[ ! -f "$ARCHIVE" ]]; then
        echo "Downloading Buildroot $BR_VERSION..."
        rm -f "$PARTIAL_ARCHIVE"
        curl --fail --location --retry 3 --retry-delay 2 --retry-all-errors \
            "$URL" --output "$PARTIAL_ARCHIVE"
        xz -t "$PARTIAL_ARCHIVE"
        mv -- "$PARTIAL_ARCHIVE" "$ARCHIVE"
    fi

    echo "Extracting Buildroot $BR_VERSION..."
    tar -xJf "$ARCHIVE" -C "$SRC_DIR"
fi

if [[ ! -f "$BR_DIR/Makefile" ]]; then
    echo "ERROR: Buildroot source not found at $BR_DIR" >&2
    exit 1
fi

cd "$BR_DIR"

make O="$BUILD_DIR" \
    BR2_DEFCONFIG="$ROOT_DIR/configs/termos_defconfig" \
    defconfig

make O="$BUILD_DIR" -j"$JOBS_COUNT"

ISO="$BUILD_DIR/images/rootfs.iso9660"

if [[ ! -s "$ISO" ]]; then
    echo "ERROR: Build finished but ISO was not found." >&2
    exit 1
fi

echo
echo "Build completed successfully."
ls -lh "$ISO"
sha256sum "$ISO"
