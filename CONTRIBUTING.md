# Contributing to TermOS

Thanks for your interest in TermOS.

## Before opening an issue

Search existing issues and describe the problem, expected behavior, actual behavior, and environment. For system bugs, include the TermOS version or commit, Debian suite, architecture, VM or physical-hardware context, and relevant logs. Remove secrets and personal data from logs.

## Pull requests

- Keep changes focused and explain the user-facing or architectural reason.
- Update documentation when behavior or accepted architecture changes.
- Add tests for new logic.
- Do not add unreviewed privileged shell execution.
- Do not add a second package manager or write into dpkg-owned paths.
- Keep the CLI usable without the TUI.
- Mark planned, experimental, and implemented functionality accurately.

## Development checks

~~~bash
make test
sh -n auto/config
bash -n scripts/*.sh
python3 -m compileall -q src tests
~~~

For ISO work, follow docs/BUILDING.md. Installer changes must be tested with disposable virtual disks.

Use concise commit prefixes where practical: docs:, feat:, fix:, test:, and ci:.
