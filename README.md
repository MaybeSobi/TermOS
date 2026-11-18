# TermOS

<div align="center">

**A modular, CLI-first Linux system built on Debian.**

A system for people who want to understand, manage, and control their Linux environment.

[![Development](https://img.shields.io/badge/status-active%20development-blue)](https://github.com/MaybeSobi/TermOS)
[![Base](https://img.shields.io/badge/base-Debian%20Stable-A81D33)](https://www.debian.org/)

**Easy to Install. Powerful to Control. Modular by Design.**

</div>

> [!WARNING]
> The Debian-based v0.3.0 generation is under development. No v0.3.0 ISO or installer is currently released. Do not use this development branch as an installable operating system.

> [!NOTE]
> TermOS v0.2.0 is the last published Buildroot generation. Its source and release artifacts remain available in the v0.2.0 release. The Debian generation is a rebuild, not an in-place upgrade.

## Project direction

TermOS does not try to hide Linux. It aims to make Linux complexity accessible, manageable, and under the user's control.

- **CLI first, not CLI only:** the shell remains a first-class interface.
- **Transparent over magical:** explain system changes and show what a management action does.
- **One system, multiple interfaces:** CLI, TUI, installer, and future graphical tools share the same system interfaces.
- **Modular by design:** the base system does not force a desktop environment.
- **User control with understandable defaults:** guided workflows do not remove access to the underlying system.

## Architecture decisions

| Area | Direction |
| --- | --- |
| Base system | Debian Stable |
| ISO construction | Debian Live Build (live-build) |
| Default environment | Minimal CLI; no desktop by default |
| Optional desktop profiles | XFCE and KDE Plasma |
| Installer | Custom TermOS installer (planned) |
| First management interface | TUI Control Center |
| Core implementation | Python application layer + Rust system backend |
| System packages | APT / dpkg |
| TermOS Package Manager (TPM) | Retired from the Debian generation |

APT and dpkg remain the authoritative package-management system. TermOS will not introduce a competing package manager.

## Development status

The first Debian-generation milestone is **v0.3.0 — Debian Foundation**.

Its initial scope is deliberately small:
- A Debian Stable-based amd64 live ISO built with live-build.
- UEFI boot validation in QEMU.
- A minimal TermOS Python CLI with truthful system information.
- Build instructions, tests, and CI scaffolding.

The custom installer, full Control Center, Rust privileged backend, and optional desktop profiles are later milestones. Their presence in the architecture or repository does not mean they are implemented.

See [Architecture](docs/ARCHITECTURE.md), [Roadmap](docs/ROADMAP.md), [Building](docs/BUILDING.md), [Installation status](docs/INSTALLATION.md), [Migration policy](docs/MIGRATION_FROM_BUILDROOT.md), and [Release process](docs/RELEASE_PROCESS.md).

## Quick start for contributors

Use a Debian Stable development environment. See docs/BUILDING.md for dependencies and commands.

~~~bash
git clone https://github.com/MaybeSobi/TermOS.git
cd TermOS
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --editable .
termos --version
~~~

The ISO build requires root privileges because live-build creates a chroot and filesystem image:

~~~bash
make build
~~~

## Previous generation

- TermOS v0.2.0 — Buildroot experimental release
- TermOS v0.1.0 — experimental preview
- Archived v0.2.0 compliance and component records: docs/archive/v0.2.0/

## Contributing

Read CONTRIBUTING.md before opening a pull request. Feature proposals should include the user problem, intended behavior, testing plan, and any security or package-ownership implications.

TermOS is experimental software. Hardware compatibility, installation safety, and release readiness must be established through documented tests rather than assumptions.
