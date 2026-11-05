import os
import shutil
import stat
import tempfile
from pathlib import Path
from unittest.mock import patch

from tpm import installer
from tpm.database import initialize_root, load_database
from tpm.installer import install_package, verify_installed


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKAGE = PROJECT_ROOT / "packages" / "hello-termos-1.0.0-x86_64.tpk"


def snapshot_tree(root: Path):
    """Capture paths, types, file bytes, and modes beneath a sandbox root."""
    snapshot = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        info = path.lstat()
        mode = stat.S_IMODE(info.st_mode)
        if stat.S_ISLNK(info.st_mode):
            snapshot[relative] = ("symlink", os.readlink(path), mode)
        elif stat.S_ISDIR(info.st_mode):
            snapshot[relative] = ("directory", mode)
        elif stat.S_ISREG(info.st_mode):
            snapshot[relative] = ("file", path.read_bytes(), mode)
        else:
            snapshot[relative] = ("special", info.st_mode, mode)
    return snapshot


def new_root(label: str, base_dir: Path | None = None) -> Path:
    build_dir = Path(base_dir) if base_dir is not None else PROJECT_ROOT / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix=f"tpm-rollback-{label}-", dir=build_dir))
    initialize_root(root)
    return root


def assert_clean_after_failure(root: Path, before):
    after = snapshot_tree(root)
    if after != before:
        before_keys = set(before)
        after_keys = set(after)
        added = sorted(after_keys - before_keys)
        missing = sorted(before_keys - after_keys)
        changed = sorted(
            key for key in before_keys & after_keys if before[key] != after[key]
        )
        raise AssertionError(
            "Sandbox differs from its pre-install state. "
            f"Added={added}; missing={missing}; changed={changed}"
        )

    database = load_database(root)
    if database.get("packages") != {}:
        raise AssertionError("Package database changed despite failed installation")


def test_failure_after_first_file(package: Path, workspace: Path | None = None):
    print("===== ROLLBACK: FAILURE DURING FILE INSTALLATION =====")
    root = new_root("mid-file", workspace)
    before = snapshot_tree(root)
    real_open = os.open
    attempted_package_files = []

    def fail_on_second_package_file(path, flags, mode=0o777, *, dir_fd=None):
        candidate = Path(path)
        try:
            relative = candidate.resolve(strict=False).relative_to(root)
        except (OSError, ValueError):
            relative = None

        if relative is not None and relative.parts and relative.parts[0] == "usr":
            attempted_package_files.append(relative.as_posix())
            if len(attempted_package_files) == 2:
                raise OSError("injected TPM test failure on second package file")

        if dir_fd is None:
            return real_open(path, flags, mode)
        return real_open(path, flags, mode, dir_fd=dir_fd)

    try:
        with patch.object(installer.os, "open", side_effect=fail_on_second_package_file):
            install_package(package, root)
    except OSError as exc:
        if "injected TPM test failure" not in str(exc):
            raise
        print(f"[PASS] Injected failure occurred: {exc}")
    else:
        raise AssertionError("Injected mid-install failure did not occur")

    if len(attempted_package_files) != 2:
        raise AssertionError(
            f"Expected failure on second package file; observed {attempted_package_files}"
        )

    assert_clean_after_failure(root, before)
    print("[PASS] First installed file and newly created directories were rolled back")
    print("[PASS] Package database is unchanged")

    # Prove the sandbox remains usable after rollback.
    manifest = install_package(package, root)
    count, problems = verify_installed(root)
    if problems or count != 1 or manifest.get("name") != "hello-termos":
        raise AssertionError(f"Sandbox did not recover after rollback: {problems}")
    print("[PASS] A normal installation succeeds after rollback")
    print(f"Sandbox retained: {root.relative_to(PROJECT_ROOT)}")


def test_database_commit_failure(package: Path, workspace: Path | None = None):
    print()
    print("===== ROLLBACK: DATABASE COMMIT FAILURE =====")
    root = new_root("db-commit", workspace)
    before = snapshot_tree(root)

    with patch.object(
        installer,
        "save_database",
        side_effect=OSError("injected TPM test database commit failure"),
    ):
        try:
            install_package(package, root)
        except OSError as exc:
            if "injected TPM test database commit failure" not in str(exc):
                raise
            print(f"[PASS] Database commit failure injected: {exc}")
        else:
            raise AssertionError("Injected database commit failure did not occur")

    assert_clean_after_failure(root, before)
    print("[PASS] All payload files were removed after database commit failure")
    print("[PASS] Package database remains empty and unchanged")

    # Verify that a later normal operation can still use this root.
    install_package(package, root)
    count, problems = verify_installed(root)
    if problems or count != 1:
        raise AssertionError(f"Sandbox did not recover after database failure: {problems}")
    print("[PASS] A normal installation succeeds after database failure")
    print(f"Sandbox retained: {root.relative_to(PROJECT_ROOT)}")


def main():
    package = DEFAULT_PACKAGE
    if not package.is_file():
        raise SystemExit(
            f"Missing package: {package.relative_to(PROJECT_ROOT)}\n"
            "Build it first with: ./test_tpm.sh"
        )

    print("TPM INSTALL ROLLBACK TESTS")
    print(f"Package: {package.relative_to(PROJECT_ROOT)}")
    test_failure_after_first_file(package)
    test_database_commit_failure(package)
    print()
    print("TPM ROLLBACK TESTS PASSED")


if __name__ == "__main__":
    main()
