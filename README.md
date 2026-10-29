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

## Licensing and binary releases

The repository's MIT `LICENSE` applies to TermOS-authored project files; it
does not replace the licenses of bundled third-party software. TermOS includes
components such as Buildroot, Linux, BusyBox, GRUB, and Python, each with its
own applicable license and redistribution conditions.

Before distributing a binary ISO, generate and review Buildroot's legal
information using the same output directory as the build:

```bash
cd src/buildroot-2025.02.19
make O="$HOME/TermOS/build" legal-info
```

Review these generated files and directories under `build/legal-info/`:

- `README` for Buildroot's notes and any warnings about missing material.
- `manifest.csv` for target packages included in the image.
- `host-manifest.csv` for host/build tools and their license information.
- `licenses/` and `host-licenses/` for collected license texts.
- `sources/` and `host-sources/` for source archives, where available.
- `buildroot.config` for the configuration used to build the image.

Buildroot reports that its own source code was not saved in this legal-info
output and must be collected manually if needed to meet applicable obligations.
Some other source or toolchain materials may also be missing for technical
reasons. A successful `legal-info` run is an inventory, not a guarantee that
all redistribution requirements have been satisfied. Review the applicable
licenses and provide required notices and corresponding source materials before
redistributing the ISO.

See [the v0.1.0 release checklist](docs/RELEASE_CHECKLIST.md) for the remaining
verification steps.

## Release

The v0.1.0 GitHub Release currently contains release notes but no ISO asset.
Physical USB boot and real-hardware compatibility have not been verified.
