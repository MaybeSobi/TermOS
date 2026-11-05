# TermOS 0.2.0 — Compliance and release checklist

**Release:** v0.2.0  
**Release commit:** 14e0173e354a44b640723755b28180a1c819af05  
**Buildroot:** 2025.02.19  
**Kernel:** Linux 6.12.27  
**Architecture:** x86_64

This checklist separates evidence-backed engineering work from decisions that require rights-holder confirmation or qualified legal review.

## Confirmed release and build evidence

- [x] Public GitHub release v0.2.0 exists and is neither a draft nor a prerelease.
- [x] Release includes TermOS-CI-x86_64.iso and SHA256SUMS.
- [x] Published ISO SHA-256 matches the digest reported by GitHub: 4b09ad178f3eaf202ab4e26a1c6b60c83eb4d869074de4352e1be92ba56da565.
- [x] CI built the ISO and reached init in QEMU with UEFI firmware and VirtIO networking.
- [x] Buildroot make legal-info completed for the exact release commit in workflow run #22.
- [x] The legal-info README, target manifest, and host manifest were inspected from the v0.2.0 release build.
- [x] All 48 manifest entries were inventoried: 10 target packages and 38 host/build-tool packages.
- [x] All 86 declared license-file entries were collected and all 86 Buildroot license-file SHA-256 checks passed.
- [x] No manifest entry has a blank/unknown declared license field.
- [x] No manifest entry has a missing declared license-file field.
- [x] The one source archive not saved by legal-info was identified as Buildroot itself.
- [x] Special/custom and multi-license declarations (Python, flex, pkgconf, bzip2, e2fsprogs, libarchive, util-linux, xz, glibc, GCC, and Linux exceptions) were flagged in the technical review.
- [x] Exact package inventory CSV was committed at docs/THIRD_PARTY_COMPONENTS_0.2.0.csv.
- [x] Technical review and third-party notices index were updated.
- [x] CycloneDX SBOM generation was added to the release CI using Buildroot show-info and generate-cyclonedx.
- [x] A corresponding-source bundle assembler and automated release-publishing workflow were added.

## Corresponding source and notices

- [x] Source archive names and license-file metadata are recorded for all target and host manifest entries.
- [x] Internal toolchain source entries (GCC initial/final, binutils, GMP, MPC, MPFR, and related host sources) are recorded in host-manifest.csv.
- [x] Buildroot 2025.02.19 is identified as the one source archive not collected by legal-info.
- [x] Source-bundle tooling includes the exact TermOS v0.2.0 source snapshot, the legal-info archive, the official Buildroot source archive and detached signature, the CycloneDX SBOM, compliance documents, and SHA-256 sums.
- [ ] Verify the automated source publisher succeeds after the documentation PR is merged and that both corresponding-source assets appear on the public v0.2.0 release page.
- [ ] Independently download the published corresponding-source archive and verify its SHA-256 and internal SHA256SUMS.
- [ ] Have a qualified legal reviewer assess the final source/notice package and unresolved license interpretations before claiming formal legal clearance.

## Ownership and contributor scope

- [ ] Confirm contributor rights and MIT coverage for all TermOS-authored files. The repository license text alone does not prove every contributor granted the necessary rights.
- [ ] Resolve the exact shipped scope of Python's "others" license declaration and any additional bundled-module notices.
- [ ] Confirm any package-specific requirements that depend on how the ISO is distributed and whether the GPLv3 User Product installation-information provisions apply.

## Hardware validation — separate from licensing

- [ ] Boot the exact published v0.2.0 ISO from USB on physical x86_64 hardware.
- [ ] Record the machine model, firmware mode, date, display, keyboard, storage, and network results.
- [ ] Test at least one physical network adapter and record the driver/device identity.
- [ ] Record failures and limitations; do not generalize from one machine to all hardware.

## Release decision

**Current status:** TermOS 0.2.0 remains an experimental preview. The technical inventory, notice documentation, SBOM generation, and source-bundle automation are prepared. Formal legal sign-off, contributor-rights confirmation, successful publication/verification of the corresponding-source assets, and physical-hardware testing remain separate gates.

The published ISO is not represented as legally certified or production-ready.

## Reproduction

From the TermOS project root, run:

    ./scripts/build.sh
    make -C src/buildroot-2025.02.19 O="$PWD/build" legal-info
    python3 scripts/generate-legal-review.py --legal-info build/legal-info --output build/legal-review
    make -C src/buildroot-2025.02.19 O="$PWD/build" show-info | python3 src/buildroot-2025.02.19/utils/generate-cyclonedx > build/TermOS-v0.2.0.cdx.json

See [Third-party license review](THIRD_PARTY_LICENSE_REVIEW_0.2.0.md), [Third-party notices](THIRD_PARTY_NOTICES.md), and the [component inventory CSV](THIRD_PARTY_COMPONENTS_0.2.0.csv).

## References

- [Buildroot manual — legal notice and licensing](https://buildroot.org/downloads/manual/manual.html#legal-notice-and-licensing)
- [Buildroot download page](https://buildroot.org/download.html)
