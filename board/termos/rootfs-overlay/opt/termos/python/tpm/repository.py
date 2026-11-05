"""Local TPM repository indexes and Ed25519 signatures.

The repository index is canonicalized as UTF-8 JSON (sorted keys, compact
separators) before it is signed or verified. Signatures are detached OpenSSL
Ed25519 signatures; the public key must be supplied from a trusted location.
"""

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .package import PackageError, validate_package

INDEX_FORMAT = "TPM-REPOSITORY"
INDEX_VERSION = 1
DEFAULT_INDEX = "repository.json"
MAX_INDEX_BYTES = 16 * 1024 * 1024
MAX_PACKAGES = 50000
_HEX = set("0123456789abcdef")


class RepositoryError(Exception):
    """Raised for invalid repository data, files, or signatures."""


def _require_regular_file(path: Path, label: str) -> Path:
    path = Path(path).expanduser()
    try:
        path.lstat()
    except OSError as exc:
        raise RepositoryError(f"Cannot access {label}: {path}: {exc}") from exc
    if path.is_symlink() or not path.is_file():
        raise RepositoryError(f"{label} must be a regular, non-symlink file: {path}")
    return path


def _sha256_file(path: Path):
    digest = hashlib.sha256()
    size = 0
    with Path(path).open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
    return size, digest.hexdigest()


