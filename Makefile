.PHONY: help test build clean verify vm

help:
	@printf '%s\n' 'TermOS development targets:' \
	  '  make test    Run Python unit tests' \
	  '  make build   Build the live ISO (requires root/sudo)' \
	  '  make clean   Clean live-build generated state' \
	  '  make verify  Inspect and checksum the generated ISO' \
	  '  make vm      Boot the ISO in QEMU with UEFI'

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

build:
	./scripts/build-iso.sh

clean:
	./scripts/clean-build.sh

verify:
	./scripts/verify-iso.sh

vm:
	./scripts/run-qemu.sh
