"""Initial TermOS command-line entry point."""

from __future__ import annotations

import argparse
import platform
from pathlib import Path

from . import __version__


def _read_os_release() -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
            if "=" not in line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            values[key] = value.strip().strip('"')
    except OSError:
        pass
    return values


def system_info() -> dict[str, str]:
    release = _read_os_release()
    return {
        "distribution": release.get("PRETTY_NAME", "Unknown distribution"),
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "python": platform.python_version(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="termos", description="TermOS command-line interface")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("info", help="show basic host system information")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "info":
        for key, value in system_info().items():
            print(f"{key:14} {value}")
        return 0
    parser.print_help()
    return 0
