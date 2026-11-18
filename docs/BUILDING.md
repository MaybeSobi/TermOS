# Building TermOS

**Current target:** Debian Stable, amd64, live-build.  
**Status:** Build configuration is being established for v0.3.0. This document is not evidence that an ISO has already been built or validated.

## Recommended host

Use a dedicated Debian Stable VM or development machine. Building live images requires root privileges and can create large temporary files. Do not run experimental installer code against disks containing important data.

## Dependencies

On a Debian Stable host:

~~~bash
sudo apt update
sudo apt install -y live-build debootstrap git make python3 python3-venv python3-pip qemu-system-x86 ovmf xorriso squashfs-tools file rsync
~~~

## Python development

~~~bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --editable .
termos --version
termos info
~~~

## Build the live ISO

From the repository root:

~~~bash
make build
~~~

The build script invokes lb config and lb build with root privileges. The expected output is live-image-amd64.hybrid.iso in the repository root.

## Verify and boot

~~~bash
make verify
make vm
~~~

The QEMU runner expects OVMF firmware at /usr/share/OVMF/OVMF_CODE_4M.fd and /usr/share/OVMF/OVMF_VARS_4M.fd. Override these with OVMF_CODE and OVMF_VARS_TEMPLATE if your host uses different paths.

## Clean generated state

~~~bash
make clean
~~~

lb clean --purge removes generated live-build state. Do not run it while a build is active.

## Reproducibility notes

The live-build configuration currently requests the moving Debian stable suite. A release record must capture the resolved codename, package versions, build date, and checksums. For stronger reproducibility, a later release pipeline should pin a Debian snapshot or another immutable package source after the project validates that workflow.

Do not claim reproducible builds until two independent builds from documented inputs have been compared.
