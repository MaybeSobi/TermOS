# TermOS 0.2.0 — Third-party license review record

**Review status:** Preliminary inventory review; not a legal opinion or certification  
**Release tag:** `v0.2.0`  
**Tagged commit:** `14e0173e354a44b640723755b28180a1c819af05`  
**Build system:** Buildroot 2025.02.19  
**Evidence:** [Main-branch CI run #22](https://github.com/MaybeSobi/TermOS/actions/runs/42106722558)

## 1. Scope

This record covers the x86_64 ISO produced by the TermOS v0.2.0 tagged commit. It separates software included in the target image from host-only tools used to build the image. Host tools are tracked as part of the build record, but their presence in Buildroot's host manifest does not by itself mean they are shipped in the ISO.

TermOS's repository-level MIT license applies only to TermOS-authored project files. It does not replace or override the licenses of the Linux kernel, BusyBox, glibc, GRUB, OpenSSL, Python, Buildroot, or other third-party components.

## 2. CI evidence collected

The successful run #22 built the tagged commit and completed the following steps:

- Buildroot `legal-info` generation.
- Validation that `build/legal-info/README` and `build/legal-info/manifest.csv` exist and are non-empty.
- ISO format and SHA-256 checks.
- QEMU UEFI boot validation until the init process was reached.

The legal-info section of the job log contains 61 package collection entries and 86 successful SHA-256 checks for collected license/notice files. These counts describe the log output; they are not a count of distinct target packages or a legal conclusion.

The warning printed by Buildroot during collection is:

```
WARNING: the Buildroot source code has not been saved
```

This warning must be considered alongside the actual README and manifests. Buildroot is the build system; it is not automatically a package shipped in the target ISO. The exact build sources, patches, configuration, and scripts needed to satisfy source obligations for distributed copyleft components still require individual verification.


## 3A. Selected upstream Buildroot recipe declarations

The following are declarations in the Buildroot 2025.02.19 package recipes for components identified in the v0.2.0 legal-info collection log. They are a useful cross-check, not a substitute for the exact target manifest or inspection of each source tree.

| Component | Version in CI log | Buildroot recipe license declaration | Review note |
|---|---:|---|---|
| Linux kernel | 6.12.27 | GPL-2.0 | Verify the exact kernel source, applied patches, configuration, and any relevant exceptions. |
| GRUB 2 | 2.12 | GPL-3.0+ | Copyleft source and notices must be included or clearly made available. |
| BusyBox | 1.37.0 | GPL-2.0; bzip2-1.0.6 | Check BusyBox configuration and source; include the separately declared bzip2 license text. |
| glibc | 2.41 snapshot | GPL-2.0+ (programs), LGPL-2.1+, BSD-3-Clause, MIT (library) | Multi-license component; do not represent the whole package with one SPDX label. |
| OpenSSL library | 3.5.9 | Apache-2.0 | Preserve its license and required notices. |
| Python | 3.12.15 | Python-2.0, others | The "others" declaration requires investigation of bundled components and associated license terms. |
| zlib | 1.3.2 | Zlib | Preserve the license notice and confirm the source version. |
| libffi | 3.4.6 | MIT | Preserve the license notice. |

The CI collection log also lists `host-kmod 33`; its Buildroot recipe declares LGPL-2.1+ for the library and GPL-2.0+ for the tools. This is a host-side build dependency in the observed collection log, not evidence that kmod is included in the target ISO. The host manifest must be used to confirm the build-only classification.

**Key unresolved point:** The exact `manifest.csv` and `host-manifest.csv` from the tagged build remain to be inspected. Recipe declarations can differ from the actual package contents, and package sources may contain additional separately licensed files or exceptions.

## 3. What is not yet verified

The actual `manifest.csv`, `host-manifest.csv`, and complete `legal-info/README` contents have not yet been manually inspected in this review session. Therefore, this record does **not** assert that:

- every package has a known and correct license declaration;
- every license text and exception has been matched to the correct component;
- all copyleft source and build/install-script obligations are satisfied;
- all required copyright and third-party notices are present in the published release;
- the MIT declaration covers every contribution with valid authorship/permission evidence.

A new CI artifact named `TermOS-Legal-Review-Metadata` is being added to expose the small reviewable subset (README, target and host manifests, Buildroot configuration, and collected license texts) separately from the large source archive. The exact data from that artifact must be reviewed before closing the relevant checklist items.

## 4. Review workflow

For the compact artifact:

1. Read `README` and record every warning.
2. Review `manifest.csv` for target packages and `host-manifest.csv` separately for host tools.
3. Flag missing or `unknown` license/version fields.
4. Compare recipe-declared license expressions against the actual collected license texts and any package-specific exceptions or embedded notices.
5. For each component in the target image, determine whether it is distributed in binary form and identify its exact corresponding source, patches, and applicable build/install scripts.
6. Publish a durable compliance bundle and clear source-access information with the release, once the required materials have been verified.
7. Retain the exact source/configuration snapshot associated with the ISO.

## 5. Legal references

- [Buildroot user manual — legal information](https://buildroot.org/downloads/manual/manual.html): describes the contents and limitations of `legal-info`, including that its data comes from package recipe declarations and must be checked before compliance use.
- [GNU GPL FAQ](https://www.gnu.org/licenses/gpl-faq.en.html): explains source distribution, corresponding-source and written-offer questions.
- [GNU GPL v2 text](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html): states the applicable source-provision choices for covered object-code distribution under GPLv2.

This document is an engineering review record. It is not legal advice, a formal legal opinion, or a compliance certificate.
