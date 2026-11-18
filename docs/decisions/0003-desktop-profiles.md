# ADR 0003: No Default Desktop; XFCE and KDE as Optional Profiles

- **Status:** Accepted
- **Date:** 2026-11-18

## Context

TermOS is CLI-first and should not impose a graphical desktop on every user. Optional desktop environments are part of the intended modular experience.

## Decision

The base installation has no default desktop environment. XFCE and KDE Plasma are the initial planned official desktop profiles. They are not included in the v0.3.0 minimal image and are not considered supported until end-to-end profile tests exist.

## Consequences

- The base ISO remains a minimal CLI environment.
- Desktop packages are installed only through an explicitly selected profile.
- Profile definitions must use APT/dpkg and must not create a second package database.
