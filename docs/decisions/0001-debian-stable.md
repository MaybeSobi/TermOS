# ADR 0001: Debian Stable as the Base System

- **Status:** Accepted
- **Date:** 2026-11-18

## Context

The project is rebuilding the TermOS development line to provide a maintainable Linux base rather than continuing to grow a custom Buildroot system.

## Decision

Use Debian Stable as the base distribution for the Debian generation, beginning with v0.3.0. The live-build configuration uses the stable suite. Every release must record the resolved Debian codename and package state.

## Consequences

- APT/dpkg are the authoritative package-management system.
- Debian service and filesystem conventions are preferred.
- The project inherits Debian's package lifecycle and security-update model.
- The moving stable alias is convenient for development but is not, by itself, a reproducible release input.
