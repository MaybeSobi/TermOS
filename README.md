# TermOS

<div align="center">

**A terminal-first Linux distribution experiment.**

A small x86_64 Linux system built with Buildroot, featuring a Python terminal dashboard, an interactive shell, networking, and the experimental TermOS Package Manager (TPM).

[![Latest release](https://img.shields.io/github/v/release/MaybeSobi/TermOS?label=release)](https://github.com/MaybeSobi/TermOS/releases/tag/v0.2.0)
![Architecture](https://img.shields.io/badge/architecture-x86__64-blue)
![Boot](https://img.shields.io/badge/boot-UEFI-informational)
![TermOS-authored files](https://img.shields.io/badge/TermOS-authored%20files-MIT-green)

[Download TermOS 0.2.0](https://github.com/MaybeSobi/TermOS/releases/tag/v0.2.0) · [Build from source](#build-from-source) · [Release checklist](docs/COMPLIANCE_CHECKLIST_0.2.0.md)

</div>

> [!WARNING]
> **TermOS is an experimental preview, not a production operating system.** The v0.2.0 ISO passed the automated UEFI/QEMU boot workflow, was manually boot-tested in VMware Workstation Pro 17 using UEFI firmware, and has also been reported to boot successfully on one physical computer. This is a single-machine smoke test; broad hardware compatibility and physical USB boot are not yet verified.

> [!IMPORTANT]
> The v0.2.0 release is an experimental preview. Its exact Buildroot manifests contain 10 target and 38 host/build-tool entries. CI collected 86 declared license files and reported successful SHA-256 checks for all 86. The package inventory and multi-license review are documented, but this technical evidence is **not a legal-compliance certification**. The corresponding-source publishing workflow is configured; treat the source package as published only after its assets appear on the [release page](https://github.com/MaybeSobi/TermOS/releases/tag/v0.2.0). See the [component inventory](docs/THIRD_PARTY_COMPONENTS_0.2.0.csv), [license review](docs/THIRD_PARTY_LICENSE_REVIEW_0.2.0.md), and [compliance checklist](docs/COMPLIANCE_CHECKLIST_0.2.0.md).

## At a glance

| Item | Details |
| --- | --- |
| Latest preview | [v0.2.0 — Experimental Preview](https://github.com/MaybeSobi/TermOS/releases/tag/v0.2.0) |
| Architecture | x86_64 |
| Boot mode | UEFI |
| Virtualization testing | QEMU (automated CI) and VMware Workstation Pro 17 (manual boot test) |
| Physical hardware test | One successful boot reported on a physical computer (single-machine smoke test) |
| Build system | Buildroot 2025.02.19 |
| Linux kernel | 6.12.27 |
| Userspace | BusyBox and Python 3 |
| Interface | Terminal, shell, and Python dashboard |
| Package management | Experimental TPM with signed repository metadata |

## What's working

- Automated ISO build in GitHub Actions
- UEFI boot reaching the init process in QEMU
- VirtIO networking in the CI QEMU environment
- Python dashboard and interactive shell
- TPM unit tests in the required ISO workflow
- TPM package metadata signature verification and guarded system-root operations (experimental)

### Virtual machine testing

The v0.2.0 ISO has been tested in both environments:

- **QEMU:** automated UEFI boot validation in GitHub Actions.
- **VMware Workstation Pro 17:** manual UEFI boot test using a newly created virtual machine.

The VMware result is a manual smoke test, not an automated compatibility guarantee. When testing in VMware, attach the ISO as a virtual CD/DVD device and use UEFI firmware.

### Physical hardware testing

A successful boot has been reported on one physical computer. This is an initial, single-machine smoke test only and does not establish general compatibility with all physical hardware.

### Known limitations

- Physical USB boot has **not** been verified.
- Broad compatibility with physical hardware has **not** been established; only the single older-PC boot described above has been reported.
- QEMU networking does not guarantee support for every physical network adapter.
- TPM is experimental; system-root package operations should only be tested in a disposable environment.
- The system is a proof of concept and is not intended for production use.

## Download TermOS 0.2.0

Open the [**TermOS v0.2.0 release page**](https://github.com/MaybeSobi/TermOS/releases/tag/v0.2.0) and download:

- `TermOS-CI-x86_64.iso`
- `SHA256SUMS`

Verify the downloaded ISO on Linux:

```bash
sha256sum --check SHA256SUMS
```

The expected SHA-256 for `TermOS-CI-x86_64.iso` is:

```text
4b09ad178f3eaf202ab4e26a1c6b60c83eb4d869074de4352e1be92ba56da565
```

Always verify the checksum after downloading. A matching checksum confirms file integrity against the published checksum; it does not establish that the image is safe, production-ready, or legally cleared for redistribution.

### USB note

Physical USB boot has not been verified. Writing an image to a USB drive can erase existing data. Use a spare drive and verify its identity before writing; do not use a drive containing files you need.

## Build from source

### Host requirements

On Debian-based Linux systems, install the build and QEMU test dependencies:

```bash
sudo apt update
sudo apt install -y \
  build-essential bc bison flex gawk git patch perl python3 python3-pytest \
  rsync file cpio unzip wget curl xz-utils libncurses-dev libssl-dev \
  libelf-dev qemu-system-x86 ovmf xorriso
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

The build script downloads Buildroot 2025.02.19 and uses the checked-in TermOS configuration and board files. Review the Buildroot version and configuration before relying on a build for release purposes.

### Run in QEMU

```bash
./scripts/run-qemu.sh
```

The runner uses Q35, OVMF UEFI firmware, 1 GiB RAM, and a VirtIO network adapter with QEMU user-mode networking. QEMU and OVMF must be installed. Firmware paths can be overridden with the `OVMF_CODE` and `OVMF_VARS_TEMPLATE` environment variables.

## Licensing, notices, and source availability

The repository's MIT `LICENSE` applies to TermOS-authored project files only, subject to the rights of the relevant contributors. It does **not** relicense Linux, Buildroot, BusyBox, GRUB, OpenSSL, Python, or any other third-party component. Each third-party component keeps its own license and redistribution conditions.

Buildroot's legal information is generated in CI for the release build. To reproduce it, run the following from the Buildroot source directory, using the same output directory as the TermOS build:

```bash
cd ~/TermOS/src/buildroot-2025.02.19
make O="$HOME/TermOS/build" legal-info
```

Review the generated material under `build/legal-info/`:

- `README` — warnings and notes about material Buildroot could not produce
- `manifest.csv` — target packages and their declared license metadata
- `host-manifest.csv` — host/build-time packages and their declared license metadata
- `licenses/` and `host-licenses/` — license texts collected by Buildroot
- `sources/` and `host-sources/` — source archives collected by Buildroot, where available
- `buildroot.config` — the configuration used for the build

A compact review bundle is generated by `scripts/generate-legal-review.py` in CI. It preserves the manifests, README, configuration, collected license texts, and a source-archive index. CI also generates a CycloneDX SBOM from Buildroot's `show-info` output. The corresponding-source workflow is configured to package the exact TermOS v0.2.0 source snapshot, the complete legal-info archive, Buildroot 2025.02.19 source and detached signature, the SBOM, compliance documents, and SHA-256 checksums.

**Important:** Buildroot states that `legal-info` is based on package recipe metadata, may be incomplete or inaccurate, and does not determine exactly what must be published. Buildroot also documents that its own source and some toolchain material may need to be collected separately. Human review of the exact package versions, license texts, patches, source archives, and applicable obligations remains necessary. See:

- [Third-party license review — v0.2.0](docs/THIRD_PARTY_LICENSE_REVIEW_0.2.0.md)
- [Compliance and release checklist — v0.2.0](docs/COMPLIANCE_CHECKLIST_0.2.0.md)
- [Third-party notices index](docs/THIRD_PARTY_NOTICES.md)
- [Buildroot manual — legal notice and licensing](https://buildroot.org/downloads/manual/manual.html#legal-notice-and-licensing)

Do not treat the generated inventory as a legal certification. Any formal legal sign-off must come from a qualified reviewer.

## TermOS Package Manager (TPM)

TermOS includes an experimental Python package manager with `.tpk` packages, local dependency resolution, signed repository indexes (Ed25519), and guarded system-root mode.

See [TPM documentation](tpm/README.md) and the [TPK format](docs/TPK_FORMAT.md).

Run the guest smoke test inside a disposable QEMU or VMware TermOS instance:

```sh
/usr/share/termos/tests/tpm-smoke.sh
```

To prepare a signed, harmless data-only test package pair on the host, run `./scripts/prepare-tpm-system-test-repo.sh`, copy the printed repository folder into a disposable VM, and then run:

```sh
/usr/share/termos/tests/tpm-system-root-test.sh /path/to/tpm-system-root-repo
```

The script requests confirmation for live-root install, upgrade, and removal, and checks that the test package is removed at the end.

System-root package operations are root-only, require a signed repository and explicit confirmation, and may not persist across reboot in live-ISO mode.

## Contributing

Issues and pull requests are welcome. Please include reproduction steps, relevant logs, and the exact TermOS release or commit you tested.

---

<div align="center">

**TermOS is an experiment. Test carefully, verify downloads, and share feedback through GitHub issues.**

</div>
