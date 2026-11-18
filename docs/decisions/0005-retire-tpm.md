# ADR 0005: Retire TPM from the Debian Generation

- **Status:** Accepted
- **Date:** 2026-11-18

## Context

The Debian generation already has a mature package-management system. A second package manager would introduce overlapping package databases, file ownership, dependency resolution, and update behavior.

## Decision

Retire TPM (TermOS Package Manager) from the Debian generation. APT and dpkg are the sole system package-management authorities. TPM source, tests, package format, and signing key are not part of the active Debian architecture.

The historical TPM implementation remains available in the Buildroot release tags and Git history.

## Consequences

- No .tpk package installation in the Debian generation.
- Profiles declare Debian package dependencies and TermOS-owned configuration only.
- The Control Center must disclose that APT/dpkg perform package operations.
