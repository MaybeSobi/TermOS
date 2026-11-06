# TermOS Debian Migration Plan

> **Status:** Proposed architecture and release policy
>
> **Target generation:** TermOS v1.0.0
>
> **Migration model:** Fresh installation
>
> **Buildroot support boundary:** TermOS 0.x, through v0.9.x

This document defines how TermOS moves from its Buildroot-based experimental generation to the Debian-based v1.0 generation. It is a project architecture and release-policy document, not a claim that the migration has already been implemented.

## 1. Decision summary

TermOS v1.0.0 will be a **new Debian-based generation that requires a fresh installation**.

There will be no supported in-place conversion from an installed Buildroot-based TermOS system to Debian. The project will not promise that a v0.x installation can be upgraded directly to v1.0, nor that existing system packages, package-manager state, services, or configuration can be carried across automatically.

The two generations have distinct roles:

- **TermOS 0.x (Buildroot):** remains the development line through v0.9.x. It is where the project develops and validates its foundations.
- **TermOS 1.x (Debian):** begins a new system generation, with a Debian base and the long-term TermOS experience described in the roadmap.

A fresh installation does not mean that users must lose personal files. It means that the operating system itself is installed as a new system. Users are responsible for making and verifying backups before installation. Any future data-import utility will be a separate, explicitly scoped feature and will not be a prerequisite for installing v1.0.

## 2. Why this is a re-platforming, not an in-place upgrade

Buildroot and Debian have different system construction and package-management models.

The current Buildroot generation produces a purpose-built system image from a configured set of packages, filesystem overlays, scripts, and build outputs. The Debian generation will use Debian's package ecosystem and lifecycle. Their package databases, filesystem composition, service integration, and update mechanisms are not interchangeable.

Therefore, v1.0 will be built as a new Debian-based system rather than attempting to transform a running Buildroot root filesystem.

The migration is primarily a **development and architecture transition**:

1. Preserve the working product concepts and TermOS-authored components.
2. Separate reusable TermOS logic from Buildroot-specific integration.
3. construct and validate a Debian base independently.
4. Re-integrate TermOS services, TPM, profiles, installer, and Control Center through explicit interfaces.
5. Publish v1.0 as a fresh-install release.

The project must not describe this process as a seamless upgrade.

## 3. Release and compatibility policy

### 3.1 Buildroot line

- Buildroot remains the base for all planned 0.x releases, including v0.9.x.
- The 0.x line is not converted to Debian midway through its lifecycle.
- Existing 0.x releases remain identifiable by their own version numbers and release notes.
- The project will document the final 0.x release and its known limitations before the v1.0 transition.

The duration and scope of maintenance for the final Buildroot release must be stated in that release's notes. This document does not promise indefinite maintenance or security updates for the 0.x line.

### 3.2 Debian line

- TermOS v1.0.0 is Debian-based and distributed as a new installation image.
- The exact Debian Stable release will be selected during the v0.9 preparation phase, based on support lifecycle, hardware compatibility, package availability, and reproducible-build requirements.
- v1.0 installation must not depend on a previous TermOS installation.
- A user may install v1.0 on a machine that previously ran 0.x, but the installer treats the target installation as a new system.
- Version numbering and release notes must clearly identify the Debian generation.

### 3.3 Upgrade policy

The following are explicitly **not supported migration paths** for v1.0:

- In-place conversion of a Buildroot root filesystem into Debian.
- Reusing the Buildroot package database as Debian's dpkg database.
- Automatically translating installed TPM packages into Debian packages.
- Automatically carrying Buildroot service state or init configuration into Debian.
- Treating a raw copy of the old root filesystem as a valid Debian installation.

Future upgrades within the Debian-based TermOS generation (for example, v1.x to a later v1.y release) are a separate topic. They must follow Debian's supported upgrade practices plus TermOS-specific compatibility testing; this document does not define or guarantee them.

## 4. User data, backups, and configuration

A clean OS installation and preservation of personal data are separate concerns.

### Before installation

The installer and release documentation must clearly tell users to:

- Back up personal files to separate storage.
- Export or record application-specific data that is not stored in ordinary user directories.
- Save important SSH keys, credentials, browser profiles, project files, and other user-managed configuration securely.
- Record network, storage, and system settings they may need to recreate.
- Verify that backups can be read before changing disk partitions.

The installer must not imply that a backup exists or is valid.

### During installation

- The installer must clearly identify the selected target disk and partitions.
- Any operation that formats, deletes, or repartitions storage must show the exact target and consequences.
- Destructive operations require a separate, explicit final confirmation.
- The default path must not silently format disks.
- If the installer cannot determine whether an existing partition contains data the user wants to keep, it must stop and ask for an explicit choice rather than assume.

The precise partitioning modes and whether a separate data partition can be retained are implementation decisions that must be validated before v1.0. No preservation behavior should be advertised until tested.

### After installation

The initial v1.0 migration workflow is manual backup and restore. TermOS may later provide documented export/import tools for selected user data or settings, but such tools must:

