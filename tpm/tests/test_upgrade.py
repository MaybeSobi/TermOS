import os
import platform
import shutil
import stat
import tempfile
from pathlib import Path
from unittest.mock import patch

from tpm import upgrade as upgrade_module
from tpm.database import initialize_root, load_database
from tpm.installer import install_package, verify_installed
from tpm.package import build_package
from tpm.upgrade import UpgradeError, upgrade_package


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUILD_DIR = PROJECT_ROOT / "build"


def snapshot_tree(root):
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


def create_package(source, output, version, files):
    for relative, (content, mode) in files.items():
        path = source.joinpath(*relative.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        path.chmod(mode)
    return build_package(
        source=source,
        output=output,
        name="hello-upgrade",
        version=version,
        architecture=platform.machine(),
        description="TPM upgrade integration test",
    )


def expect_upgrade_error(package, root, label):
    try:
        upgrade_package(package, root)
    except UpgradeError as exc:
        print(f"[PASS] {label}: {exc}")
        return
    raise AssertionError(f"Expected upgrade rejection: {label}")


def make_fixture(workspace):
    source_v1 = workspace / "source-v1"
    source_v2 = workspace / "source-v2"
    package_v1 = workspace / "hello-upgrade-1.0.0.tpk"
    package_v2 = workspace / "hello-upgrade-1.1.0.tpk"

    create_package(
        source_v1,
        package_v1,
        "1.0.0",
        {
            "usr/bin/hello-upgrade": ("#!/bin/sh\necho Version 1\n", 0o755),
            "usr/share/doc/hello-upgrade/kept.txt": ("old documentation\n", 0o644),
            "usr/share/doc/hello-upgrade/obsolete.txt": ("obsolete file\n", 0o644),
        },
    )
    create_package(
        source_v2,
        package_v2,
        "1.1.0",
        {
            "usr/bin/hello-upgrade": ("#!/bin/sh\necho Version 2\n", 0o755),
            "usr/share/doc/hello-upgrade/kept.txt": ("updated documentation\n", 0o644),
            "usr/share/doc/hello-upgrade/added.txt": ("new documentation\n", 0o644),
        },
    )
    return package_v1, package_v2


def new_root(label, base_dir=None):
    base = Path(base_dir) if base_dir is not None else BUILD_DIR
    base.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix=f"tpm-upgrade-{label}-", dir=base))
    initialize_root(root)
    return root


def test_success_and_version_rules(package_v1, package_v2, workspace: Path | None = None):
    print("===== SUCCESSFUL UPGRADE / VERSION RULES =====")
    root = new_root("success", workspace)
    install_package(package_v1, root)
    untouched = root / "etc/local-note.txt"
    untouched.parent.mkdir(parents=True, exist_ok=True)
    untouched.write_text("leave me alone\n", encoding="utf-8")

    result = upgrade_package(package_v2, root)
    database = load_database(root)
    record = database["packages"]["hello-upgrade"]

    assert result["old_version"] == "1.0.0"
    assert result["new_version"] == "1.1.0"
    assert record["version"] == "1.1.0"
    assert (root / "usr/bin/hello-upgrade").read_text(encoding="utf-8").endswith("Version 2\n")
    assert (root / "usr/share/doc/hello-upgrade/added.txt").is_file()
    assert (root / "usr/share/doc/hello-upgrade/kept.txt").read_text(encoding="utf-8") == "updated documentation\n"
    assert not (root / "usr/share/doc/hello-upgrade/obsolete.txt").exists()
    assert untouched.read_text(encoding="utf-8") == "leave me alone\n"

    count, problems = verify_installed(root)
    assert count == 1 and not problems, problems
    print("[PASS] Existing files updated, new file added, obsolete file removed")
    print("[PASS] Unowned files were preserved")
    print("[PASS] Database records the new version")
    print("[PASS] Installed package verifies after upgrade")

    expect_upgrade_error(package_v1, root, "Downgrade rejected")
    expect_upgrade_error(package_v2, root, "Same-version upgrade rejected")


def test_modified_file_protection(package_v1, package_v2, workspace: Path | None = None):
    print("\n===== MODIFIED FILE PROTECTION =====")
    root = new_root("modified", workspace)
    install_package(package_v1, root)
    executable = root / "usr/bin/hello-upgrade"
    executable.write_text(executable.read_text(encoding="utf-8") + "# local edit\n", encoding="utf-8")
    before = snapshot_tree(root)
    expect_upgrade_error(package_v2, root, "Modified installed file blocked upgrade")
    assert snapshot_tree(root) == before
    print("[PASS] Files and database remained unchanged")


