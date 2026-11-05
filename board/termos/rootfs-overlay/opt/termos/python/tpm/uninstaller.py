import hashlib
import os
import re
import shutil
import stat
import tempfile
from pathlib import Path

from .database import load_database, save_database, validate_root
from .dependencies import DependencyError, find_dependents
from .security import normalize_package_path


class UninstallError(Exception):
    pass


def _ensure_internal_directory(root, parts):
    current = root
    for part in parts:
        candidate = current / part
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            try:
                candidate.mkdir(mode=0o700)
            except FileExistsError:
                pass
            try:
                info = candidate.lstat()
            except FileNotFoundError as exc:
                raise UninstallError(f"Internal directory disappeared: {candidate}") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise UninstallError(f"Unsafe TPM internal directory: {candidate}")
        current = candidate
    return current


def _check_parent_directories(root, parts):
    current = root
    for part in parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            return False
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise UninstallError(f"Unsafe path component: {current}")
    return True


def _hash_regular_file(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None

    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise UninstallError(f"Refusing to remove a non-regular file: {path}")

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


def remove_package(package_name, root_path, keep_modified=False):
    if not isinstance(package_name, str) or not re.fullmatch(
        r"[a-z0-9][a-z0-9+_.-]{0,127}", package_name
    ):
        raise UninstallError("Invalid package name")

    root = validate_root(root_path)
    database = load_database(root)
    packages = database["packages"]

    if package_name not in packages:
        raise UninstallError(f"Package is not installed: {package_name}")
    try:
        blockers = find_dependents(package_name, packages)
    except DependencyError as exc:
        raise UninstallError(f"Cannot safely check dependents: {exc}") from exc
    if blockers:
        details = ", ".join(f"{name} ({spec})" for name, spec in blockers)
        raise UninstallError(
            f"Cannot remove {package_name}; it is required by installed package(s): {details}"
        )

    package = packages[package_name]
    entries = package.get("files")
    if not isinstance(entries, list):
        raise UninstallError("Invalid package record in TPM database")

    checked = []
    seen = set()
    modified = []
    missing = []

    # Complete preflight before moving or deleting anything.
    for entry in entries:
        if not isinstance(entry, dict):
            raise UninstallError("Invalid file record in TPM database")
        try:
            relative = normalize_package_path(entry["path"])
            expected_size = entry["size"]
            expected_hash = entry["sha256"]
        except (KeyError, TypeError, ValueError) as exc:
            raise UninstallError(f"Invalid file record: {exc}") from exc

        if relative in seen:
            raise UninstallError(f"Duplicate file record: {relative}")
        seen.add(relative)

        parts = relative.split("/")
        if relative == ".tpm-root" or relative.startswith(".tpm-root/"):
            raise UninstallError("Package record references reserved TPM marker")
        if relative == "var/lib/tpm" or relative.startswith("var/lib/tpm/"):
            raise UninstallError("Package record references reserved TPM database area")
        if type(expected_size) is not int or expected_size < 0:
            raise UninstallError(f"Invalid recorded size: {relative}")
        if (
            not isinstance(expected_hash, str)
            or len(expected_hash) != 64
            or any(char not in "0123456789abcdef" for char in expected_hash)
        ):
            raise UninstallError(f"Invalid recorded SHA-256: {relative}")

        if not _check_parent_directories(root, parts[:-1]):
            missing.append(relative)
            continue

        destination = root.joinpath(*parts)
        actual = _hash_regular_file(destination)
        if actual is None:
            missing.append(relative)
            continue

        if actual != (expected_size, expected_hash):
            modified.append(relative)
        else:
            checked.append((relative, destination))

    if modified and not keep_modified:
        preview = ", ".join(modified[:5])
        if len(modified) > 5:
            preview += f", and {len(modified) - 5} more"
        raise UninstallError(
            "Modified files detected; nothing was removed. "
            f"Use --keep-modified to leave them in place: {preview}"
        )

    transaction_parent = _ensure_internal_directory(
        root, ("var", "lib", "tpm", "transactions")
    )
    transaction = Path(
        tempfile.mkdtemp(prefix="remove-", dir=str(transaction_parent))
    )
    moved = []
    committed = False

    try:
        for relative, source in checked:
            parts = relative.split("/")
            backup = transaction.joinpath(*parts)
            backup.parent.mkdir(parents=True, exist_ok=True)

            # Re-check immediately before moving the file.
            if not _check_parent_directories(root, parts[:-1]):
                raise UninstallError(f"File parent disappeared: {relative}")
            current = _hash_regular_file(source)
            expected = next(
                (item["size"], item["sha256"])
                for item in entries
                if item["path"] == relative
            )
            if current != expected:
                raise UninstallError(f"File changed during removal: {relative}")

            os.replace(source, backup)
            moved.append((source, backup))

        del packages[package_name]
        save_database(root, database)
        committed = True

    except Exception as exc:
        rollback_errors = []
        for original, backup in reversed(moved):
            try:
                relative_parts = original.relative_to(root).parts
                if not _check_parent_directories(root, relative_parts[:-1]):
                    raise OSError("original parent directory is missing")
                if os.path.lexists(original):
                    raise OSError("original path is occupied; refusing to overwrite")
                os.replace(backup, original)
            except OSError as rollback_exc:
                rollback_errors.append(f"{original}: {rollback_exc}")

        if rollback_errors:
            details = "; ".join(rollback_errors)
            raise UninstallError(
                f"Removal failed ({exc}); rollback was incomplete. "
                f"Recovery files remain in {transaction}: {details}"
            ) from exc
        shutil.rmtree(transaction, ignore_errors=True)
        if isinstance(exc, UninstallError):
            raise
        raise UninstallError(f"Removal failed; changes rolled back: {exc}") from exc

    cleanup_warning = None
    if committed:
        try:
            shutil.rmtree(transaction)
        except OSError as exc:
            cleanup_warning = (
                f"Package was removed, but temporary backup data remains at "
                f"{transaction}: {exc}"
            )

    return {
        "name": package_name,
        "removed": len(moved),
        "modified_kept": modified if keep_modified else [],
        "missing": missing,
        "cleanup_warning": cleanup_warning,
    }
