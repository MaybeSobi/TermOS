# TermOS

<div align="center">

**A terminal-first Linux distribution experiment.**

A small, Buildroot-based Linux system with a Python dashboard, an interactive shell, and basic networking.

[![Release](https://img.shields.io/github/v/release/MaybeSobi/TermOS?label=release)](https://github.com/MaybeSobi/TermOS/releases/tag/v0.1.0)
![Architecture](https://img.shields.io/badge/architecture-x86__64-blue)
![Boot](https://img.shields.io/badge/boot-UEFI-informational)
![Project files license](https://img.shields.io/badge/project%20files-MIT-green)

[Download v0.1.0](https://github.com/MaybeSobi/TermOS/releases/tag/v0.1.0) · [Build from source](#build-from-source) · [Release checklist](docs/RELEASE_CHECKLIST.md)

</div>

> [!WARNING]
> **TermOS is an experimental preview, not a production operating system.** UEFI boot, the terminal dashboard, shell, and networking have been tested in QEMU and VMware. Physical USB boot and compatibility with real hardware remain unverified.

> [!IMPORTANT]
> The v0.1.0 ISO is currently publicly downloadable, but the third-party redistribution review is not complete. Buildroot's `legal-info` output warns that Buildroot's own source was not saved and that other material may be missing. Required source and notice obligations must be resolved before mirroring or redistributing the ISO.

## At a glance

| Item | Details |
| --- | --- |
| Latest preview | [v0.1.0 — Experimental Preview](https://github.com/MaybeSobi/TermOS/releases/tag/v0.1.0) |
| Architecture | x86_64 |
| Boot mode | UEFI |
| Build system | Buildroot 2025.02.19 |
| Linux kernel | 6.12.27 |
| Userspace | BusyBox and Python 3.12.15 |
| Interface | Terminal, shell, and Python dashboard |

## What's working

- UEFI boot in QEMU and VMware
- Python terminal dashboard and interactive shell
- VirtIO networking in QEMU
- VMware virtual networking and internet connectivity in VMware
- DHCP, DNS resolution, and outbound connectivity have been observed in virtual machines

### Known limitations

- Physical USB boot has **not** been verified.
- Real-hardware compatibility has **not** been verified.
- QEMU networking tests do not guarantee support for every physical network adapter.
- The system is a proof of concept; it is not intended for production use.

## Download the preview

Get the currently published ISO from the [**TermOS v0.1.0 release page**](https://github.com/MaybeSobi/TermOS/releases/tag/v0.1.0).

**Important:** the newly tested VMware-compatible build has been verified locally, but has not yet been uploaded as a new release asset. Do not assume the existing v0.1.0 download is identical to that build. The new local image's SHA-256 is `fdf9986af5fb7fc835e1868220385de95d3aa0bdf88672fa5a4fffec4c1336d3`; the release page must be updated after the new image is published.

The existing v0.1.0 release asset is currently stored on GitHub as `rootfs.iso9660`. The commands below download it with a more descriptive local filename and verify its SHA-256 checksum.

```bash
curl -fL \
  https://github.com/MaybeSobi/TermOS/releases/download/v0.1.0/rootfs.iso9660 \
  -o TermOS-0.1.0-x86_64.iso

printf '%s  %s\n' \
  'cb6d60f6dacee9ec65d4f4681bace1f5f2971673087f318dcfe5b9383e7628f7' \
  'TermOS-0.1.0-x86_64.iso' | sha256sum --check
```

Expected result: `TermOS-0.1.0-x86_64.iso: OK`.

The checksum matches the SHA-256 digest reported by the published GitHub release asset. Always verify the checksum after downloading.

### USB note

Physical USB boot has not been verified. Before writing the ISO to a USB drive, check the image-writing method and remember that writing an image can erase existing data. Do not assume that USB boot works on every system.

## Build from source

### Host requirements

On Debian-based Linux systems, install the build tools:

```bash
sudo apt update
sudo apt install build-essential bc bison flex gawk git patch perl \
  python3 rsync file cpio unzip wget curl xz-utils libncurses-dev \
  libssl-dev libelf-dev qemu-system-x86 ovmf
```

### Build

From the TermOS project directory:

```bash
./scripts/build.sh
```

The generated ISO should be at:

```text
build/images/rootfs.iso9660
```

To limit parallel compilation:

```bash
JOBS=2 ./scripts/build.sh
```

### Run in QEMU

```bash
./scripts/run-qemu.sh
```

The runner uses Q35, OVMF UEFI firmware, 1 GiB RAM, and a VirtIO network adapter with QEMU user-mode networking. QEMU and OVMF must be installed. Firmware paths can be overridden with the `OVMF_CODE` and `OVMF_VARS_TEMPLATE` environment variables.

## Licensing and third-party software

The repository's MIT `LICENSE` applies to **TermOS-authored project files only**. It does not relicense the Linux kernel, Buildroot, BusyBox, GRUB, Python, or other third-party components; each component retains its own license and redistribution conditions.

Buildroot's legal information has been generated for the current build. To reproduce it, run the following from the Buildroot source directory, using the same output directory as the TermOS build:

```bash
cd ~/TermOS/src/buildroot-2025.02.19
make O="$HOME/TermOS/build" legal-info
```

Review the generated material under `build/legal-info/`:

- `README` — warnings and notes about missing material
- `manifest.csv` — target packages
- `host-manifest.csv` — host and build tools
- `licenses/` and `host-licenses/` — collected license texts
- `sources/` and `host-sources/` — source archives, where available
- `buildroot.config` — configuration used for the build

The current legal-info output explicitly warns that Buildroot's source code was not saved. Some other source or toolchain material may also be missing. A successful `legal-info` run is an inventory, **not a legal-compliance certification**. The applicable license terms, required notices, and corresponding-source obligations still need to be reviewed and satisfied before redistributing the ISO.

See the [v0.1.0 release checklist](docs/RELEASE_CHECKLIST.md) for the recorded status and remaining verification steps.

---

<div align="center">

**TermOS is an experiment. Test carefully, verify downloads, and share feedback through GitHub issues.**

</div>
