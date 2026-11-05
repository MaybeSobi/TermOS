import hashlib
import io
import json
import os
import stat
import tarfile

from pathlib import Path, PurePosixPath

from .dependencies import DependencyError, validate_dependencies
from .security import (
    PackageSecurityError,
    normalize_package_path,
)

FORMAT_VERSION = 1
MAX_MANIFEST_SIZE = 4 * 1024 * 1024
MAX_FILES = 100_000


class PackageError(Exception):
    pass


def build_package(source, output, name, version, architecture, description="", depends=None):
    source = Path(source).resolve()
    output = Path(output).resolve()

    if not source.is_dir():
        raise PackageError("Source directory does not exist")

    if not all(isinstance(v, str) and v.strip() for v in (name, version, architecture)):
        raise PackageError("Name, version and architecture are required")

    try:
        dependency_specs = validate_dependencies(depends or [], package_name=name)
    except DependencyError as exc:
        raise PackageError(f"Invalid dependencies: {exc}") from exc

    files = []

    for current, directories, filenames in os.walk(source, followlinks=False):
        current_path = Path(current)

        for directory in directories:
            if (current_path / directory).is_symlink():
                raise PackageError("Symlink directories are forbidden")

        for filename in filenames:
            file_path = current_path / filename

            if file_path.is_symlink() or not stat.S_ISREG(file_path.lstat().st_mode):
                raise PackageError(f"Unsupported file: {file_path}")

            relative = file_path.relative_to(source).as_posix()
            relative = normalize_package_path(relative)

            digest = hashlib.sha256(file_path.read_bytes()).hexdigest()

            files.append({
                "path": relative,
                "sha256": digest,
                "mode": stat.S_IMODE(file_path.stat().st_mode) & 0o777,
                "size": file_path.stat().st_size,
            })

    if not files or len(files) > MAX_FILES:
        raise PackageError("Invalid package file count")

    files.sort(key=lambda item: item["path"])

    manifest = {
        "format": "TPK",
        "format_version": FORMAT_VERSION,
        "name": name,
        "version": version,
        "architecture": architecture,
        "description": description,
        "depends": dependency_specs,
        "files": files,
    }

    manifest_data = json.dumps(
        manifest, ensure_ascii=False, indent=2, sort_keys=True
    ).encode("utf-8")

    output.parent.mkdir(parents=True, exist_ok=True)

    with tarfile.open(output, "w", format=tarfile.PAX_FORMAT) as archive:
        info = tarfile.TarInfo("manifest.json")
        info.size = len(manifest_data)
        info.mode = 0o644
        info.mtime = 0
        archive.addfile(info, io.BytesIO(manifest_data))

        for entry in files:
            path = source.joinpath(*PurePosixPath(entry["path"]).parts)
            info = tarfile.TarInfo("payload/" + entry["path"])
            info.size = entry["size"]
            info.mode = entry["mode"]
            info.mtime = 0

            with path.open("rb") as file:
                archive.addfile(info, file)

    return manifest


def validate_package(package_path):
    try:
        with tarfile.open(package_path, "r:") as archive:
            members = archive.getmembers()

            if len(members) > MAX_FILES + 1:
                raise PackageError("Too many archive entries")

            names = set()

            for member in members:
                if member.name in names:
                    raise PackageError("Duplicate archive entry")
                names.add(member.name)

                if not member.isfile():
                    raise PackageError("Only regular files are supported")

                if member.name != "manifest.json":
                    if not member.name.startswith("payload/"):
                        raise PackageError("Unexpected archive entry")
                    normalize_package_path(member.name[len("payload/"):])

            if "manifest.json" not in names:
                raise PackageError("Manifest missing")

            manifest_member = archive.getmember("manifest.json")

            if manifest_member.size > MAX_MANIFEST_SIZE:
                raise PackageError("Manifest too large")

            stream = archive.extractfile(manifest_member)
            if stream is None:
                raise PackageError("Cannot read manifest")

            manifest = json.loads(stream.read())
            if not isinstance(manifest, dict):
                raise PackageError("Manifest must be a JSON object")
            try:
                manifest["depends"] = validate_dependencies(
                    manifest.get("depends", []), package_name=manifest.get("name")
                )
            except DependencyError as exc:
                raise PackageError(f"Invalid dependency metadata: {exc}") from exc

            if manifest.get("format") != "TPK":
                raise PackageError("Invalid package format")

            if manifest.get("format_version") != FORMAT_VERSION:
                raise PackageError("Unsupported format version")

            entries = manifest.get("files")

            if not isinstance(entries, list) or not entries or len(entries) > MAX_FILES:
                raise PackageError("Invalid manifest file list")

            expected = set()

            for entry in entries:
                path = normalize_package_path(entry["path"])

                if path in expected:
                    raise PackageError("Duplicate manifest path")
                expected.add(path)

                digest = entry["sha256"]
                size = entry["size"]
                mode = entry["mode"]

                if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
                    raise PackageError("Invalid SHA-256")

                if type(size) is not int or size < 0:
                    raise PackageError("Invalid file size")

                if type(mode) is not int or mode < 0 or mode > 0o777:
                    raise PackageError("Invalid file mode")

                member_name = "payload/" + path

                if member_name not in names:
                    raise PackageError("Missing payload: " + path)

                member = archive.getmember(member_name)

                if member.size != size:
                    raise PackageError("Size mismatch: " + path)

                stream = archive.extractfile(member)
                if stream is None:
                    raise PackageError("Cannot read payload: " + path)

                actual = hashlib.sha256(stream.read()).hexdigest()

                if actual != digest:
                    raise PackageError("Checksum mismatch: " + path)

            actual = {n[8:] for n in names if n.startswith("payload/")}

            if actual != expected:
                raise PackageError("Unexpected payload entries")

            return manifest

    except PackageError:
        raise
    except PackageSecurityError as exc:
        raise PackageError(
            f"Package security validation failed: {exc}"
        ) from exc
    except (tarfile.TarError, json.JSONDecodeError, KeyError, TypeError, OSError, UnicodeError) as exc:
        raise PackageError(f"Invalid package: {exc}") from exc


def package_info(package_path):
    return validate_package(package_path)
