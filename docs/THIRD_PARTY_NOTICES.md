# TermOS 0.2.0 — Third-party notices and source availability

This is the stable index for third-party software and licensing evidence associated with the TermOS v0.2.0 image.

## Package inventory

The exact Buildroot v0.2.0 target and host package records are in [THIRD_PARTY_COMPONENTS_0.2.0.csv](THIRD_PARTY_COMPONENTS_0.2.0.csv):

- 10 target package entries;
- 38 host/build-tool package entries;
- 86 collected license-file entries;
- no blank/unknown license fields and no missing license-file fields in the manifests.

The original Buildroot manifests and all collected license texts are retained in the full legal-info archive included in the corresponding-source bundle. Do not treat host/build-tool packages as automatically present in the installed target image.

## License texts

Buildroot's legal-info output collects license files listed by package recipes in:

- licenses/ — target components;
- host-licenses/ — host/build tools.

The v0.2.0 CI log reports 86 successful SHA-256 checks for collected license files. The original texts are preserved verbatim in the legal-info archive. Multi-license packages and custom labels are described in [the technical license review](THIRD_PARTY_LICENSE_REVIEW_0.2.0.md); do not replace them with a single generic SPDX label.

## Corresponding source

The corresponding-source package is designed to include:

- the exact TermOS v0.2.0 Git tag source snapshot;
- the original Buildroot legal-info archive, including sources, host-sources, patches/series, manifests, collected license texts, configuration, and README;
- the official Buildroot 2025.02.19 source archive and detached signature, covering the source omitted by legal-info and Buildroot's support/libtool patch material;
- the generated CycloneDX SBOM;
- the compliance documents and SHA-256 checksums.

The release workflow publishes the source archive and its checksum to the [TermOS v0.2.0 release page](https://github.com/MaybeSobi/TermOS/releases/tag/v0.2.0) after the compliance documentation is merged and the successful main-branch build completes. Verify that the assets are present before treating publication as complete.

## Reproduce the inventory

From the TermOS project root:

    make -C src/buildroot-2025.02.19 O="$PWD/build" legal-info
    python3 scripts/generate-legal-review.py --legal-info build/legal-info --output build/legal-review
    make -C src/buildroot-2025.02.19 O="$PWD/build" show-info | python3 src/buildroot-2025.02.19/utils/generate-cyclonedx > build/TermOS-v0.2.0.cdx.json

## Important limitation

This index and its generated inventory are technical evidence, not a legal opinion, legal audit opinion, or compliance certificate. Buildroot itself warns that recipe metadata can be incomplete or inaccurate. Contributor ownership and package-specific legal interpretation must be confirmed separately.
