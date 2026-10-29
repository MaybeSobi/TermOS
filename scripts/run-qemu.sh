#!/usr/bin/env bash
set -euo pipefail

TERMOS_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ISO="$TERMOS_DIR/build/images/rootfs.iso9660"

OVMF_CODE="${OVMF_CODE:-/usr/share/OVMF/OVMF_CODE_4M.fd}"
OVMF_VARS_TEMPLATE="${OVMF_VARS_TEMPLATE:-/usr/share/OVMF/OVMF_VARS_4M.fd}"
OVMF_VARS="$TERMOS_DIR/build/OVMF_VARS_TermOS.fd"

if [[ ! -f "$ISO" ]]; then
    echo "ERROR: TermOS ISO not found: $ISO" >&2
    exit 1
fi

if [[ ! -f "$OVMF_CODE" ]]; then
    echo "ERROR: OVMF firmware not found: $OVMF_CODE" >&2
    exit 1
fi

if [[ ! -f "$OVMF_VARS" ]]; then
    if [[ ! -f "$OVMF_VARS_TEMPLATE" ]]; then
        echo "ERROR: OVMF variables template not found: $OVMF_VARS_TEMPLATE" >&2
        exit 1
    fi
    cp "$OVMF_VARS_TEMPLATE" "$OVMF_VARS"
fi

exec qemu-system-x86_64 \
    -machine q35 \
    -m 1024 \
    -drive "if=pflash,format=raw,unit=0,readonly=on,file=$OVMF_CODE" \
    -drive "if=pflash,format=raw,unit=1,file=$OVMF_VARS" \
    -cdrom "$ISO" \
    -boot order=d,menu=on \
    -nic user,model=virtio-net-pci \
    -no-reboot \
    "$@"
