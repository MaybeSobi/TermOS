# TermOS Roadmap

> **Project direction:** A modular, CLI-first Linux platform.
>
> **Guiding idea:** Easy to install. Powerful to control. Modular by design.

This document is the long-term development agreement for TermOS. It records the intended direction so that future implementation and release decisions remain consistent. The detailed Debian transition and release policy are defined in [Migration to Debian](MIGRATION_TO_DEBIAN.md).

The roadmap is intentionally capability-driven: version numbers describe milestones, not deadlines. A release must meet its acceptance criteria before it is considered complete.

## 1. Product vision

TermOS is intended for both newcomers and experienced Linux users.

Its identity remains **CLI-first, not CLI-only**:

- Installation should be guided by a polished, keyboard-friendly TUI rather than requiring users to work from an empty shell.
- After installation, the default experience should remain a CLI login followed by the TermOS Control Center.
- The Control Center should be the central entry point for system management while preserving access to a normal shell.
- Official graphical desktop environments should be optional profiles, not mandatory parts of the base installation.
- Community developers should eventually be able to publish compatible TermOS profiles through independent repositories.

The Control Center is an interface, not the owner of system logic. It should call well-defined system services/APIs and report their results rather than implementing privileged operations itself.

## 2. Audience and product principles

### 2.1 Intended audience

TermOS is not designed for an undefined audience of "everyone". Its intended users fall into four overlapping groups:

1. **Terminal Enthusiasts** — people for whom the terminal is a primary working environment. They value shell workflows, system administration through the CLI, resource and service visibility, fast access to tools, scripting, and composable workflows.
2. **Developers & Builders** — people who continually create and adapt their working environments. They value configurable development environments, profiles, package/tool management, and control over their workspace.
3. **Linux Power Users** — experienced users who want meaningful control over system behavior. They value modular architecture, choice of desktop environment, and direct management of networking, storage, services, and system configuration.
4. **Curious Linux Users** — people who want to understand and use Linux more deeply without having to assemble every part of a usable system from scratch. They benefit from a guided TUI installer, an understandable Control Center, a CLI-first experience, and access to a real shell.

These are overlapping personas on a spectrum, not four isolated markets or mutually exclusive user types. One person may fit several groups. Their needs can also conflict, so the project must be explicit about whose needs guide difficult prioritization decisions.

### 2.2 Primary user and prioritization

The primary design user is between the **Linux Power User** and the **Curious Linux User**: someone who wants to understand and control their Linux system, values the terminal, and appreciates a coherent starting point instead of having to assemble every component manually.

The other three audience groups remain important. Naming a primary user is a prioritization tool, not a decision to exclude anyone. When two design choices conflict, prefer the option that gives this primary user understandable, real system control while preserving direct CLI access and extensibility for experienced users.

Early 0.x releases may naturally appeal first to Terminal Enthusiasts and technically curious testers because the foundations arrive before the complete installer and Control Center experience. This is an intentional development sequence, not a change in the long-term audience.

### 2.3 User needs (working user stories)

Use these stories to evaluate whether planned capabilities solve real user needs. Refine them as implementation and testing reveal more detail.

- **Terminal Enthusiast:** "When I manage my system, I want to inspect and control its resources, services, and packages directly from the shell, so I can build fast, repeatable, scriptable workflows."
- **Developer & Builder:** "When I set up a project or change the kind of work I do, I want configurable tools and reusable profiles, so I can create a consistent environment without rebuilding it manually each time."
- **Linux Power User:** "When I need to change system behavior, I want clear access to the underlying configuration and service interfaces, so I can make informed decisions instead of being locked into hidden defaults."
- **Curious Linux User:** "When I install or configure TermOS, I want guided steps and a clear management interface that explains what is happening, so I can learn and use the system without first memorizing every command and configuration file."

### 2.4 Product and interaction principles

The following principles are design constraints for future features, not claims that every capability is already implemented.

1. **CLI First, Not CLI Only.** The shell is a first-class interface. Helpful TUI and optional graphical interfaces may make system capabilities easier to discover, but must not replace or obstruct the shell.
2. **Scriptable by Design.** System-management capabilities exposed through the Control Center should also be available through documented CLI commands or stable interfaces suitable for automation. Avoid UI-only functionality wherever practical.
3. **Transparent Over Magical.** Explain what an operation will change. Where practical, the Control Center should show the equivalent command or clearly identify the underlying operation before execution. Do not imply that displaying a command makes it safe; validation, authorization, and confirmation are still required.
4. **One System, Multiple Interfaces.** The CLI, Control Center, installer, and future interfaces should use shared system services/APIs rather than implementing separate versions of privileged logic. Equivalent actions should have consistent behavior and results.
5. **Modular by Design.** Keep optional components, profiles, and desktop environments separable. Users should be able to choose a suitable system composition without being forced into one desktop or workflow.
6. **User Control With Understandable Defaults.** Provide sensible defaults and guided workflows without hiding important decisions or removing the ability to inspect and override supported settings.
7. **Accessible Without Hiding Linux.** Help newer users discover and understand system capabilities; do not conceal the underlying Linux concepts or prevent advanced users from working directly with them.
8. **Honest About Capability.** Distinguish implemented, experimental, unavailable, and hardware-dependent functionality. Never display fabricated system data or imply an operation succeeded when it did not.

