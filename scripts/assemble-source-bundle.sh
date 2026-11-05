#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "$0")/.." && pwd)"
ARTIFACT_DIR="\${1:?usage: assemble-source-bundle.sh <ci-artifact-dir> <output-dir>}"
OUTPUT_DIR="\${2:?usage: assemble-source-bundle.sh <ci-artifact-dir> <output-dir>}"

RELEASE_TAG="v0.2.0"
EXPECTED_COMMIT="14e0173e354a44b640723755b28180a1c819af05"
BUILDROOT_VERSION="2025.02.19"
BUILDROOT_BASE_URL="https://buildroot.org/downloads"
LEGAL_INFO_ARCHIVE="$ARTIFACT_DIR/TermOS-legal-info.tar.gz"
BUNDLE_NAME="TermOS-v0.2.0-corresponding-source"

if [[ -z "$ARTIFACT_DIR" || -z "$OUTPUT_DIR" ]]; then
    echo "ERROR: usage: assemble-source-bundle.sh <ci-artifact-dir> <output-dir>" >&2
    exit 2
fi

mkdir -p "$OUTPUT_DIR"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT
BUNDLE_DIR="$WORK_DIR/$BUNDLE_NAME"
mkdir -p "$BUNDLE_DIR/compliance-docs"

if [[ ! -s "$LEGAL_INFO_ARCHIVE" ]]; then
    echo "ERROR: missing CI legal-info archive: $LEGAL_INFO_ARCHIVE" >&2
    exit 1
fi

if ! git rev-parse --verify "$RELEASE_TAG^{commit}" >/dev/null 2>&1; then
    git fetch --force origin "refs/tags/$RELEASE_TAG:refs/tags/$RELEASE_TAG"
fi
ACTUAL_COMMIT="$(git rev-parse "$RELEASE_TAG^{commit}")"
if [[ "$ACTUAL_COMMIT" != "$EXPECTED_COMMIT" ]]; then
    echo "ERROR: $RELEASE_TAG resolves to $ACTUAL_COMMIT, expected $EXPECTED_COMMIT" >&2
    exit 1
fi

LEGAL_LIST="$WORK_DIR/legal-info-files.txt"
tar -tzf "$LEGAL_INFO_ARCHIVE" > "$LEGAL_LIST"
for required in \
    legal-info/README \
    legal-info/manifest.csv \
    legal-info/host-manifest.csv \
    legal-info/buildroot.config; do
    if ! grep -Fxq "$required" "$LEGAL_LIST"; then
        echo "ERROR: required legal-info entry missing: $required" >&2
        exit 1
    fi
done
for directory in legal-info/sources/ legal-info/host-sources/ legal-info/licenses/ legal-info/host-licenses/; do
    if ! grep -Fq "$directory" "$LEGAL_LIST"; then
        echo "ERROR: required legal-info directory missing: $directory" >&2
        exit 1
    fi
done

cp "$LEGAL_INFO_ARCHIVE" "$BUNDLE_DIR/TermOS-legal-info.tar.gz"

BUILDROOT_ARCHIVE="buildroot-$BUILDROOT_VERSION.tar.xz"
curl --fail --location --retry 3 --retry-delay 2 \
    "$BUILDROOT_BASE_URL/$BUILDROOT_ARCHIVE" \
    --output "$BUNDLE_DIR/$BUILDROOT_ARCHIVE"
curl --fail --location --retry 3 --retry-delay 2 \
    "$BUILDROOT_BASE_URL/$BUILDROOT_ARCHIVE.sign" \
    --output "$BUNDLE_DIR/$BUILDROOT_ARCHIVE.sign"
xz --test "$BUNDLE_DIR/$BUILDROOT_ARCHIVE"
tar -tJf "$BUNDLE_DIR/$BUILDROOT_ARCHIVE" > "$WORK_DIR/buildroot-files.txt"
grep -Fq "buildroot-$BUILDROOT_VERSION/support/libtool/" "$WORK_DIR/buildroot-files.txt"

git -C "$ROOT_DIR" archive --format=tar "$RELEASE_TAG" |
    gzip -n > "$BUNDLE_DIR/TermOS-source-$RELEASE_TAG.tar.gz"