def _canonical_json(data) -> bytes:
    return json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _atomic_write(path: Path, data: bytes, mode=0o644):
    path = Path(path).expanduser()
    parent = path.parent.resolve(strict=True)
    path = parent / path.name
    if path.is_symlink():
        raise RepositoryError(f"Refusing to replace symlink: {path}")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            os.fchmod(stream.fileno(), mode)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        try:
            dir_fd = os.open(parent, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except OSError:
            pass
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise
    return path


def _dependencies_from_manifest(manifest):
    # Stage 6 metadata is normally stored under "dependencies". Accept "depends"
    # as well for compatibility with early package archives.
    value = manifest.get("dependencies", manifest.get("depends", []))
    if value is None:
        return []
    if not isinstance(value, list):
        raise RepositoryError(f"Invalid dependency metadata in {manifest.get('name', '?')}")
    result = []
    for item in value:
        if isinstance(item, str) and item.strip():
            result.append(item)
        elif isinstance(item, dict):
            if not isinstance(item.get("name"), str) or not item["name"].strip():
                raise RepositoryError("Invalid structured dependency in package manifest")
            result.append(item)
        else:
            raise RepositoryError("Invalid dependency entry in package manifest")
    return result


def build_index(repository_dir, output=None, repository_name="TermOS"):
    """Validate top-level .tpk files and create repository.json."""
    repo = Path(repository_dir).expanduser()
    if repo.is_symlink() or not repo.is_dir():
        raise RepositoryError(f"Repository path must be a real directory: {repo}")
    repo = repo.resolve(strict=True)
    if not isinstance(repository_name, str) or not repository_name.strip() or len(repository_name) > 128:
        raise RepositoryError("Repository name must contain 1..128 characters")

    archives = sorted(repo.glob("*.tpk"), key=lambda p: p.name.casefold())
    if len(archives) > MAX_PACKAGES:
        raise RepositoryError(f"Repository contains more than {MAX_PACKAGES} packages")

    packages = []
    identities = set()
    filenames = set()
    for archive in archives:
        _require_regular_file(archive, "package archive")
        try:
            manifest = validate_package(archive)
        except PackageError as exc:
            raise RepositoryError(f"Invalid package {archive.name}: {exc}") from exc

        name = manifest.get("name")
        version = manifest.get("version")
        architecture = manifest.get("architecture")
        description = manifest.get("description", "")
        if not all(isinstance(v, str) and v.strip() for v in (name, version, architecture)):
            raise RepositoryError(f"Invalid package identity in {archive.name}")
        if not isinstance(description, str):
            raise RepositoryError(f"Invalid package description in {archive.name}")

        identity = (name, version, architecture)
        if identity in identities:
            raise RepositoryError(f"Duplicate package identity: {name} {version} [{architecture}]")
        if archive.name in filenames:
            raise RepositoryError(f"Duplicate package filename: {archive.name}")
        identities.add(identity)
        filenames.add(archive.name)

        size, digest = _sha256_file(archive)
        packages.append({
            "name": name,
            "version": version,
            "architecture": architecture,
            "description": description,
            "filename": archive.name,
            "size": size,
            "sha256": digest,
            "dependencies": _dependencies_from_manifest(manifest),
        })

    index = {
        "format": INDEX_FORMAT,
        "format_version": INDEX_VERSION,
        "repository": {"name": repository_name.strip()},
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "packages": packages,
    }
    destination = Path(output).expanduser() if output is not None else repo / DEFAULT_INDEX
    if not destination.is_absolute():
        destination = Path.cwd() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(index, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    _atomic_write(destination, data, 0o644)
    return destination, index


def load_index(index_path):
    path = _require_regular_file(Path(index_path), "repository index")
    try:
        if path.stat().st_size > MAX_INDEX_BYTES:
            raise RepositoryError("Repository index is too large")
        data = json.loads(path.read_text(encoding="utf-8"))
    except RepositoryError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RepositoryError(f"Cannot read repository index: {exc}") from exc

    if not isinstance(data, dict) or data.get("format") != INDEX_FORMAT:
        raise RepositoryError("Invalid repository index format")
    if data.get("format_version") != INDEX_VERSION:
        raise RepositoryError("Unsupported repository index version")
    repository = data.get("repository")
    if not isinstance(repository, dict) or not isinstance(repository.get("name"), str):
        raise RepositoryError("Invalid repository metadata")
    packages = data.get("packages")
    if not isinstance(packages, list) or len(packages) > MAX_PACKAGES:
        raise RepositoryError("Invalid repository package list")

    seen_identities = set()
    seen_files = set()
    for item in packages:
        if not isinstance(item, dict):
            raise RepositoryError("Invalid package record in repository index")
        name, version, arch = item.get("name"), item.get("version"), item.get("architecture")
        filename, digest, size = item.get("filename"), item.get("sha256"), item.get("size")
        description, dependencies = item.get("description", ""), item.get("dependencies", [])
        if not all(isinstance(v, str) and v.strip() for v in (name, version, arch)):
            raise RepositoryError("Package record has invalid identity fields")
        if (not isinstance(filename, str) or not filename.endswith(".tpk")
                or Path(filename).name != filename or filename in (".", "..")
                or "/" in filename or "\\" in filename):
            raise RepositoryError(f"Unsafe package filename: {filename!r}")
        if type(size) is not int or size <= 0:
            raise RepositoryError(f"Invalid package size for {name}")
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in _HEX for c in digest):
            raise RepositoryError(f"Invalid SHA-256 for {name}")
        if not isinstance(description, str) or not isinstance(dependencies, list):
            raise RepositoryError(f"Invalid optional metadata for {name}")
        identity = (name, version, arch)
        if identity in seen_identities:
            raise RepositoryError(f"Duplicate package identity in index: {identity}")
        if filename in seen_files:
            raise RepositoryError(f"Duplicate package filename in index: {filename}")
        seen_identities.add(identity)
        seen_files.add(filename)
    return data


def _openssl(*args):
    executable = shutil.which("openssl")
    if not executable:
        raise RepositoryError("OpenSSL CLI not found; Ed25519 signing requires openssl")
    result = subprocess.run(
        [executable, *map(str, args)], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RepositoryError(f"OpenSSL operation failed: {detail or 'unknown error'}")
    return result.stdout.strip()


def generate_keypair(private_key, public_key, force=False):
    private_path, public_path = Path(private_key).expanduser(), Path(public_key).expanduser()
    if private_path.absolute() == public_path.absolute():
        raise RepositoryError("Private and public key paths must be different")
    for path in (private_path, public_path):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not force:
            raise RepositoryError(f"Key file already exists (use --force to replace): {path}")
        if path.is_symlink():
            raise RepositoryError(f"Refusing to use symlink key path: {path}")

    private_fd, private_tmp = tempfile.mkstemp(prefix=".tpm-ed25519-private-", dir=private_path.parent)
    os.close(private_fd)
    public_fd, public_tmp = tempfile.mkstemp(prefix=".tpm-ed25519-public-", dir=public_path.parent)
    os.close(public_fd)
    try:
        _openssl("genpkey", "-algorithm", "ED25519", "-out", private_tmp)
        _openssl("pkey", "-in", private_tmp, "-pubout", "-out", public_tmp)
        os.chmod(private_tmp, 0o600)
        os.chmod(public_tmp, 0o644)
        os.replace(private_tmp, private_path)
        os.replace(public_tmp, public_path)
    except Exception:
        for temp in (private_tmp, public_tmp):
            try:
                os.unlink(temp)
            except FileNotFoundError:
                pass
        raise
    return private_path, public_path


def _canonical_index_file(index_path):
    return _canonical_json(load_index(index_path))


def _write_temp_bytes(directory, prefix, data):
    fd, path = tempfile.mkstemp(prefix=prefix, dir=directory)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return path


def sign_index(index_path, private_key, signature_path=None):
    index_path = _require_regular_file(Path(index_path), "repository index")
    private_key = _require_regular_file(Path(private_key), "private key")
    canonical = _canonical_index_file(index_path)
    signature = Path(signature_path).expanduser() if signature_path else Path(str(index_path) + ".sig")
    signature.parent.mkdir(parents=True, exist_ok=True)
    if signature.is_symlink():
        raise RepositoryError("Refusing to replace a symlink signature file")
    with tempfile.TemporaryDirectory(prefix="tpm-sign-") as temporary:
        message_path = _write_temp_bytes(temporary, "index-", canonical)
        signature_tmp = Path(temporary) / "index.sig"
        _openssl("pkeyutl", "-sign", "-inkey", private_key, "-rawin", "-in", message_path, "-out", signature_tmp)
        data = signature_tmp.read_bytes()
    _atomic_write(signature, data, 0o644)
    return signature


def verify_index_signature(index_path, public_key, signature_path=None):
    index_path = _require_regular_file(Path(index_path), "repository index")
    public_key = _require_regular_file(Path(public_key), "trusted public key")
    signature = Path(signature_path).expanduser() if signature_path else Path(str(index_path) + ".sig")
    signature = _require_regular_file(signature, "repository signature")
    canonical = _canonical_index_file(index_path)
    with tempfile.TemporaryDirectory(prefix="tpm-verify-") as temporary:
        message_path = _write_temp_bytes(temporary, "index-", canonical)
        _openssl("pkeyutl", "-verify", "-pubin", "-inkey", public_key,
                 "-rawin", "-in", message_path, "-sigfile", signature)
    return True


def verify_repository(repository_dir, index_name=DEFAULT_INDEX, public_key=None,
                      signature_path=None, allow_unsigned=False, verify_archives=True):
    repo = Path(repository_dir).expanduser()
    if repo.is_symlink() or not repo.is_dir():
        raise RepositoryError(f"Repository path must be a real directory: {repo}")
    repo = repo.resolve(strict=True)
    index_path = Path(index_name).expanduser()
    if not index_path.is_absolute():
        index_path = repo / index_path
    index = load_index(index_path)
    sig_path = Path(signature_path).expanduser() if signature_path else Path(str(index_path) + ".sig")

    if sig_path.exists():
        if public_key is None:
            raise RepositoryError("Repository is signed but no trusted --public-key was supplied")
        verify_index_signature(index_path, public_key, sig_path)
        signature_status = "verified"
    else:
        if public_key is not None:
            raise RepositoryError("A public key was supplied but the repository signature is missing")
        if not allow_unsigned:
            raise RepositoryError("Unsigned repository rejected; explicitly use --allow-unsigned only for local testing")
        signature_status = "unsigned (explicitly allowed)"

    indexed_filenames = {item["filename"] for item in index["packages"]}
    archive_paths = list(repo.glob("*.tpk"))
    for archive_path in archive_paths:
        _require_regular_file(archive_path, "repository package archive")
    actual_filenames = {path.name for path in archive_paths}
    if actual_filenames != indexed_filenames:
        extra = sorted(actual_filenames - indexed_filenames)
        missing = sorted(indexed_filenames - actual_filenames)
        raise RepositoryError(f"Repository archive inventory differs from index; extra={extra}, missing={missing}")

    checked = 0
    if verify_archives:
        for item in index["packages"]:
            archive = repo / item["filename"]
            _require_regular_file(archive, "indexed package archive")
            size, digest = _sha256_file(archive)
            if size != item["size"] or digest != item["sha256"]:
                raise RepositoryError(f"Package archive does not match signed index: {item['filename']}")
            checked += 1
    return {
        "repository": index["repository"]["name"],
        "packages": len(index["packages"]),
        "archives_verified": checked,
        "signature": signature_status,
        "index_path": str(index_path),
    }


def search_packages(repository_dir, query, index_name=DEFAULT_INDEX, public_key=None,
                    signature_path=None, allow_unsigned=False):
    if not isinstance(query, str) or not query.strip():
        raise RepositoryError("Search query cannot be empty")
    repo = Path(repository_dir).expanduser().resolve(strict=True)
    verification = verify_repository(
        repo, index_name=index_name, public_key=public_key,
        signature_path=signature_path, allow_unsigned=allow_unsigned,
        verify_archives=True,
    )
    index_path = Path(index_name).expanduser()
    if not index_path.is_absolute():
        index_path = repo / index_path
    index = load_index(index_path)
    terms = query.casefold().split()
    matches = []
    for item in index["packages"]:
        haystack = " ".join((item["name"], item["version"], item["architecture"], item.get("description", ""))).casefold()
        if all(term in haystack for term in terms):
            matches.append(item)
    matches.sort(key=lambda item: (item["name"].casefold(), item["version"], item["architecture"]))
    return matches, verification
