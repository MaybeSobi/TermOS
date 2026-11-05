import hashlib
import os
import platform
import re
import stat
import tarfile
from pathlib import Path

from .dependencies import DependencyError, check_installed_dependencies
from .database import (
    DatabaseError,
    load_database,
    save_database,
    validate_root,
)
from .package import PackageError, validate_package
from .security import normalize_package_path


class InstallError(Exception):
    pass


def _check_existing_parent(root, parts):
    current = root
    for part in parts:
        candidate = current / part
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            return
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise InstallError(f"Unsafe destination directory: {candidate}")
        current = candidate


def _create_parent(root, parts, created_directories):
    current = root
    for part in parts:
        candidate = current / part
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            try:
                candidate.mkdir(mode=0o755)
                created_directories.append(candidate)
            except FileExistsError:
                pass
            try:
                info = candidate.lstat()
            except FileNotFoundError as exc:
                raise InstallError(f"Directory disappeared: {candidate}") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise InstallError(f"Unsafe destination directory: {candidate}")
        current = candidate
    return current


def _validate_manifest_identity(manifest):
    name = manifest.get("name")
    version = manifest.get("version")
    architecture = manifest.get("architecture")

    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9+_.-]{0,127}", name):
        raise InstallError("Invalid package name")
    if not isinstance(version, str) or not version.strip() or len(version) > 128:
        raise InstallError("Invalid package version")
    if not isinstance(architecture, str) or not architecture.strip():
        raise InstallError("Invalid package architecture")

    host_arch = platform.machine()
    if architecture not in ("all", host_arch):
        raise InstallError(
            f"Architecture mismatch: package={architecture}, host={host_arch}"
        )


def _manifest_paths(manifest):
    result = []
    seen = set()
    reserved = ".tpm-root"

    for entry in manifest["files"]:
        path = normalize_package_path(entry["path"])
        if path == reserved or path.startswith(reserved + "/"):
            raise InstallError("Package attempts to overwrite TPM root marker")
        if path == "var/lib/tpm" or path.startswith("var/lib/tpm/"):
            raise InstallError("Package attempts to overwrite TPM database area")
        if path in seen:
            raise InstallError(f"Duplicate package path: {path}")
        seen.add(path)
        result.append(path)

    # A regular file cannot also be the parent directory of another package file.
    for path in result:
        parts = path.split("/")
        for index in range(1, len(parts)):
            parent = "/".join(parts[:index])
            if parent in seen:
                raise InstallError(f"Conflicting file paths: {parent} and {path}")

    return result


def install_package(package_path, root_path):
    root = validate_root(root_path)
    package_path = Path(package_path)
    manifest = validate_package(package_path)
    _validate_manifest_identity(manifest)
    paths = _manifest_paths(manifest)

    database = load_database(root)
    name = manifest["name"]
    if name in database["packages"]:
        raise InstallError(f"Package already installed: {name}")
    try:
        check_installed_dependencies(
            manifest.get("depends", []), database["packages"], package_name=name
        )
    except DependencyError as exc:
        raise InstallError(str(exc)) from exc

    owned_paths = {
        item["path"]
        for package in database["packages"].values()
        for item in package.get("files", [])
    }
    for path in paths:
        if path in owned_paths:
            raise InstallError(f"File is already owned by another package: {path}")
        parts = path.split("/")
        _check_existing_parent(root, parts[:-1])
        destination = root.joinpath(*parts)
        if os.path.lexists(destination):
            raise InstallError(f"Refusing to overwrite existing path: {path}")

    created_files = []
    created_directories = []

    try:
        with tarfile.open(package_path, mode="r:") as archive:
            for entry, path in zip(manifest["files"], paths):
                member = archive.getmember("payload/" + path)
                source = archive.extractfile(member)
                if source is None:
                    raise InstallError(f"Cannot read package file: {path}")

                parts = path.split("/")
                parent = _create_parent(root, parts[:-1], created_directories)
                destination = parent / parts[-1]

                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
                if hasattr(os, "O_NOFOLLOW"):
                    flags |= os.O_NOFOLLOW
                fd = os.open(destination, flags, 0o600)
                created_files.append(destination)

                digest = hashlib.sha256()
                total = 0
                with os.fdopen(fd, "wb") as output, source:
                    while True:
                        chunk = source.read(1024 * 1024)
                        if not chunk:
                            break
                        output.write(chunk)
                        digest.update(chunk)
                        total += len(chunk)
                    output.flush()
                    os.fchmod(output.fileno(), entry["mode"])
                    os.fsync(output.fileno())

                if total != entry["size"]:
                    raise InstallError(f"Size changed while installing: {path}")
                if digest.hexdigest() != entry["sha256"]:
                    raise InstallError(f"Checksum changed while installing: {path}")

        database["packages"][name] = {
            "version": manifest["version"],
            "architecture": manifest["architecture"],
            "description": manifest.get("description", ""),
            "depends": manifest.get("depends", []),
            "files": [
                {
                    "path": entry["path"],
                    "sha256": entry["sha256"],
                    "size": entry["size"],
                    "mode": entry["mode"],
                }
                for entry in manifest["files"]
            ],
        }
        save_database(root, database)

    except Exception:
        for path in reversed(created_files):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        for directory in reversed(created_directories):
            try:
                directory.rmdir()
            except OSError:
                pass
        raise

    return manifest


def list_installed(root_path):
    root = validate_root(root_path)
    return load_database(root)["packages"]


def verify_installed(root_path, package_name=None):
    root = validate_root(root_path)
    packages = load_database(root)["packages"]

    if package_name is not None and package_name not in packages:
        raise InstallError(f"Package is not installed: {package_name}")

    selected = (
        {package_name: packages[package_name]}
        if package_name is not None
        else packages
    )
    problems = []

    for name, package in selected.items():
        try:
            check_installed_dependencies(
                package.get("depends", []), packages, package_name=name
            )
        except DependencyError as exc:
            problems.append(f"{name}: {exc}")

    for name, package in selected.items():
        for entry in package.get("files", []):
            path = normalize_package_path(entry["path"])
            parts = path.split("/")
            try:
                _check_existing_parent(root, parts[:-1])
                file_path = root.joinpath(*parts)
                info = file_path.lstat()
                if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
                    raise InstallError("not a regular file")
                flags = os.O_RDONLY
                if hasattr(os, "O_NOFOLLOW"):
                    flags |= os.O_NOFOLLOW
                fd = os.open(file_path, flags)
                digest = hashlib.sha256()
                total = 0
                with os.fdopen(fd, "rb") as stream:
                    while True:
                        chunk = stream.read(1024 * 1024)
                        if not chunk:
                            break
                        digest.update(chunk)
                        total += len(chunk)
                if total != entry["size"] or digest.hexdigest() != entry["sha256"]:
                    raise InstallError("size or checksum mismatch")
            except (OSError, InstallError, ValueError) as exc:
                problems.append(f"{name}: {path}: {exc}")

    return len(selected), problems
