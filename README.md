# TermOS

TermOS is an experimental, terminal-first Linux distribution proof of concept.

Version 0.1 focuses on a bootable Live ISO, a Python dashboard, a shell,
and basic networking.

## Status

- UEFI boot tested in QEMU.
- Python dashboard and shell tested.
- VirtIO networking tested in QEMU.
- DHCP, DNS resolution, and internet connectivity tested in QEMU.
- Physical USB boot has not yet been verified.
- Physical hardware compatibility has not yet been verified.

## Components

- Build system: Buildroot 2025.02.19
- Linux kernel: 6.12.27
- Architecture: x86_64
- Boot mode: UEFI
- Interface: terminal and Python dashboard

## Host requirements

On Debian-based Linux systems, install the required build tools:

```bash
sudo apt update
sudo apt install build-essential bc bison flex gawk git patch perl \
  python3 rsync file cpio unzip wget curl xz-utils libncurses-dev \
  libssl-dev libelf-dev qemu-system-x86 ovmf
```

## Build

From the TermOS project directory:

```bash
./scripts/build.sh
```

The generated ISO should be located at:

```text
build/images/rootfs.iso9660
```

Set `JOBS` to limit parallel compilation:

```bash
JOBS=2 ./scripts/build.sh
```

## Run in QEMU

```bash
./scripts/run-qemu.sh
```

The runner uses Q35, OVMF UEFI firmware, 1 GiB RAM, and a VirtIO network
adapter with QEMU user-mode networking.

The runner requires QEMU and OVMF to be installed. Firmware paths can be
overridden with the `OVMF_CODE` and `OVMF_VARS_TEMPLATE` environment variables.

## Networking

DHCP, DNS resolution, and outbound IP connectivity have been tested in QEMU.
This does not guarantee support for every physical network adapter.

## USB boot

Booting from a physical USB drive has not yet been verified. Before attempting
it, confirm that the ISO is suitable for direct USB imaging. Writing an image
to a USB drive can erase existing data.

## Licensing

TermOS includes third-party components such as Buildroot, Linux, BusyBox,
GRUB, and Python. Each component retains its own license and redistribution
terms. Review and include the required notices before publishing a binary
release.
