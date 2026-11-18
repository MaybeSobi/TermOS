# Rebuild Boundary: Buildroot Generation to Debian Generation

**Status:** Accepted project policy  
**Previous generation:** Buildroot-based TermOS v0.1.0 and v0.2.0  
**New development generation:** Debian-based TermOS v0.3.0 onward

## Decision

TermOS is rebuilding its development line on Debian Stable beginning with v0.3.0. The Buildroot-based v0.1.0 and v0.2.0 releases remain historical releases. There is no supported in-place conversion from an installed Buildroot system to the Debian generation.

This is a development and architecture reset, not an operating-system upgrade.

## What is preserved

- Published release tags and release assets.
- Historical Buildroot configuration, source, and release evidence through their Git history and tags.
- Product principles and useful lessons from the first generation.
- Individual TermOS-authored ideas or code only when reviewed and deliberately reimplemented or ported.

## What is not carried forward as active Debian architecture

- Buildroot defconfigs, kernel fragments, root filesystem overlays, and image-generation scripts.
- BusyBox-specific assumptions and Buildroot boot integration.
- TPM (TermOS Package Manager), its .tpk format, repository database, and package ownership model.
- The old TPM repository signing key and package tests.
- Any claim that the old dashboard or scripts are already compatible with Debian.

TPM is retired from the Debian generation. APT/dpkg are the authoritative package-management tools.

## User data and installation

No automatic migration of system files, package state, services, or configuration is promised. A future Debian installer must clearly identify target disks and require explicit confirmation before destructive operations.

Users should back up personal data to separate storage before installing any future TermOS image. Do not assume that an installer preserves existing partitions until that exact behavior is implemented and tested.

## Versioning

- v0.1.0 and v0.2.0 remain Buildroot historical releases.
- v0.3.0 begins the Debian-based development line.
- v0.x milestones are capability-driven development releases.
- v1.0.0 is the intended first stable release, not the point at which Debian is introduced.

## Repository policy

The active development branch should contain only the current Debian-generation build and application architecture. Historical release documentation is retained under docs/archive/; old implementation code remains recoverable from the original release tags and Git history.

No history rewrite or deletion of published tags is part of this rebuild.
