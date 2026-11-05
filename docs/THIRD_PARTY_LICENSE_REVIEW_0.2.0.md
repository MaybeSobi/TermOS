# TermOS 0.2.0 — Third-party license review

**Release:** v0.2.0  
**Release commit:** 14e0173e354a44b640723755b28180a1c819af05  
**Buildroot:** 2025.02.19  
**Linux:** 6.12.27  
**Architecture:** x86_64

## Review result

The exact target and host manifests from the successful v0.2.0 CI build were inspected. The recorded technical results are:

| Check | Result |
|---|---:|
| Target package entries | 10 |
| Host/build-tool package entries | 38 |
| Total manifest entries | 48 |
| Collected license-file entries | 86 |
| SHA-256 license-file checks reported successful by Buildroot | 86 |
| Blank/unknown declared license fields | 0 |
| Missing declared license-file fields | 0 |
| Source archive entries not found by the review generator | 1 |

The one source entry not saved by legal-info is Buildroot itself: the host manifest lists version -gf7b6724 with source archive and source site marked "not saved". All other 47 manifest entries have source archives located by filename in the legal-info source directories. The sole explicit warning in the release legal-info README is that Buildroot source was not saved.

The review generator reports human_review_required=true by design. A complete inventory is not the same as a legal opinion. Some declared license names are custom descriptions rather than SPDX identifiers, and some packages contain code under several different licenses.

The exact source inventory is preserved in [THIRD_PARTY_COMPONENTS_0.2.0.csv](THIRD_PARTY_COMPONENTS_0.2.0.csv). The original full manifests and all collected license texts are also preserved in the legal-info archive used by the source-bundle publisher.

## 1. Target image components

These are the ten entries in Buildroot's target manifest. Their license-file names and source archive names are in the CSV inventory.

| Package | Version | Buildroot-declared license |
|---|---|---|
| gcc-final | 13.4.0 | GPL-3.0-with-GCC-exception |
| glibc | 2.41-167-gf247c0a2fb5b3e48a771d2d23efc9a45c64e957d | GPL-2.0+ (programs), LGPL-2.1+, BSD-3-Clause, MIT (library) |
| linux-headers | 6.12.27 | GPL-2.0 |
| busybox | 1.37.0 | GPL-2.0, bzip2-1.0.6 |
| libffi | 3.4.6 | MIT |
| libopenssl | 3.5.9 | Apache-2.0 |
| libzlib | 1.3.2 | Zlib |
| python3 | 3.12.15 | Python-2.0, others |
| grub2 | 2.12 | GPL-3.0+ |
| linux | 6.12.27 | GPL-2.0 |

### Target-license observations

- **Linux and Linux headers:** Buildroot collects COPYING, the preferred GPL-2.0 text, and the Linux syscall exception. Preserve the exception text alongside the GPL text and the complete Linux source.
- **BusyBox:** the package is declared GPL-2.0 and additionally records the bzip2 1.0.6 license for bundled archive code. Both license files are collected; do not replace the latter with a generic GPL label.
- **glibc:** this is a multi-license package. The manifest identifies GPL for programs, LGPL for the library, and BSD/MIT portions. The source bundle must retain all glibc license files and any applicable notices.
- **GCC runtime:** the target gcc-final entry is declared GPL-3.0-with-GCC-exception and points to COPYING.RUNTIME. The exception must remain associated with the corresponding runtime components.
- **GRUB:** declared GPL-3.0+. Its COPYING text and exact source archive are part of the recorded legal-info material.
- **OpenSSL 3.5.9:** Buildroot declares Apache-2.0 and collects LICENSE.txt. Retain the license and any upstream NOTICE material that applies to this source release.
- **Python 3.12.15:** the package is declared "Python-2.0, others". The collected LICENSE identifies the Python Software Foundation License Version 2, the Zero-Clause BSD license for documentation examples, and states that some software incorporated into Python has different licenses. Therefore "others" must not be treated as a single license or silently dropped. The complete Python source archive and its upstream license file are included in the legal-info bundle; a final determination of every bundled module actually shipped in this image remains a human-review item.
- **libffi and zlib:** the manifest declares MIT and Zlib respectively; their upstream license files are collected.

