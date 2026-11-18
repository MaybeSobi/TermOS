# TermOS 0.2.0 — Third-party license review record

**Review status:** Preliminary inventory review; not a legal opinion or certification  
**Release tag:** v0.2.0  
**Tagged commit:** 14e0173e354a44b640723755b28180a1c819af05  
**Build system:** Buildroot 2025.02.19  
**Evidence:** Main-branch CI run #22

## 1. Scope

This record covers the x86_64 ISO produced by the TermOS v0.2.0 tagged commit. It separates software included in the target image from host-only tools used to build the image. Host tools are part of the build record, but their presence in Buildroot's host manifest does not mean they are shipped in the ISO.

TermOS's repository MIT license applies only to TermOS-authored project files. It does not replace the licenses of the Linux kernel, BusyBox, glibc, GRUB, OpenSSL, Python, Buildroot, or other third-party components.

## 2. CI evidence collected

The successful run #22 built the tagged commit and completed Buildroot legal-info generation, ISO format and SHA-256 checks, and QEMU UEFI boot validation until init was reached.

The legal-info section of the job log contains 61 package collection entries and 86 successful SHA-256 checks for collected license/notice files. These counts describe log output; they are not a count of distinct target packages or a legal conclusion.

Buildroot reported: "WARNING: the Buildroot source code has not been saved". This warning must be considered alongside the actual README and manifests. Buildroot is the build system; it is not automatically a package shipped in the target ISO. Exact build sources, patches, configuration, and scripts needed for distributed copyleft components still require individual verification.

## 3. Selected upstream recipe declarations

The following are declarations in Buildroot 2025.02.19 recipes for components identified in the v0.2.0 legal-info collection log. They are a cross-check, not a substitute for the exact target manifest or source inspection.

| Component | Version in CI log | Recipe license declaration | Review note |
| --- | --- | --- | --- |
| Linux kernel | 6.12.27 | GPL-2.0 | Verify exact source, patches, configuration, and exceptions. |
| GRUB 2 | 2.12 | GPL-3.0+ | Copyleft source and notices must be included or made available. |
| BusyBox | 1.37.0 | GPL-2.0; bzip2-1.0.6 | Check configuration and source; include the bzip2 license text. |
| glibc | 2.41 snapshot | GPL-2.0+ (programs), LGPL-2.1+, BSD-3-Clause, MIT (library) | Multi-license component; do not reduce to one SPDX label. |
| OpenSSL library | 3.5.9 | Apache-2.0 | Preserve license and required notices. |
| Python | 3.12.15 | Python-2.0, others | The "others" declaration requires investigation of bundled components. |
| zlib | 1.3.2 | Zlib | Preserve notice and confirm source version. |
| libffi | 3.4.6 | MIT | Preserve license notice. |

The CI collection log also lists host-kmod 33; its recipe declares LGPL-2.1+ for the library and GPL-2.0+ for tools. This is a host-side build dependency in the observed log, not evidence that kmod is in the target ISO.

The exact manifest.csv and host-manifest.csv from the tagged build still require manual inspection. Recipe declarations can differ from actual package contents, and sources may contain additional separately licensed files or exceptions.

## 4. What is not verified

The actual target manifest, host manifest, and complete legal-info README were not manually inspected in the preliminary review. This record does not assert that every package has a known and correct license, every license text has been matched, all source obligations are satisfied, all notices are present, or the MIT declaration covers every contribution with valid authorship evidence.

## 5. Review workflow

1. Read README and record every warning.
2. Review target manifest and host manifest separately.
3. Flag missing or unknown license/version fields.
4. Compare recipe declarations with collected texts and package-specific exceptions.
5. Identify exact corresponding source, patches, and applicable build/install scripts for every copyleft component in the target image.
6. Publish durable notices and source-access information once verified.
7. Retain the exact source/configuration snapshot associated with the ISO.

## 6. References

- Buildroot manual — legal information: https://buildroot.org/downloads/manual/manual.html
- GNU GPL FAQ: https://www.gnu.org/licenses/gpl-faq.en.html
- GNU GPL v2: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html

This document is an engineering review record, not legal advice, a formal legal opinion, or a compliance certificate.
