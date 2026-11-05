import hashlib
from pathlib import PurePosixPath


class PackageSecurityError(Exception):
    """Raised when a package path violates security rules."""


def normalize_package_path(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise PackageSecurityError("Empty package path")

    if "\x00" in value or "\\" in value:
        raise PackageSecurityError("Invalid characters in package path")

    path = PurePosixPath(value)

    if path.is_absolute():
        raise PackageSecurityError("Absolute paths are forbidden")

    if any(part in ("", ".", "..") for part in value.split("/")):
        raise PackageSecurityError("Unsafe package path")

    return path.as_posix()


def sha256_file(file_path) -> str:
    digest = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()