## 2. Host/build-tool components

Host entries describe tools used to construct the image. They are not automatically software shipped in the target ISO, but they are included in the source/evidence package to support reproducibility and review of the build process.

| Package | Version | Buildroot-declared license |
|---|---|---|
| buildroot | -gf7b6724 | GPL-2.0+ |
| gcc-final | 13.4.0 | GPL-2.0, GPL-3.0, LGPL-2.1, LGPL-3.0 |
| bison | 3.8.2 | GPL-3.0+ |
| m4 | 1.4.21 | GPL-3.0+ |
| gawk | 5.3.1 | GPL-3.0+ |
| gcc-initial | 13.4.0 | GPL-2.0, GPL-3.0, LGPL-2.1, LGPL-3.0 |
| binutils | 2.43.1 | GPL-3.0+, GPL-2.0+, LGPL-2.1+ |
| gmp | 6.3.0 | LGPL-3.0+ or GPL-2.0+ |
| autoconf | 2.72 | GPL-3.0+ with exceptions |
| libtool | 2.4.6 | GPL-2.0+ (libtool), LGPL-2.1+ (libltdl) |
| automake | 1.16.5 | GPL-2.0+ |
| mpc | 1.3.1 | LGPL-3.0+ |
| mpfr | 4.1.1 | LGPL-3.0+ |
| e2fsprogs | 1.47.2 | GPL-2.0, MIT-like with advertising clause (libss and libet) |
| libarchive | 3.8.9 | BSD-2-Clause, BSD-3-Clause, CC0-1.0, OpenSSL, Apache-2.0 |
| libzlib | 1.3.2 | Zlib |
| pkgconf | 2.3.0 | pkgconf license |
| util-linux | 2.40.4 | GPL-2.0+, BSD-4-Clause, LGPL-2.1+ (libblkid, libfdisk, libmount), BSD-3-Clause (libuuid), BSD-2-Clause (xxhash), ISC (rfkill), MIT (hardlink, flock) |
| kmod | 33 | LGPL-2.1+ (library) |
| patchelf | 0.13 | GPL-3.0+ |
| python3 | 3.12.15 | Python-2.0, others |
| autoconf-archive | 2023.02.20 | GPL-3.0+ with exception |
| expat | 2.9.0 | MIT |
| libffi | 3.4.6 | MIT |
| flex | 2.6.4 | FLEX |
| gettext-tiny | 0.3.2 | MIT, GPL-3.0+ (extra gettext) |
| grub2 | 2.12 | GPL-3.0+ |
| elfutils | 0.193 | GPL-2.0+ or LGPL-3.0+ (library) |
| bzip2 | 1.0.8 | bzip2 license |
| xz | 5.6.4 | 0BSD, GPL-2.0+, GPL-3.0+, LGPL-2.1+, FSFUL, FSFULLR, Public Domain |
| zstd | 1.5.7 | BSD-3-Clause or GPL-2.0 |
| acl | 2.3.2 | GPL-2.0+ (programs), LGPL-2.1+ (libraries) |
| attr | 2.5.2 | GPL-2.0+ (programs), LGPL-2.1+ (libraries) |
| fakeroot | 1.36 | GPL-3.0+ |
| dosfstools | 4.2 | GPL-3.0+ |
| lzip | 1.25 | GPL-2.0+ |
| mtools | 4.0.48 | GPL-3.0+ |
| xorriso | 1.5.4.pl02 | GPL-3.0+ |

### Custom and multi-license host entries

The following entries deserve individual attention rather than being normalized to a convenient SPDX label:

