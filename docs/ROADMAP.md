# TermOS Roadmap

> **Direction:** A modular, CLI-first Linux system built on Debian.  
> **Guiding idea:** Easy to Install. Powerful to Control. Modular by Design.

This roadmap describes intended milestones, not deadlines. A version is complete only when its acceptance criteria are met and implementation status is honestly documented.

## Product principles

1. **CLI First, Not CLI Only:** the shell is always a first-class interface.
2. **Scriptable by Design:** management actions have documented CLI equivalents or stable APIs.
3. **Transparent Over Magical:** explain operations and their effects before changes.
4. **One System, Multiple Interfaces:** CLI, TUI, installer, and future GUI share system logic.
5. **Modular by Design:** no mandatory desktop; profiles are composable.
6. **User Control With Understandable Defaults:** guided flows preserve meaningful choices.
7. **Accessible Without Hiding Linux:** help users learn without locking them away from the system.
8. **Honest About Capability:** implemented, planned, experimental, and unavailable features are clearly distinguished.

## Platform baseline

| Area | Decision |
| --- | --- |
| Base | Debian Stable |
| ISO builder | live-build |
| Architecture | amd64 initially |
| Default environment | Minimal CLI |
| Optional desktops | XFCE and KDE Plasma |
| Installer | Custom TermOS installer |
| First Control Center | TUI |
| Core languages | Python + Rust |
| Package management | APT / dpkg |
| TPM | Retired |

## Milestones

| Version | Focus | Exit criteria |
| --- | --- | --- |
| **v0.3.0** | Debian Foundation | Minimal amd64 live ISO, UEFI/QEMU boot validation, initial Python CLI, tests and build documentation. |
| **v0.4.0** | TermOS Core | Shared configuration model, profile manifest schema, system-information interfaces, initial TUI Control Center, and Rust backend prototype only where required. |
| **v0.5.0** | Custom Installer | Guided installer prototype with safe disk discovery, explicit target selection, final destructive-action confirmation, logs, and VM installation tests. |
| **v0.6.0** | Profiles | Declarative profile manager, Minimal and Developer profiles, and profile validation. |
| **v0.7.0** | Desktop Integration | Optional XFCE and KDE Plasma profiles, desktop session integration, and documented package ownership through APT/dpkg. |
| **v0.8.0** | Reliability | Upgrade/recovery design, broader VM and hardware testing, security review, diagnostics, and failure handling. |
| **v0.9.0** | Release Candidate | Feature freeze, reproducible build review, installation hardening, documentation completion, and RC validation. |
| **v1.0.0** | First Stable Release | Stable Debian-based TermOS with tested installer, CLI/TUI management, supported profiles, release documentation, and published limitations. |

## v0.3.0 — Debian Foundation

### In scope
- Debian Stable live image built with live-build.
- amd64 architecture.
- Minimal CLI environment; no desktop packages in the base image.
- UEFI boot validation in QEMU.
- Python package and termos command.
- Basic truthful system information command.
- Build, clean, verify, and QEMU helper scripts.
- GitHub Actions validation and manually triggered ISO build workflow.
- Architecture, build, migration, and installation-status documentation.

### Explicitly out of scope
- Custom disk installer.
- Full TUI Control Center.
- Rust privileged system service.
- XFCE or KDE packages in the default ISO.
- Profile installation/switching.
- TPM or any parallel package manager.
- Claims of physical hardware compatibility before testing.

### Acceptance criteria
- lb config and lb build complete in the documented Debian Stable environment.
- ISO artifact exists and has a recorded SHA-256.
- UEFI boot reaches the live environment in QEMU.
- termos --version and termos info work.
- Unit tests and shell syntax checks pass.
- Documentation accurately states that installer and desktop profiles are not yet implemented.

## Release policy

- Buildroot v0.1.0 and v0.2.0 remain historical releases and are not rewritten.
- v0.3.0 starts the Debian development generation.
- Buildroot-to-Debian is a rebuild boundary; no in-place conversion is supported.
- Milestones move when quality gates are not met.
- Experimental releases must not be described as production-ready.