def test_unowned_collision(package_v1, package_v2, workspace: Path | None = None):
    print("\n===== UNOWNED PATH COLLISION =====")
    root = new_root("collision", workspace)
    install_package(package_v1, root)
    collision = root / "usr/share/doc/hello-upgrade/added.txt"
    collision.parent.mkdir(parents=True, exist_ok=True)
    collision.write_text("user-owned file\n", encoding="utf-8")
    before = snapshot_tree(root)
    expect_upgrade_error(package_v2, root, "Unowned destination collision blocked")
    assert snapshot_tree(root) == before
    print("[PASS] Existing unowned file was preserved")


def test_mid_apply_rollback(package_v1, package_v2, workspace: Path | None = None):
    print("\n===== ROLLBACK: FAILURE DURING FILE REPLACEMENT =====")
    root = new_root("mid-apply", workspace)
    install_package(package_v1, root)
    before = snapshot_tree(root)
    real_open = os.open
    target_creates = []

    def fail_on_second_target_create(path, flags, mode=0o777, *, dir_fd=None):
        candidate = Path(path)
        try:
            relative = candidate.resolve(strict=False).relative_to(root)
        except (OSError, ValueError):
            relative = None
        if flags & os.O_CREAT and relative is not None and relative.parts and relative.parts[0] == "usr":
            target_creates.append(relative.as_posix())
            if len(target_creates) == 2:
                raise OSError("injected TPM upgrade failure on second new file")
        if dir_fd is None:
            return real_open(path, flags, mode)
        return real_open(path, flags, mode, dir_fd=dir_fd)

    try:
        with patch.object(upgrade_module.os, "open", side_effect=fail_on_second_target_create):
            upgrade_package(package_v2, root)
    except UpgradeError as exc:
        assert "injected TPM upgrade failure" in str(exc), exc
        print(f"[PASS] Mid-upgrade failure injected: {exc}")
    else:
        raise AssertionError("Injected mid-upgrade failure did not occur")

    after = snapshot_tree(root)
    assert after == before, "Sandbox differs from pre-upgrade state after rollback"
    assert load_database(root)["packages"]["hello-upgrade"]["version"] == "1.0.0"
    print("[PASS] Previous files and database were fully restored")

    result = upgrade_package(package_v2, root)
    assert result["new_version"] == "1.1.0"
    count, problems = verify_installed(root)
    assert count == 1 and not problems, problems
    print("[PASS] A normal upgrade succeeds after rollback")


def test_database_commit_rollback(package_v1, package_v2, workspace: Path | None = None):
    print("\n===== ROLLBACK: DATABASE COMMIT FAILURE =====")
    root = new_root("db-commit", workspace)
    install_package(package_v1, root)
    before = snapshot_tree(root)

    with patch.object(
        upgrade_module,
        "save_database",
        side_effect=OSError("injected TPM upgrade database commit failure"),
    ):
        try:
            upgrade_package(package_v2, root)
        except UpgradeError as exc:
            assert "previous version restored" in str(exc), exc
            print(f"[PASS] Database failure injected and handled: {exc}")
        else:
            raise AssertionError("Injected database commit failure did not occur")

    assert snapshot_tree(root) == before, "Sandbox differs after database failure rollback"
    assert load_database(root)["packages"]["hello-upgrade"]["version"] == "1.0.0"
    print("[PASS] Previous files and database were fully restored")

    result = upgrade_package(package_v2, root)
    assert result["new_version"] == "1.1.0"
    print("[PASS] A normal upgrade succeeds after database failure")


def main():
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tpm-upgrade-fixture-", dir=BUILD_DIR) as temporary:
        workspace = Path(temporary)
        package_v1, package_v2 = make_fixture(workspace)
        print("TPM UPGRADE TESTS")
        print(f"Packages: {package_v1.name} -> {package_v2.name}")
        test_success_and_version_rules(package_v1, package_v2)
        test_modified_file_protection(package_v1, package_v2)
        test_unowned_collision(package_v1, package_v2)
        test_mid_apply_rollback(package_v1, package_v2)
        test_database_commit_rollback(package_v1, package_v2)
        print("\nTPM UPGRADE TESTS PASSED")


if __name__ == "__main__":
    main()
