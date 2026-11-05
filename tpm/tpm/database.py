import json
import os
import stat
import tempfile
from pathlib import Path

MARKER_NAME = ".tpm-root"
MARKER_CONTENT = "TermOS TPM sandbox root v1\n"
DB_PARTS = ("var", "lib", "tpm", "installed.json")
DB_MAX_SIZE = 16 * 1024 * 1024


class DatabaseError(Exception):
    pass


def _check_root_argument(path):
    raw = Path(path).expanduser()
    if raw.is_symlink():
        raise DatabaseError("Root path itself cannot be a symlink")
    raw.mkdir(parents=True, exist_ok=True)
    root = raw.resolve(strict=True)
    if root == Path("/"):
        raise DatabaseError("Refusing to use / as a TPM sandbox root")
    if not root.is_dir():
        raise DatabaseError("Root must be a directory")
    return root


def initialize_root(path):
    root = _check_root_argument(path)
    marker = root / MARKER_NAME

    try:
        info = marker.lstat()
    except FileNotFoundError:
        info = None

    if info is not None:
        if not stat.S_ISREG(info.st_mode) or marker.is_symlink():
            raise DatabaseError("Invalid TPM root marker")
        if marker.read_text(encoding="utf-8") != MARKER_CONTENT:
            raise DatabaseError("TPM root marker has unexpected content")
        return root

    if any(root.iterdir()):
        raise DatabaseError("Refusing to initialize a non-empty directory")

    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(marker, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(MARKER_CONTENT)
        stream.flush()
        os.fsync(stream.fileno())
    return root


def validate_root(path):
    raw = Path(path).expanduser()
    if raw.is_symlink():
        raise DatabaseError("Root path itself cannot be a symlink")
    root = raw.resolve(strict=True)
    if root == Path("/"):
        # The live system root is intentionally unavailable to ordinary TPM
        # operations. The installed /usr/bin/tpm launcher sets this opt-in only
        # after checking root privileges, the TermOS release marker, and a
        # typed confirmation for mutating commands.
        if os.environ.get("TPM_ALLOW_SYSTEM_ROOT") != "1":
            raise DatabaseError(
                "Refusing the live system root. Use the installed 'tpm --system' "
                "launcher on TermOS."
            )
        if not hasattr(os, "geteuid") or os.geteuid() != 0:
            raise DatabaseError("System-root operations require effective UID 0")
        release_marker = root / "etc" / "termos-release"
        try:
            marker_info = release_marker.lstat()
            marker_text = release_marker.read_text(encoding="utf-8")
        except OSError as exc:
            raise DatabaseError(f"Cannot validate TermOS system marker: {exc}") from exc
        if not stat.S_ISREG(marker_info.st_mode) or stat.S_ISLNK(marker_info.st_mode):
            raise DatabaseError("TermOS system marker is not a regular file")
        if "ID=termos" not in marker_text.splitlines():
            raise DatabaseError("This root filesystem is not identified as TermOS")
        return root
    if not root.is_dir():
        raise DatabaseError("Invalid TPM sandbox root")

    marker = root / MARKER_NAME
    try:
        info = marker.lstat()
    except FileNotFoundError as exc:
        raise DatabaseError("Not a TPM sandbox. Run 'tpm init-root' first") from exc
    if not stat.S_ISREG(info.st_mode) or marker.is_symlink():
        raise DatabaseError("Invalid TPM root marker")
    if marker.read_text(encoding="utf-8") != MARKER_CONTENT:
        raise DatabaseError("TPM root marker has unexpected content")
    return root


def _safe_directory(root, parts, create=False):
    current = root
    for part in parts:
        candidate = current / part
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            if not create:
                return None
            try:
                candidate.mkdir(mode=0o755)
            except FileExistsError:
                pass
            try:
                info = candidate.lstat()
            except FileNotFoundError as exc:
                raise DatabaseError(f"Directory disappeared: {candidate}") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise DatabaseError(f"Unsafe directory component: {candidate}")
        current = candidate
    return current


def empty_database():
    return {"format_version": 1, "packages": {}}


def load_database(root):
    parent = _safe_directory(root, DB_PARTS[:-1], create=False)
    if parent is None:
        return empty_database()

    database_path = parent / DB_PARTS[-1]
    try:
        info = database_path.lstat()
    except FileNotFoundError:
        return empty_database()

    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise DatabaseError("TPM database is not a regular file")
    if info.st_size > DB_MAX_SIZE:
        raise DatabaseError("TPM database is too large")

    try:
        data = json.loads(database_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DatabaseError(f"Cannot read TPM database: {exc}") from exc

    if (
        not isinstance(data, dict)
        or data.get("format_version") != 1
        or not isinstance(data.get("packages"), dict)
    ):
        raise DatabaseError("Invalid TPM database structure")
    return data


def save_database(root, data):
    parent = _safe_directory(root, DB_PARTS[:-1], create=True)
    database_path = parent / DB_PARTS[-1]

    try:
        info = database_path.lstat()
    except FileNotFoundError:
        info = None
    if info is not None and (stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode)):
        raise DatabaseError("Refusing to replace an unsafe TPM database file")

    payload = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if len(payload) > DB_MAX_SIZE:
        raise DatabaseError("TPM database would exceed size limit")

    fd, temporary_name = tempfile.mkstemp(prefix=".installed-", suffix=".tmp", dir=parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, database_path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
