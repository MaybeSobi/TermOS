# TermOS 0.2.0 — Third-party license review

**Review scope:** the published v0.2.0 x86_64 ISO, built from commit `14e0173e354a44b640723755b28180a1c819af05` using Buildroot 2025.02.19 and Linux 6.12.27.

**Review status:** evidence collection is automated; package-by-package legal review remains open until the exact release manifests, license texts, and source archives have been inspected and reconciled.

## 1. What the project currently establishes

The TermOS workflow ran Buildroot's `make legal-info` successfully for the release commit (workflow run #22). The workflow artifact contains the generated legal-info material. The build pipeline also confirms that the ISO was built and reached the init process in QEMU with UEFI firmware.

The repository contains a top-level MIT `LICENSE`. That license covers TermOS-authored project files only to the extent those files are owned or properly licensed by the relevant contributors. It does not replace or override licenses of third-party components in the image.

The current public v0.2.0 release contains the ISO and its checksum file. It does not itself contain a durable, reviewed source-and-notices package.

## 2. How to interpret the Buildroot inventory

Buildroot produces separate target and host manifests:

- `manifest.csv` describes packages selected for the target image.
- `host-manifest.csv` describes host-side build tools. A host-only tool is not automatically shipped in the target ISO, but its role must be kept distinct when reviewing distribution of build tooling or source bundles.
- `licenses/` and `host-licenses/` contain license files collected from package recipes.
- `sources/` and `host-sources/` contain source archives Buildroot was able to collect.
- `README` records warnings and material that Buildroot could not collect.
- `buildroot.config` records the configuration used for the build.

The compact evidence generator in `scripts/generate-legal-review.py` preserves those manifests and license-text directories, creates a component table, and indexes source archives. Its source-name match is only an availability hint; it does not prove that the archive is complete, corresponds to the exact binary, contains all applied patches, or satisfies a license obligation.

## 3. Known gaps that require explicit treatment

### Buildroot source

Buildroot's own documentation says that its source code is not normally collected by `make legal-info`. The Buildroot manual also explains that Buildroot is usually a build-time tool rather than part of the device image, but records the Buildroot developers' view that Buildroot source should be released with source for GPL-licensed software in the product because the build system forms part of the scripts used to control compilation and installation. The manual advises seeking legal advice if uncertain.

TermOS builds with Buildroot 2025.02.19. The source archive is available upstream at:

- https://buildroot.org/downloads/buildroot-2025.02.19.tar.xz

A reproducible source package should preserve that exact Buildroot version together with the TermOS defconfig, board configuration, local patches, and the scripts needed to reproduce the build. The upstream download link alone is not yet proof that a versioned corresponding-source package has been published and tested.

### Toolchain and host components

The exact release manifest and legal-info README must be checked for toolchain/compiler/runtime gaps and host packages. Do not infer source availability or license status from the fact that the ISO built successfully.

### Target component obligations

Each target component must be reviewed against its exact package version and actual upstream license text. For each component, identify whether the license requires retention of notices, delivery of license text, publication or offer of source, relinking materials, installation information, or other conditions. The answer depends on the exact license and how the component is used and distributed; a generic list of license families is not a substitute for this check.

## 4. Required review procedure

1. Inspect the exact v0.2.0 target and host manifests and every warning in the legal-info README.
2. Compare each declared license and license-file entry with the corresponding package source and upstream license text.
3. For each source-required component, match the source archive to the exact version and verify all applicable patches and configuration.
4. Review the Linux kernel configuration and enabled modules, GRUB, BusyBox, OpenSSL, Python, and all transitive packages listed in the target manifest.
5. Identify any additional notices or source obligations created by package patches, bundled firmware, generated binaries, or TermOS-authored integration code.
6. Package the required source materials and notices for the exact release, publish them at a stable location, and verify that a third party can download and inspect them.
7. Record the result and unresolved items in the compliance checklist.

## 5. What this review does not claim

This document is a technical compliance work record, not a legal opinion, audit opinion, or certificate. Buildroot itself warns that its package metadata is declarative and may not be accurate or exhaustive. Final legal interpretation, including whether a given distribution method meets every applicable obligation, must be confirmed by a qualified legal reviewer.

## References

- [Buildroot manual — complying with open-source licenses](https://buildroot.org/downloads/manual/manual.html#legal-notice-and-licensing)
- [Buildroot 2025.02.19 source archive](https://buildroot.org/downloads/buildroot-2025.02.19.tar.xz)
- [TermOS v0.2.0 release](https://github.com/MaybeSobi/TermOS/releases/tag/v0.2.0)
- [TermOS v0.2.0 CI workflow run #22](https://github.com/MaybeSobi/TermOS/actions/runs/42106722558)