- **flex 2.6.4:** Buildroot calls the license FLEX. The collected COPYING is a modified Berkeley/Flex BSD-style notice with retention conditions, a disclaimer, and a non-endorsement clause. Preserve the actual text.
- **pkgconf 2.3.0:** Buildroot calls this "pkgconf license". Its collected COPYING is a short permissive notice requiring preservation of copyright and permission text plus a warranty disclaimer. Retain the original text rather than inventing an SPDX identifier.
- **bzip2 1.0.8:** the package uses its own multi-condition bzip2 license, not a generic MIT/BSD label. Preserve its original LICENSE and conditions.
- **e2fsprogs 1.47.2:** its NOTICE distinguishes GPL-2.0 utilities, LGPL-covered libraries, a BSD-style UUID library, and MIT-style libet/libss code with an advertising clause. The collected NOTICE and the specified source/header license files must travel together.
- **libarchive 3.8.9:** multiple license families are declared. The complete source and COPYING file are included; preserve the individual notices present in the source distribution.
- **util-linux 2.40.4:** licensing differs by subcomponent (including GPL, BSD, LGPL, ISC, and MIT portions). Do not apply one license to the whole source tree.
- **xz 5.6.4:** the recipe records several possible license families, including 0BSD, GPL, LGPL, FSFUL/FSFULLR, and public-domain material. Preserve the source's separate license texts and patches.
- **GCC, GMP, MPC, MPFR, binutils, glibc, and Linux:** these are material to the internal Buildroot toolchain or target runtime. Their distinct source archives and license texts are included in the host/target legal-info trees; the GCC runtime exception and the glibc/Linux exceptions must not be omitted.

## 3. Corresponding-source and notice preparation

The release legal-info README contains one explicit warning: Buildroot source itself was not saved. It also explains two limitations of legal-info:

1. Toolchain source may need to be collected manually. In this build, the host manifest records source archives for the internal GCC toolchain components, including GCC initial/final, binutils, GMP, MPC, and MPFR. The source bundle includes the host-sources directory so those sources and their collected patches are available for inspection.
2. Buildroot applies additional patches to Libtool scripts under support/libtool; these are not copied into each package's legal-info source tree. The exact Buildroot 2025.02.19 source archive is therefore included separately in the source bundle, along with its original detached signature.

The automated corresponding-source publisher is configured to take the legal-info archive from the successful release-build run, add the exact TermOS v0.2.0 tag source snapshot, add the official Buildroot 2025.02.19 source archive and signature, include the CycloneDX SBOM and compliance documents, generate SHA-256 sums, and attach the resulting source archive and checksum to the existing v0.2.0 GitHub release. Publication is only complete after that workflow succeeds and the two assets are visible on the release page.

## 4. Buildroot inventory limitations

Buildroot documents that legal-info is based on declarative package recipe metadata. It collects more material than every license strictly requires, and its metadata may be inaccurate or incomplete. It is therefore not a substitute for checking the actual package version and source. Buildroot also says it does not normally collect its own source, and its legal-info output omits the additional support/libtool patch material described above.

TermOS also generates a CycloneDX SBOM using Buildroot's show-info and generate-cyclonedx tools. The SBOM is useful for machine-readable inventory, but it also relies on Buildroot package metadata and does not independently prove legal compliance.

## 5. Remaining human decisions

The technical evidence and reproducible source bundle are being prepared in the repository. The following decisions cannot be honestly marked as completed solely from CI:

- Confirm that all TermOS-authored files are covered by the repository MIT license and that every contributor had the right to contribute under that license.
- Resolve the detailed scope of "others" in Python's package license and every relevant subcomponent license for the exact binary.
- Have a qualified legal reviewer assess any remaining interpretation of GPL/LGPL, Apache-2.0, multi-license packages, and whether the publication method satisfies the applicable obligations for this specific distribution.
- Confirm the corresponding-source archive has been attached successfully to the public v0.2.0 release and can be downloaded and verified by a third party.

This document is a technical review record, not a legal opinion, legal audit opinion, or certificate. No legal certification is claimed.

## References

- [Buildroot manual — legal notice and licensing](https://buildroot.org/downloads/manual/manual.html#legal-notice-and-licensing)
- [Official Buildroot 2025.02.19 source archive and PGP signature](https://buildroot.org/downloads/buildroot-2025.02.19.tar.xz)
- [Buildroot download page](https://buildroot.org/download.html)
- [TermOS v0.2.0 release](https://github.com/MaybeSobi/TermOS/releases/tag/v0.2.0)
- [TermOS v0.2.0 CI workflow run #22](https://github.com/MaybeSobi/TermOS/actions/runs/42106722558)