- Be opt-in and inspectable.
- Show exactly what will be imported or overwritten.
- Validate input and handle malformed or incompatible data safely.
- Avoid importing privileged system files, package databases, service definitions, or arbitrary startup scripts by default.
- Support a dry-run or preview where practical.
- Never be required for a successful fresh installation.

## 5. Target v1.0 architecture

The Debian generation should separate the user experience from system operations and from the underlying distribution base.

```text
User
 |
 +-- Guided TUI Installer (live environment)
 |
 +-- CLI Login
      |
      +-- TermOS Control Center
      |     |
      |     +-- TermOS System API
      |            |
      |            +-- Debian services / systemd (candidate)
      |            +-- APT / dpkg
      |            +-- Network and storage tools
      |            +-- Hardware interfaces
      |
      +-- Normal Shell

TermOS Core
 +-- TPM (TermOS-specific package workflows)
 +-- Profile Manager
 +-- Configuration Manager
 +-- Logging / Diagnostics

Debian Base
 +-- Debian Stable (release selected during v0.9)
 +-- Linux kernel and firmware
 +-- Base libraries and utilities
 +-- Bootloader and init/service system
```

The diagram describes intended boundaries, not a finalized implementation. The init/service manager, privilege mechanism, filesystem layout, and exact system API must be decided and tested before they are treated as stable interfaces.

### Architectural requirements

- The Control Center is a presentation layer; it must not own privileged system logic.
- System operations should be exposed through documented, narrow interfaces.
- Privileged operations must validate inputs, enforce authorization, and log meaningful outcomes.
- TermOS components should avoid depending on UI-specific implementation details.
- Distribution-specific integration should be isolated behind adapters where practical.
- The system must remain usable through a normal shell if the Control Center fails.

## 6. Debian base construction

The current working direction is:

- Use **debootstrap or mmdebstrap** to create a minimal Debian root filesystem for development and integration testing.
- Use a chroot or equivalent isolated build environment to configure and test the root filesystem without modifying the host system.
- Investigate **live-build** for producing the bootable live ISO and its filesystem layout.
- Develop the guided TermOS installer as a distinct component. Do not assume that choosing live-build automatically provides the final TermOS installer UX.
- Select the Debian Stable release during v0.9 preparation rather than freezing a release years in advance.

These are proposed tools, not irrevocable dependencies. The project should compare their reproducibility, maintenance burden, boot support, and suitability before finalizing the build pipeline.

The v1.0 image must support the firmware modes and hardware scope explicitly listed in its release requirements. UEFI should be a required validation target; legacy BIOS support is a separate compatibility decision.

## 7. Package ownership: APT/dpkg and TPM

The Debian generation must have one authoritative owner for each installed file.

### Debian package ownership

APT/dpkg owns Debian packages and the files installed by those packages, including the Debian base system and packages installed from configured Debian-compatible repositories.

### TermOS package ownership

TPM (TermOS Package Manager) may manage TermOS-specific packages, metadata, and repositories only within a clearly defined ownership boundary. It must not overwrite or remove files owned by dpkg.

The exact TPM v1-on-Debian design remains open until a dedicated package architecture decision is reviewed. In particular, the project must specify:

- Package format and metadata.
- File ownership and conflict detection against dpkg.
- Dependency declarations and how Debian dependencies are represented.
- Install, upgrade, remove, and rollback transaction semantics.
- Repository signing, key trust, key rotation/revocation, and metadata freshness.
- Privilege boundaries and recovery behavior after interrupted operations.

The Control Center may present a unified package interface, but it must identify which backend performs each operation. A unified interface does not mean that TPM and APT share or overwrite package databases.

## 8. Reusing the Buildroot generation

The migration should preserve knowledge and reusable TermOS-authored work, not blindly copy the old root filesystem.

For each existing component, classify it as one of:

1. **Reusable logic:** distribution-independent code that can be carried forward with tests.
2. **Needs an adapter or port:** useful functionality coupled to Buildroot paths, BusyBox behavior, init scripts, or current filesystem assumptions.
3. **Buildroot-only integration:** defconfigs, overlays, image assembly, and scripts that remain with the 0.x line.
4. **Retire or redesign:** prototypes that do not meet the Debian generation's architecture or security requirements.

Likely candidates for review include:

- TPM core logic and its tests.
- Dashboard presentation and formatting helpers.
- Hardware information collection.
- Configuration and profile concepts.
- Documentation, test fixtures, and release engineering knowledge.

No component is automatically considered portable merely because it is written in Python or shell. Each port must be tested against the target Debian environment.

## 9. Migration work phases

The work is expected to proceed in phases. These are dependency stages, not calendar commitments.

### Phase A — Decouple TermOS from Buildroot

- Inventory TermOS-authored source code, overlays, scripts, services, and filesystem assumptions.
- Separate core logic from Buildroot-specific paths and boot integration.
- Define interfaces for configuration, logging, hardware discovery, and system operations.
- Add tests around reusable behavior before porting it.

