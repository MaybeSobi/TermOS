# ADR 0004: Python Application Layer and Rust System Backend

- **Status:** Accepted direction; implementation staged
- **Date:** 2026-11-18

## Context

TermOS needs a maintainable user-facing application layer and a clear boundary for privileged system operations.

## Decision

Use Python for the CLI, TUI, profile/configuration workflows, and non-privileged orchestration. Introduce Rust for a narrowly scoped system backend when privileged operations and stable interfaces are implemented.

Do not create a Rust daemon in v0.3.0 solely to satisfy the language choice. The first milestone can ship without a privileged backend.

## Consequences

- UI layers must not run as root by default.
- Privileged operations require narrow APIs, input validation, and system authorization.
- D-Bus and Polkit are candidates for integration; their final use must be validated.
- Python and Rust must not independently implement the same privileged operation.
