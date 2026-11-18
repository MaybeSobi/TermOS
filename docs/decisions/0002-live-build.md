# ADR 0002: Use Debian Live Build for ISO Construction

- **Status:** Accepted
- **Date:** 2026-11-18

## Context

TermOS needs a repeatable way to assemble a Debian-based live ISO while keeping package selection and filesystem customization declarative.

## Decision

Use Debian Live Build (live-build) for the v0.3.0 image pipeline. Keep configuration under auto/ and config/. The custom TermOS disk installer remains a separate future component.

## Consequences

- live-build owns live-image assembly and bootable ISO generation.
- TermOS scripts wrap build, clean, verification, and VM launch tasks.
- The installer must not be conflated with the live-image builder.
- The exact live-build version and resolved Debian package set must be recorded for releases.