### 2.5 Control Center and CLI parity

The Control Center is a discoverable interface to TermOS capabilities, not a separate or exclusive way to administer the system.

For each supported management action:

- Provide a documented CLI equivalent or a documented stable system interface that can be used by scripts.
- Keep the underlying operation in a shared service/API layer; do not duplicate privileged business logic in UI code.
- Where practical, show the command or explain the exact operation the Control Center will request. If the operation cannot be represented safely as one command, explain the relevant service/API action instead of inventing a misleading command.
- Validate inputs and permissions consistently regardless of which interface initiates the action.
- Show meaningful success, failure, and diagnostic information. Do not report success until the backend confirms it.
- Preserve shell access and avoid requiring the Control Center for routine system use.

This principle lets a newer user learn through guided controls while allowing an experienced user to bypass the interface and automate the same capabilities.

### 2.6 Roadmap alignment with audience needs

The current milestone sequence introduces capabilities progressively:

| Milestone | Main audience emphasis | Why it matters |
| --- | --- | --- |
| v0.3.x | Terminal Enthusiasts and early Linux users | Reliable foundations, real system data, TPM, and persistence work |
| v0.4.x | Curious Linux Users | Guided installation begins to make setup understandable |
| v0.5.x | All audience groups | Control Center provides discoverable access to system capabilities while preserving CLI parity |
| v0.6.x | Developers & Builders and modular-system users | Profiles support repeatable, configurable environments |
| v0.7.x onward | Linux Power Users and all groups | Network, storage, services, settings, compatibility, and security deepen practical control |

This is an emphasis map, not an exclusion list or a promise that every feature will be complete for a persona at a particular milestone. Acceptance criteria and validation remain more important than the version label.

## 3. The 0.x / 1.0 agreement

### Through v0.9.x: Buildroot development and experimentation

TermOS will remain Buildroot-based through the entire 0.x series, including v0.9.x.

The purpose of this phase is to build, test, and understand the system's capabilities one by one. Buildroot is the development foundation for this phase; it is not a promise that Buildroot will remain the base forever.

During 0.x:

- Add capabilities incrementally and validate them in disposable virtual machines before relying on them.
- Keep the system small and understand the limits of the current base.
- Document architecture decisions, security boundaries, known limitations, and recovery procedures.
- Avoid presenting experimental functionality as production-ready.
- Do not begin the full Debian migration merely to accelerate a feature milestone.

### v1.0.0: Debian-based next generation

TermOS 1.0 is intended to be a major architectural transition to a Debian-based system.

The goal is not simply to replace Buildroot with Debian. The 1.0 release should deliver the product vision described in this roadmap:

- A guided, full-screen TUI installer.
- A CLI login and a polished TermOS Control Center as the default management experience.
- A modular system architecture with clear service/API boundaries.
- A package strategy that integrates Debian's package infrastructure without creating conflicting ownership of system files.
- Official, optional desktop profiles such as KDE Plasma and, subject to compatibility and maintenance capacity, GNOME, Hyprland, and XFCE.
- A documented profile format that can support community-maintained profiles.
- Hardware, installation, upgrade, security, and recovery validation appropriate for a public 1.0 release.

The exact Debian release, package versions, init/service choices, and migration mechanism must be selected and validated during the 0.9 preparation phase. They are not frozen by this roadmap.

## 4. Version milestones

The version-to-feature mapping below is a planning guide. Scope may move between releases when testing shows that a feature needs more work.