for doc in \
    docs/THIRD_PARTY_NOTICES.md \
    docs/THIRD_PARTY_COMPONENTS_0.2.0.csv \
    docs/THIRD_PARTY_LICENSE_REVIEW_0.2.0.md \
    docs/COMPLIANCE_CHECKLIST_0.2.0.md; do
    if [[ -f "$ROOT_DIR/$doc" ]]; then
        cp "$ROOT_DIR/$doc" "$BUNDLE_DIR/compliance-docs/"
    fi
done

cat > "$BUNDLE_DIR/README.txt" <<EOF
TermOS 0.2.0 — corresponding-source and license-evidence bundle
================================================================

Release tag: $RELEASE_TAG
TermOS source commit: $EXPECTED_COMMIT
Buildroot: $BUILDROOT_VERSION
Linux kernel: 6.12.27
Architecture: x86_64

Contents
--------
1. TermOS-source-$RELEASE_TAG.tar.gz
   Exact source snapshot from the published TermOS v0.2.0 tag. It contains
   the defconfig, board files, local source, scripts, tests, and project
   documentation present in the release commit.

2. TermOS-legal-info.tar.gz
   Buildroot legal-info output from the successful v0.2.0 CI build. It
   contains target and host manifests, collected license texts, source
   archives, package patches and patch series as collected by Buildroot,
   the Buildroot configuration, and Buildroot's legal-info README.

3. $BUILDROOT_ARCHIVE and $BUILDROOT_ARCHIVE.sign
   The exact Buildroot source release used by TermOS. The separate Buildroot
   source is included because make legal-info reports that the Buildroot
   source code was not saved. This also includes Buildroot support/libtool
   material, which Buildroot documents as additional patches not copied into
   the per-package legal-info source directories.

4. compliance-docs/
   TermOS's component inventory, third-party notices index, technical review,
   and compliance checklist prepared after the v0.2.0 release.

Inventory facts from the v0.2.0 legal-info run
----------------------------------------------
- 10 target package entries.
- 38 host/build-tool package entries.
- 86 declared license-file entries collected.
- 0 blank/unknown declared license fields.
- 0 missing declared license-file fields.
- 1 source archive not saved by legal-info: Buildroot itself. Its exact
  upstream source archive and detached signature are supplied separately.

Verification
------------
The detached Buildroot signature is the original signature published by
Buildroot. Verify it with a trusted Buildroot release-signing public key:

  gpg --verify $BUILDROOT_ARCHIVE.sign $BUILDROOT_ARCHIVE

Verify the TermOS source snapshot and legal-info archive using SHA256SUMS:

  sha256sum --check SHA256SUMS

The checksum file covers the TermOS source snapshot, the legal-info archive,
the Buildroot source archive, and its detached signature. The outer release
asset has a separate .sha256 checksum beside it on the GitHub release page.

Scope and limitations
---------------------
Host packages are build-time tools and are not automatically part of the
installed target image. The manifests and license texts preserve Buildroot's
declarative package metadata; they are not a legal opinion. In particular,
license expressions such as "Python-2.0, others", custom license labels, and
multi-license packages require human interpretation. The bundle provides
corresponding source material and notices for review; it is not a legal
compliance certificate or an attorney's sign-off.
EOF

(
    cd "$BUNDLE_DIR"
    sha256sum \
        "TermOS-source-$RELEASE_TAG.tar.gz" \
        "TermOS-legal-info.tar.gz" \
        "$BUILDROOT_ARCHIVE" \
        "$BUILDROOT_ARCHIVE.sign" > SHA256SUMS
)

FINAL_ARCHIVE="$OUTPUT_DIR/TermOS-Corresponding-Source-$RELEASE_TAG.tar.gz"
tar -C "$WORK_DIR" -czf "$FINAL_ARCHIVE" "$BUNDLE_NAME"
(
    cd "$OUTPUT_DIR"
    sha256sum "$(basename "$FINAL_ARCHIVE")" > "$(basename "$FINAL_ARCHIVE").sha256"
)
echo "Created: $FINAL_ARCHIVE"
cat "$FINAL_ARCHIVE.sha256"
