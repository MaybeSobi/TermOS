#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
BR_VERSION="2025.02.19"

SRC_DIR="$ROOT_DIR/src"
BR_DIR="$SRC_DIR/buildroot-$BR_VERSION"
DOWNLOAD_DIR="$ROOT_DIR/downloads"
BUILD_DIR="$ROOT_DIR/build"

ARCHIVE="$DOWNLOAD_DIR/buildroot-$BR_VERSION.tar.xz"
URL="https://buildroot.org/downloads/buildroot-$BR_VERSION.tar.xz"

mkdir -p "$SRC_DIR" "$DOWNLOAD_DIR" "$BUILD_DIR"

if [[ ! -f "$BR_DIR/Makefile" ]]; then
    if [[ ! -f "$ARCHIVE" ]]; then
        echo "Downloading Buildroot $BR_VERSION..."
        curl -fL --retry 3 "$URL" -o "$ARCHIVE"
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

make O="$BUILD_DIR" -j"${JOBS:-$(nproc)}"

ISO="$BUILD_DIR/images/rootfs.iso9660"

if [[ ! -s "$ISO" ]]; then
    echo "ERROR: Build finished but ISO was not found." >&2
    exit 1
fi

echo
echo "Build completed successfully."
ls -lh "$ISO"
sha256sum "$ISO"