| Milestone | Main focus | Expected outcome |
| --- | --- | --- |
| v0.2.x | Experimental foundation | Build/CI, UEFI boot, dashboard, shell, and initial TPM integration documented |
| v0.3.0 | Balanced system foundations | TPM improvements, persistence investigation/implementation, dashboard integration, and hardware visibility |
| v0.4.x | Guided installation foundations | Installer UX and safe, testable installation workflow prototypes |
| v0.5.x | Control Center | Modular TUI dashboard connected to real system capabilities |
| v0.6.x | Profiles | Initial profile manifest/specification and profile lifecycle prototype |
| v0.7.x | System management | Network, services, storage, and settings integration |
| v0.8.x | Integration and compatibility | Broader VM and physical-hardware testing; security and recovery hardening |
| v0.9.x | Buildroot finalization and migration preparation | Stabilize the 0.x line, document limitations, define Debian target architecture, and prove migration-critical prototypes |
| **v1.0.0** | **Debian-based next generation** | **Deliver the modular, CLI-first TermOS platform with guided installation and official optional desktop profiles** |

## 5. v0.3.0 scope: balanced foundations

The first planned milestone under this agreement is v0.3.0. Its four focus areas are:

### 4.1 TPM — TermOS Package Manager

- Continue developing TPM as the TermOS-specific package and repository component.
- Review and consolidate duplicated TPM runtime sources so there is one maintainable source of truth.
- Improve package-format validation, repository verification, dependency handling, conflict detection, and transaction behavior.
- Evaluate secure repository transport and signed metadata as part of the repository workflow.
- Clearly document unsupported features and failure-recovery limits.
- Keep system-root operations guarded and test them only in disposable environments until their safety is demonstrated.

TPM must not be confused with the hardware Trusted Platform Module. In this project, TPM means **TermOS Package Manager**.

### 4.2 Persistence

- Inspect and document the current boot, root-filesystem, and mount architecture before choosing an implementation.
- Define what should persist, such as user data, TermOS configuration, and package state.
- Test persistence across reboots, missing or damaged persistence storage, and storage exhaustion.
- Avoid claiming that a live ISO or overlay-based setup has persistent behavior unless it has been demonstrated in repeatable tests.
- Defer a general-purpose disk installer and automatic partitioning unless separately scoped.

### 4.3 Dashboard / Control Center foundations

- Evolve the existing dashboard rather than rebuilding already-working information panels without reason.
- Integrate real system information, TPM status, storage/persistence state, and hardware data.
- Keep the interface usable on small terminal sizes and avoid unnecessary heavy dependencies.
- Preserve a clear path from the dashboard to a normal interactive shell.
- Keep privileged operations outside the presentation layer.

### 4.4 Hardware visibility and validation

- Improve detection/reporting of CPU, memory, storage, network interfaces, and available graphics devices.
- Treat sensor temperatures and GPU telemetry as hardware- and driver-dependent; show unavailable data honestly rather than inventing values.
- Record tested machine/VM configuration, firmware mode, devices, results, and known issues.
- Expand validation beyond a single virtual machine or physical computer where practical.

### v0.3.0 acceptance gate

Do not call v0.3.0 complete until:

- The four focus areas have documented implementation status and known limitations.
- Relevant unit and integration tests pass.
- TPM security and transaction tests cover the supported behavior.
- Persistence behavior is repeatable and its failure cases are documented.
- Dashboard values come from real system sources.
- Hardware detection handles unavailable devices gracefully.
- The ISO builds and passes the project's required boot tests.
- Release assets, checksums, corresponding source, and third-party license review are handled according to the release checklist.

## 6. Installer and first-boot experience

The intended TermOS installer is a guided TUI inspired by the usability of modern terminal installers.

It should provide clear steps for language/keyboard, storage selection and partitioning, timezone, user creation, initial profile, a final review, and installation progress.

Safety requirements:

- Destructive storage operations must show the target device and consequences and require explicit final confirmation.
- The installer must validate inputs and handle errors without silently continuing.
- Installation logs and failure information should be available for troubleshooting.
- The installer must not assume that every machine has identical firmware, storage, or network hardware.

After installation, the intended default flow is:

1. Boot the installed system.
2. Show a clear TermOS identity/boot experience.
3. Present a CLI login.
4. After successful login, launch the TermOS Control Center by default.
5. Allow the user to open or switch to a normal shell at any time.

A graphical desktop must not be forced on users who choose the CLI experience.

## 7. Control Center and system architecture

The long-term Control Center should provide modules for:

- Overview and system information
- Hardware and resource monitoring
- Package management
- Network configuration and status
- Storage and persistence
- Service management
- Profiles and optional desktop environments
- System settings and diagnostics

The Control Center should communicate with dedicated system components through documented interfaces. UI code should not become a collection of ad-hoc privileged shell commands.

Privileged actions must use narrow, auditable authorization boundaries, validate arguments, provide clear confirmation for destructive changes, and log meaningful outcomes.

## 8. Package-management boundaries for v1.0

If Debian is selected as the v1.0 base, the package architecture must avoid two independent package managers writing over the same files.

The working direction is:

- Debian's package infrastructure (APT/dpkg) owns and manages Debian base-system packages and their files.
- TPM manages TermOS-specific package metadata, repositories, profiles, and integration workflows within explicitly defined ownership boundaries.
- The Control Center may present a unified experience, but it must make clear which backend performs an operation.
- Profile manifests must declare dependencies and compatibility; they must not bypass package ownership or security checks.
- Any future decision to replace or deeply extend the base package manager requires a separate architecture review.

This boundary is a design requirement to validate, not a claim that the final implementation already exists.

## 9. Profiles and optional desktop environments

The long-term profile system should support official profiles and, eventually, community repositories.

Potential official profiles include:

- CLI base
- KDE Plasma
- GNOME
- Hyprland
- XFCE
- Developer environment

A profile specification should define at least:

- Unique profile ID and human-readable name
- Profile version and supported TermOS versions
- Architecture compatibility
- Package dependencies
- Required or enabled services
- Configuration payloads and their ownership
- Installation, update, and removal behavior
- Integrity/authenticity metadata and provenance

Profiles from GitHub or other remote sources must never be treated as trusted merely because they are hosted on a known platform. Validate metadata and package integrity, establish signing/trust rules, review privileged actions, and provide clear user consent. Avoid blindly piping remote scripts into a root shell.

Official profile support means the project commits to testing and maintaining the profile; it should not be used as a label for unverified community contributions.

## 10. Testing, security, and release discipline

Every feature should have acceptance criteria before implementation.

The project should maintain, as applicable:

- Unit tests for core logic.
- Integration tests for interactions between TPM, system services, persistence, and the dashboard.
- Build and ISO generation checks.
- UEFI boot tests in QEMU and supported VM platforms.
- Guest-level tests for installation and system operations.
- Persistence/reboot tests.
- Hardware test records that distinguish automated tests from manual smoke tests.
- Security tests for signatures, path validation, package integrity, permissions, and failure handling.
- Documentation for known limitations and recovery procedures.

A passing CI run is evidence for the tests it executes; it is not proof of broad hardware compatibility, power-loss safety, or production readiness.

Before public redistribution of each release, review applicable third-party licenses, notices, and corresponding-source obligations. Build metadata or a successful legal-info command is not itself legal approval.

## 11. v0.9 to v1.0 migration gate

The Debian transition must be treated as a separate generation of the project, not a routine base-image update. **TermOS v1.0.0 requires a fresh installation; in-place conversion from Buildroot-based 0.x installations is not supported.** See [Migration to Debian](MIGRATION_TO_DEBIAN.md) for the release policy, backup guidance, architecture, work phases, and acceptance gate.

Before starting the 1.0 release candidate, require:

- A documented Debian-based architecture and selected target release.
- A working minimal base-system prototype.
- Verified boot, networking, storage, user/login, and service management.
- A proven package ownership model for APT/dpkg and TPM.
- A working Control Center prototype against the new system interfaces.
- A profile prototype, including at least one optional desktop environment tested end to end.
- A guided installer prototype tested in disposable VMs.
- An upgrade/reinstall and user-data migration policy.
- Security review, automated tests, hardware compatibility notes, and complete release documentation.

If any critical requirement is not met, extend the 0.9 preparation period or delay 1.0. Do not ship 1.0 merely to meet a calendar target.

## 12. Out of scope unless separately approved

The following are not automatic commitments for the 0.x roadmap:

- A custom Linux kernel.
- A desktop environment enabled by default.
- A promise to support every GPU, laptop, or peripheral.
- Unreviewed arbitrary root scripts from remote repositories.
- A guarantee of recovery from every sudden power loss or hardware failure.
- Replacing APT/dpkg without a separate package architecture proposal.
- A full graphical settings application before the CLI Control Center is stable.

## 13. Project rules

1. **Buildroot through v0.9.x.** Do not migrate the 0.x development line to Debian.
2. **v1.0 is the Debian-based generation.** It must deliver a meaningful, tested architectural transition.
3. **Quality over release dates.** Milestones move when acceptance criteria are not met.
4. **No fake functionality.** UI elements must reflect working capabilities or be clearly marked experimental/unavailable.
5. **Security is part of the feature.** Privileged operations, packages, profiles, and updates need explicit trust boundaries.
6. **Document what is tested.** Separate automated results, manual tests, and assumptions.
7. **Preserve project knowledge.** Update this roadmap and relevant design documents when decisions materially change.

---

**Short version:** TermOS 0.x is where the project experiments and validates its foundations on Buildroot. TermOS 1.0 is the Debian-based, modular, CLI-first platform that turns those lessons into a coherent operating system.
