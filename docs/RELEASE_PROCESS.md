# Release Process

This document defines release discipline for the Debian generation. It does not certify that any current development build is ready for publication.

## Before a release

- Confirm the milestone acceptance criteria in ROADMAP.md.
- Build from a clean checkout using the documented environment.
- Record the Debian suite and resolved codename, package versions, build host, and build date.
- Run unit tests, shell syntax checks, and integration tests.
- Boot the ISO in UEFI QEMU; record the command and result.
- Perform manual VM and physical-hardware tests only when available, clearly separating them from automated tests.
- Generate SHA-256 checksums.
- Review third-party packages, licenses, notices, and corresponding-source obligations for the exact image.
- Publish known limitations and recovery guidance.
- Verify release assets after upload.

## Release artifacts

A public ISO release should include, as applicable: ISO image, SHA256SUMS, release notes, known limitations, exact source revision and build instructions, third-party notices and corresponding-source materials, test evidence, and supported hardware scope.

## Version policy

- Development package version: 0.3.0.devN until a release is approved.
- Milestone release tags use v0.3.0, v0.4.0, and so on.
- Do not retarget an already published tag.
- Buildroot v0.1.0 and v0.2.0 tags remain unchanged.

## Publication rule

Do not publish a generated ISO as a supported release merely because CI built it. Release readiness requires passing the milestone gate and a human review of the exact artifacts and their notices.
