# Installation Status

**Current status:** No custom installer is implemented in v0.3.0 development scaffolding.

The first Debian-generation milestone targets a bootable live ISO. It does not yet install TermOS to a disk.

## Planned installer

The custom TermOS installer is a separate component from live-build. live-build constructs the live environment; it does not provide the final TermOS installation workflow.

The installer is planned to support hardware and firmware checks, language and keyboard selection, timezone, explicit disk and partition selection, clear display of destructive changes, a separate final confirmation, user creation, base-system installation, bootloader setup, logs, and actionable failure messages.

## Safety requirements

- Never format or repartition a disk by default.
- Display the exact target disk and planned changes.
- Require explicit final confirmation for destructive operations.
- Stop when disk identity or partition intent is ambiguous.
- Test against disposable virtual disks before physical hardware.
- Never claim that existing user data or partitions will be preserved unless that behavior has passed dedicated tests.

## Current development use

For v0.3.0, use the live ISO only in QEMU or another disposable virtual machine. There is no supported installation path yet.
