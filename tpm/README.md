# TermOS Package Manager (TPM)

TPM is the terminal package manager developed for TermOS. It builds and
validates `.tpk` archives, installs/removes/upgrades packages in a marked root,
resolves local repository dependencies, and verifies signed repository indexes.

## Requirements

- Python 3.12 or newer.
- OpenSSL command-line utility with Ed25519 support for repository signing and
  verification.
- A repository public key obtained through a trusted channel for signed-repo
  operations.

## Source-tree usage

From the TermOS repository root:

```sh
python3 -m tpm.tpm --help
./test_tpm.sh
./test_tpm_security.py
./test_tpm_install.sh
./test_tpm_remove.sh
./test_tpm_rollback.sh
./test_tpm_upgrade.sh
./test_tpm_dependencies.sh
./test_tpm_repository.sh
```

## TermOS image usage

The integration image installs the runtime under `/opt/termos/python/tpm`, the
launcher at `/usr/bin/tpm`, and the trusted public key at
`/etc/termos/repository-ed25519.pub`.

Sandbox operations continue to require an explicit `--root DIR`. The separate
`--system` mode is available only on a root-owned TermOS system identified by
`/etc/termos-release`. Mutating system operations require a typed confirmation
and a package present in a signature-verified repository. Example:

```sh
tpm install packages/example-1.0.0-x86_64.tpk \
  --system --repo /var/lib/termos/repository
```

The trusted key defaults to `/etc/termos/repository-ed25519.pub`; an explicit
`--repo-key FILE` can override it. System-root operations require UID 0.

**Live/ISO persistence warning:** a successful system-root operation modifies
the currently mounted `/` filesystem. Whether it survives reboot depends on the
boot/storage layout. The current TermOS preview is not a disk installer and
must not be assumed to provide persistent package storage in every live-ISO
boot mode. Test first in disposable QEMU/VMware virtual machines.

## Security model and limitations

- `.tpk` payload files are checked against manifest sizes and SHA-256 values.
- Repository index signatures are checked with Ed25519 and a provisioned public
  key; the private key is never copied into the image.
- Sandbox root initialization and live system-root authorization are separate.
- Live system-root access is gated by root privileges, `/etc/termos-release`,
  and explicit confirmation for install/remove/upgrade.
- TPM version 1 does not execute package maintainer scripts and does not support
  symlink payloads. It is not a general-purpose replacement for mature package
  managers and remains experimental.
- Current transaction tests inject software failures. They do not prove
  recovery after power loss, kernel panic, or sudden hardware failure.
- Repository sync over HTTPS, key rotation, revocation, and repository freshness
  policy are not provided by this integration step.

See [`../docs/TPK_FORMAT.md`](../docs/TPK_FORMAT.md) for the archive specification.
