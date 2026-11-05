"""Transactional package upgrades for the TermOS Package Manager."""

import hashlib
import os
import re
import shutil
import stat
import tarfile
import tempfile
from pathlib import Path

from .database import load_database, save_database, validate_root
from .dependencies import (
    DependencyError,
    check_installed_dependencies,
    check_reverse_dependencies,
)
from .installer import _manifest_paths, _validate_manifest_identity
from .package import PackageError, validate_package
from .security import normalize_package_path


class UpgradeError(Exception):
    """Raised when a package upgrade cannot be completed safely."""


def _version_key(value):
    """Parse a numeric dotted version (for example 1.2.3) for safe ordering."""
    if not isinstance(value, str) or len(value) > 128:
        raise UpgradeError("Upgrade requires numeric dotted versions such as 1.2.3")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){0,7}", value):
        raise UpgradeError(
            f"Unsupported version format: {value!r}; use numeric dotted versions such as 1.2.3"
        )
    parts = [int(part) for part in value.split(".")]
    if any(part > 2_147_483_647 for part in parts):
        raise UpgradeError("Version component is too large")
    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


def _safe_hash(path):
    """Return (size, sha256) for a regular, non-symlink file; None if absent."""
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise UpgradeError(f"Refusing to replace a non-regular file: {path}")

    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags)
    digest = hashlib.sha256()
    size = 0
    with os.fdopen(fd, "rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
    return size, digest.hexdigest()


def _check_parent(root, parts):
    current = root
    for part in parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            return
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise UpgradeError(f"Unsafe destination directory: {current}")


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
                raise UpgradeError(f"Directory disappeared: {candidate}") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise UpgradeError(f"Unsafe destination directory: {candidate}")
        current = candidate
    return current


def _transaction_parent(root):
    """Create and validate the internal transaction directory."""
    current = root
    created = []
    for part in ("var", "lib", "tpm", "transactions"):
        candidate = current / part
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            try:
                candidate.mkdir(mode=0o700 if part == "transactions" else 0o755)
                created.append(candidate)
            except FileExistsError:
                pass
            try:
                info = candidate.lstat()
            except FileNotFoundError as exc:
                raise UpgradeError(f"TPM transaction directory disappeared: {candidate}") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise UpgradeError(f"Unsafe TPM transaction directory: {candidate}")
        current = candidate
    return current, created


def _validate_installed_entries(entries):
    if not isinstance(entries, list):
        raise UpgradeError("Invalid installed package record: files must be a list")

    result = {}
    reserved = (".tpm-root", "var/lib/tpm")
    for entry in entries:
        if not isinstance(entry, dict):
            raise UpgradeError("Invalid installed package file record")
        try:
            path = normalize_package_path(entry["path"])
            size = entry["size"]
            digest = entry["sha256"]
            mode = entry["mode"]
        except (KeyError, TypeError, ValueError) as exc:
            raise UpgradeError(f"Invalid installed package file record: {exc}") from exc

        if any(path == item or path.startswith(item + "/") for item in reserved):
            raise UpgradeError(f"Installed package record references reserved path: {path}")
        if path in result:
            raise UpgradeError(f"Duplicate installed package path: {path}")
        if type(size) is not int or size < 0:
            raise UpgradeError(f"Invalid recorded file size: {path}")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)
        ):
            raise UpgradeError(f"Invalid recorded SHA-256: {path}")
        if type(mode) is not int or mode < 0 or mode > 0o777:
            raise UpgradeError(f"Invalid recorded file mode: {path}")
        result[path] = entry

    paths = set(result)
    for path in paths:
        parts = path.split("/")
        for index in range(1, len(parts)):
            parent = "/".join(parts[:index])
            if parent in paths:
                raise UpgradeError(f"Conflicting installed file paths: {parent} and {path}")
    return result