**Exit condition:** reusable TermOS components can be tested independently of a Buildroot image.

### Phase B — Debian base prototype

- Select a candidate Debian Stable release for the prototype.
- Generate a minimal root filesystem using debootstrap or mmdebstrap.
- Boot it in a disposable VM.
- Validate bootloader, kernel, init/service manager, users, networking, storage, package operations, and logs.
- Record all deviations from the intended v1.0 architecture.

**Exit condition:** a reproducible minimal Debian-based TermOS development image boots and provides the required base services.

### Phase C — TermOS core port

- Port TPM according to the approved ownership model.
- Port the dashboard and connect it to the System API.
- Implement configuration and logging foundations.
- Establish service integration and privilege boundaries.
- Run unit, integration, and security tests.

**Exit condition:** core TermOS management functions work without relying on Buildroot-specific behavior.

### Phase D — Live image and installer

- Build a Debian-based live image.
- Implement and test the guided TUI installer independently from the live-image build mechanism.
- Validate disk discovery, partition selection, filesystem creation, bootloader installation, user creation, and failure handling.
- Test installation in disposable VMs before testing on physical hardware.
- Verify the installed system boots independently of the live environment.

**Exit condition:** a user can install the Debian-based TermOS generation from the live image using the documented supported installation paths.

### Phase E — Control Center and profiles

- Connect Control Center modules to real System API operations.
- Implement profile manifests and lifecycle rules.
- Validate the CLI base profile.
- Implement at least one optional desktop profile end to end before claiming desktop-profile support.
- Verify profile operations respect APT/dpkg and TPM ownership boundaries.

**Exit condition:** the default CLI-first experience and at least one supported optional profile work on a clean installation.

### Phase F — Release hardening

- Expand VM and physical hardware testing.
- Test installer safety, boot recovery, networking, storage, package operations, and system updates.
- Review security boundaries and third-party licensing obligations.
- Publish known limitations, checksums, source materials, and reproducible build instructions.
- Complete the v1.0 acceptance gate.

**Exit condition:** all mandatory v1.0 release criteria pass and the release documentation accurately describes tested hardware and limitations.

## 10. v1.0 acceptance gate

TermOS v1.0.0 must not be released until all mandatory items below are satisfied:

- [ ] The selected Debian Stable release and support policy are documented.
- [ ] The Debian base image can be built reproducibly from documented inputs.
- [ ] The live image boots in the required UEFI test environments.
- [ ] The guided installer completes a fresh installation in disposable VMs.
- [ ] Destructive disk operations require clear target display and explicit confirmation.
- [ ] The installed system boots without the live medium.
- [ ] User creation, login, networking, storage, and service management work.
- [ ] The System API has documented interfaces and authorization boundaries.
- [ ] The Control Center uses real system capabilities and has a normal-shell fallback.
- [ ] APT/dpkg and TPM have non-overlapping file ownership and tested conflict handling.
- [ ] TPM repository trust and package integrity behavior have passed security tests.
- [ ] The CLI base profile is validated; any advertised desktop profile has passed end-to-end tests.
- [ ] Backup and manual restore guidance is published.
- [ ] The release clearly states that v1.0 requires a fresh installation and does not support in-place Buildroot-to-Debian conversion.
- [ ] Automated tests, VM tests, and physical hardware tests are reported separately.
- [ ] Known limitations, recovery guidance, checksums, source availability, and third-party notices are published.

A failed mandatory item blocks the release. The project should delay v1.0 rather than silently downgrade the acceptance criteria.

## 11. Communication requirements

All v1.0 announcements, download pages, installer screens, and upgrade guidance must use consistent language:

> **TermOS v1.0 is a new Debian-based generation and requires a fresh installation. Direct in-place upgrades from Buildroot-based TermOS 0.x are not supported. Back up personal data to separate storage before installing.**

Do not use wording such as "upgrade from 0.x" unless referring only to moving to a new release by performing a fresh installation.

The 0.x and 1.x generations must not be confused in download labels, support statements, package instructions, or issue templates.

## 12. Open architecture decisions

The following decisions are intentionally deferred until prototypes and testing provide evidence:

- Exact Debian Stable release for v1.0.
- Final init/service manager choice (systemd is a candidate, not yet a frozen requirement).
- Final live-image build configuration and boot-mode support.
- Final installer implementation and supported partitioning modes.
- TPM package format and exact integration with Debian dependencies.
- Privilege/authorization mechanism for the System API.
- Official desktop profiles and their maintenance scope.
- Whether a future, separately scoped data export/import utility will be provided.

Each finalized decision should be recorded in a short Architecture Decision Record under `docs/decisions/`.

---

**Summary:** Buildroot remains the foundation of TermOS 0.x through v0.9.x. TermOS v1.0 begins a new Debian-based generation, delivered through a fresh installation. The project preserves reusable code and knowledge, but does not promise an in-place operating-system conversion or automatic migration of system state.
