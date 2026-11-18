# TermOS Architecture

**Status:** Accepted direction for the Debian generation; implementation is incremental.  
**Baseline:** v0.3.0 development line.

## Product boundary

TermOS is a Debian-based system integration and user-experience project. Debian supplies the operating-system base, kernel, package database, and standard services. TermOS supplies a coherent CLI-first experience, configuration conventions, profiles, installer, and management interfaces.

## Accepted platform decisions

| Area | Decision |
| --- | --- |
| Distribution base | Debian Stable |
| ISO construction | Debian Live Build (live-build) |
| Initial architecture | amd64 |
| Default session | Minimal CLI; no desktop environment |
| Optional desktop profiles | XFCE and KDE Plasma |
| Installer | Custom TermOS installer, planned |
| First management interface | TUI Control Center |
| Application layer | Python |
| System backend | Rust, introduced when privileged operations are implemented |
| Package ownership | APT / dpkg |
| TPM | Retired; no TPM code in the Debian generation |

The configured stable suite tracks Debian Stable. Release engineering must record the resolved Debian codename and package snapshot used for every published ISO.

## Logical layers

1. **Interface layer:** CLI, TUI Control Center, custom installer, and optional desktop integrations.
2. **Application layer:** Python commands, presentation, profile definitions, and non-privileged orchestration.
3. **System backend:** Rust service for narrowly scoped privileged operations. This is a future component, not required for the first v0.3 ISO.
4. **Debian services:** systemd, D-Bus, Polkit, NetworkManager, APT/dpkg, and standard Linux interfaces.
5. **Hardware:** CPU, memory, storage, network, graphics, and peripherals.

Interfaces must call shared application/system APIs. Do not duplicate privileged business logic in the TUI, CLI, or installer.

## Python and Rust responsibilities

Python owns user-facing orchestration and presentation: CLI, TUI, profile parsing, configuration workflows, and non-privileged system inspection.

Rust is reserved for the system backend where a long-running service, strict input validation, and narrow privileged operations justify it. Do not add Rust merely to duplicate an existing Debian tool.

The backend should expose a documented local interface, with D-Bus as the preferred integration mechanism when it fits the operation. Authorization should use system policy (for example, Polkit) rather than a permanently privileged UI process.

## Package ownership

- APT/dpkg exclusively own Debian packages and the files installed by them.
- TermOS profiles may declare Debian package dependencies and TermOS-owned configuration.
- TermOS must not install a second package database or overwrite dpkg-owned paths.
- The Control Center may provide a unified presentation, but it must disclose that APT/dpkg perform package operations.
- No TPM or replacement package manager is part of this generation.

## Profiles

Profiles are declarative descriptions of supported system compositions. They may reference Debian package names, optional services, and TermOS-owned configuration. Profile application must be idempotent, inspectable, and reversible where practical.

Initial concepts: minimal (base CLI), developer (tools layered on another profile), xfce, and kde. The v0.3 milestone only establishes the base image and profile format. It does not claim that profile switching or desktop installation is implemented.

## Security boundaries

- Never run arbitrary profile-provided shell scripts as root.
- Validate all inputs at the backend boundary.
- Keep privileged operations narrow and auditable.
- Require explicit confirmation for destructive storage operations.
- Do not expose a general-purpose root command execution API to the UI.
- Report success only after the underlying operation confirms success.
- Log meaningful operation outcomes without recording secrets.

## Build and image lifecycle

live-build creates the live ISO. It is not the installer. The custom installer will be a separate program executed from the live environment and will install a Debian-based system to a target disk in a later milestone.

The v0.3 base image has no default desktop. XFCE and KDE are future optional profiles and are not included in the initial minimal ISO.

## Architecture evolution

Implementation status is tracked in ROADMAP.md. Significant changes to accepted boundaries require a new Architecture Decision Record under docs/decisions/.
