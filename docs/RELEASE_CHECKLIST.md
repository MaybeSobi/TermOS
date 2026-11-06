# TermOS v0.2.0 — Release and Validation Checklist

This document records the published state of TermOS v0.2.0. Check an item only when the result is supported by a release artifact, CI run, or recorded test.

## Release identity

- [x] Version: `v0.2.0`
- [x] Release type: experimental preview
- [x] Build system: Buildroot `2025.02.19`
- [x] Linux kernel: `6.12.27`
- [x] Target architecture: `x86_64`
- [x] Boot mode: UEFI
- [x] Release tag: [v0.2.0](https://github.com/MaybeSobi/TermOS/releases/tag/v0.2.0)

## Published release assets

- [x] `TermOS-CI-x86_64.iso` — 44,107,776 bytes
- [x] `SHA256SUMS` — published with the release
- [x] `TermOS-Corresponding-Source-v0.2.0.tar.gz` — 470,346,600 bytes
- [x] `TermOS-Corresponding-Source-v0.2.0.tar.gz.sha256` — published with the source bundle
- [x] ISO SHA-256 recorded for this release:

  `4b09ad178f3eaf202ab4e26a1c6b60c83eb4d869074de4352e1be92ba56da565`

## CI and automated validation

- [x] Main ISO workflow completed successfully — run `42126043907`.
- [x] Source publisher workflow completed successfully — run `42126460206`.
- [x] Automated UEFI/QEMU boot validation passed.
- [x] Source bundle was generated and attached to the release.
- [x] Source bundle checksum file was generated and published.

## Manual boot validation

- [x] Maintainer-reported boot test in VMware Workstation Pro 17 using UEFI.
- [x] Maintainer-reported successful boot on one physical computer.
- [ ] Record the physical computer's exact model and hardware specifications.
- [ ] Record the physical test date, USB creation method, and boot settings.
- [ ] Repeat physical boot testing on additional hardware.
- [ ] Record results for networking, storage, keyboard, display, and shutdown/reboot on each tested device.

A successful boot on one physical computer is a useful smoke test, not a claim of broad hardware compatibility. Keep the test environment and observed results attached to the relevant release notes or issue.

## TPM validation status

TPM is experimental in v0.2.0. Its current documented capabilities include package archive validation, sandbox and guarded system-root operations, local repository dependency resolution, and Ed25519-signed repository index verification.

- [x] TPM test scripts are present in the source tree for core, security, install, remove, rollback, upgrade, dependency, and repository behavior.
- [x] Guest/system-root test scripts are present in the repository.
- [ ] Run and record the complete TPM test suite against the exact v0.2.0 source and release image.
- [ ] Record the tested package fixtures and repository key setup.
- [ ] Keep the documented v1 limitations visible: no maintainer-script execution and no symlink payload support.
- [ ] Do not describe HTTPS repository synchronization, key rotation, revocation, or repository freshness enforcement as supported in v0.2.0.

## Known limitations and release caveats

- TermOS v0.2.0 is an experimental UEFI ISO preview, not a full disk installer.
- Persistence across reboot depends on the boot and storage layout; do not promise persistent package installation or user changes in every live-ISO boot mode.
- TPM system-root operations modify the currently mounted root filesystem and must be tested in a disposable VM before use.
- TPM transaction tests cover injected software failures; they do not prove recovery from power loss, kernel panic, or sudden hardware failure.
- Hardware compatibility beyond the recorded test machines is not established.

## Third-party licensing and corresponding-source review

The v0.2.0 corresponding-source archive is published with the release. Publication of a source archive does not, by itself, establish that every third-party license obligation has been reviewed and satisfied.

- [ ] Generate Buildroot `legal-info` from the exact Buildroot output used to produce the v0.2.0 ISO.
- [ ] Review the resulting package manifest and license texts.
- [ ] Resolve or document missing-source warnings for all components that require corresponding source.
- [ ] Verify required copyright notices, license texts, and source-availability information.
- [ ] Record the review outcome and the location of the applicable notices/source materials.

Do not treat a successful `legal-info` run or the existence of the source bundle as legal approval. Complete the review before encouraging wider redistribution or mirroring.

## Reproducing the build

The release build uses Buildroot `2025.02.19`. From the TermOS repository root:

```bash
./scripts/build.sh
```

The build script downloads/extracts the pinned Buildroot version when needed and produces the ISO under:

```text
build/images/rootfs.iso9660
```

For legal information, run the following from the Buildroot source directory, using the same output directory as the release build:

```bash
cd src/buildroot-2025.02.19
make O="../../build" legal-info
```

Review the generated files under `build/legal-info/`, including `README`, `manifest.csv`, and the collected license/source materials.

## Next release

This checklist is specific to v0.2.0. Do not reuse its completed status for v0.3.0. Create a new release checklist and validate each new artifact and feature independently.
