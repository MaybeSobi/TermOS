# ADR 0006: Package the TermOS CLI as a Debian Package

- **Status:** Accepted for v0.3.0
- **Date:** 2026-11-18

## Context

The live ISO needs to include the TermOS CLI without using pip to modify the system Python environment or creating a parallel package manager.

## Decision

Build a small architecture-independent .deb package from the TermOS Python source using dpkg-deb. live-build installs this local package from config/packages.chroot. The package owns only the TermOS module under /usr/lib/python3/dist-packages and the termos entry point under /usr/bin.

## Consequences

- dpkg owns and tracks the installed TermOS CLI files.
- APT/dpkg remain the only package-management authority.
- The local .deb is generated during the build and is not committed as a binary artifact.
- The package build script must be tested and the generated package inspected before release.