def _manifest_record(manifest):
    return {
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


def upgrade_package(package_path, root_path):
    """Upgrade one installed package, rolling files back if commit fails."""
    root = validate_root(root_path)
    package_path = Path(package_path)

    try:
        manifest = validate_package(package_path)
    except PackageError:
        raise

    _validate_manifest_identity(manifest)
    new_paths = _manifest_paths(manifest)
    name = manifest["name"]
    new_version = manifest["version"]

    database = load_database(root)
    packages = database["packages"]
    if name not in packages:
        raise UpgradeError(f"Package is not installed: {name}")

    old_record = packages[name]
    old_version = old_record.get("version")
    if _version_key(new_version) <= _version_key(old_version):
        raise UpgradeError(
            f"New version {new_version} must be greater than installed version {old_version}"
        )

    if old_record.get("architecture") != manifest["architecture"]:
        raise UpgradeError("Package architecture cannot change during an upgrade")
    try:
        check_installed_dependencies(
            manifest.get("depends", []), packages, package_name=name
        )
        check_reverse_dependencies(name, new_version, packages)
    except DependencyError as exc:
        raise UpgradeError(str(exc)) from exc

    old_entries = _validate_installed_entries(old_record.get("files"))
    new_entries = {entry["path"]: entry for entry in manifest["files"]}
    old_paths = set(old_entries)
    new_path_set = set(new_paths)

    other_owned = {
        item.get("path")
        for other_name, record in packages.items()
        if other_name != name
        for item in record.get("files", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    for path in new_path_set:
        for owned in other_owned:
            if path == owned or path.startswith(owned + "/") or owned.startswith(path + "/"):
                raise UpgradeError(f"New package path conflicts with another package: {path}")

    # Preflight every old file before making any change. Modified files are never
    # silently overwritten or removed by an upgrade.
    old_present = set()
    for relative, entry in old_entries.items():
        parts = relative.split("/")
        _check_parent(root, parts[:-1])
        destination = root.joinpath(*parts)
        actual = _safe_hash(destination)
        if actual is None:
            continue  # A missing old file can be restored by the new package.
        if actual != (entry["size"], entry["sha256"]):
            raise UpgradeError(
                f"Modified installed file detected; upgrade aborted: {relative}"
            )
        old_present.add(relative)

    # New paths not owned by the current package must be genuinely unused.
    for relative in new_path_set - old_paths:
        parts = relative.split("/")
        _check_parent(root, parts[:-1])
        destination = root.joinpath(*parts)
        if os.path.lexists(destination):
            raise UpgradeError(f"Refusing to overwrite an unowned path: {relative}")

    transaction_parent, created_internal_dirs = _transaction_parent(root)
    transaction = Path(tempfile.mkdtemp(prefix="upgrade-", dir=str(transaction_parent)))
    stage_root = transaction / "stage"
    backup_root = transaction / "backup"
    stage_root.mkdir(mode=0o700)
    backup_root.mkdir(mode=0o700)

    created_files = []
    created_directories = []
    moved_old_files = []
    committed = False

    try:
        # Extract into a private staging area first. Nothing in the installed root
        # changes until all incoming files have been rechecked and staged.
        with tarfile.open(package_path, mode="r:") as archive:
            for relative in new_paths:
                entry = new_entries[relative]
                member = archive.getmember("payload/" + relative)
                source = archive.extractfile(member)
                if source is None:
                    raise UpgradeError(f"Cannot read package file: {relative}")

                staged = stage_root.joinpath(*relative.split("/"))
                staged.parent.mkdir(parents=True, exist_ok=True)
                digest = hashlib.sha256()
                total = 0
                with staged.open("xb") as output, source:
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

                if total != entry["size"] or digest.hexdigest() != entry["sha256"]:
                    raise UpgradeError(f"Package content changed while staging: {relative}")

        # Move every still-present old file into the transaction backup. This
        # includes obsolete paths that are absent from the new version.
        for relative in sorted(old_present):
            parts = relative.split("/")
            source = root.joinpath(*parts)
            current = _safe_hash(source)
            expected = old_entries[relative]
            if current != (expected["size"], expected["sha256"]):
                raise UpgradeError(f"Installed file changed during upgrade: {relative}")
            backup = backup_root.joinpath(*parts)
            backup.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, backup)
            moved_old_files.append((source, backup))

        # Put the staged new version in place without following symlinks and
        # without overwriting an unexpected file that appeared after preflight.
        for relative in new_paths:
            entry = new_entries[relative]
            parts = relative.split("/")
            parent = _create_parent(root, parts[:-1], created_directories)
            destination = parent / parts[-1]
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            fd = os.open(destination, flags, 0o600)
            created_files.append(destination)
            staged = stage_root.joinpath(*parts)
            with os.fdopen(fd, "wb") as output, staged.open("rb") as source:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
                output.flush()
                os.fchmod(output.fileno(), entry["mode"])
                os.fsync(output.fileno())

        packages[name] = _manifest_record(manifest)
        save_database(root, database)
        committed = True

    except Exception as exc:
        rollback_errors = []

        for path in reversed(created_files):
            try:
                path.unlink(missing_ok=True)
            except OSError as rollback_exc:
                rollback_errors.append(f"remove {path}: {rollback_exc}")

        for original, backup in reversed(moved_old_files):
            try:
                if os.path.lexists(original):
                    raise OSError("original path is occupied; refusing to overwrite")
                parent = _create_parent(root, original.relative_to(root).parts[:-1], created_directories)
                os.replace(backup, parent / original.name)
            except OSError as rollback_exc:
                rollback_errors.append(f"restore {original}: {rollback_exc}")
            except UpgradeError as rollback_exc:
                rollback_errors.append(f"restore {original}: {rollback_exc}")

        if rollback_errors:
            details = "; ".join(rollback_errors)
            raise UpgradeError(
                f"Upgrade failed ({exc}); rollback was incomplete. "
                f"Recovery data remains in {transaction}: {details}"
            ) from exc

        for directory in reversed(created_directories):
            try:
                directory.rmdir()
            except OSError:
                pass

        shutil.rmtree(transaction, ignore_errors=True)
        for directory in reversed(created_internal_dirs):
            try:
                directory.rmdir()
            except OSError:
                pass

        if isinstance(exc, (UpgradeError, PackageError)):
            raise
        raise UpgradeError(f"Upgrade failed; previous version restored: {exc}") from exc

    if committed:
        shutil.rmtree(transaction)
        for directory in reversed(created_internal_dirs):
            try:
                directory.rmdir()
            except OSError:
                pass

    return {
        "name": name,
        "old_version": old_version,
        "new_version": new_version,
        "added": len(new_path_set - old_paths),
        "updated": len(new_path_set & old_paths),
        "removed": len(old_paths - new_path_set),
    }
