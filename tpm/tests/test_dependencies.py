import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from tpm import manager as manager_module
from tpm.database import initialize_root, load_database
from tpm.dependencies import DependencyError, parse_dependency
from tpm.installer import install_package, verify_installed
from tpm.manager import install_with_dependencies
from tpm.package import build_package, validate_package
from tpm.uninstaller import UninstallError, remove_package
from tpm.upgrade import UpgradeError, upgrade_package


TPM_PROJECT_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TPM_PROJECT_DIR.parent
BUILD_DIR = PROJECT_ROOT / "build"


def make_package(workspace, name, version, depends=None):
    source = workspace / f"source-{name}-{version}"
    output = workspace / f"{name}-{version}.tpk"
    payload = source / "usr" / "share" / name / "version.txt"
    payload.parent.mkdir(parents=True, exist_ok=True)
    payload.write_text(f"{name} {version}\n", encoding="utf-8")
    build_package(
        source=source,
        output=output,
        name=name,
        version=version,
        architecture=platform.machine(),
        description=f"Dependency test package {name}",
        depends=depends or [],
    )
    return output


def new_root(label, base_dir=None):
    base = Path(base_dir) if base_dir is not None else BUILD_DIR
    base.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix=f"tpm-deps-{label}-", dir=base))
    initialize_root(root)
    return root



def test_cli_build_and_local_repo_install(workspace):
    print("\n===== CLI BUILD / LOCAL REPOSITORY INSTALL =====")
    repo = workspace / "repo-cli"
    repo.mkdir()

    lib_source = workspace / "cli-lib-source"
    lib_payload = lib_source / "usr" / "share" / "cli-lib" / "version.txt"
    lib_payload.parent.mkdir(parents=True, exist_ok=True)
    lib_payload.write_text("cli-lib 1.0.0\n", encoding="utf-8")
    lib_archive = repo / "cli-lib-1.0.0.tpk"
    subprocess.run(
        [
            sys.executable, "-m", "tpm", "build", str(lib_source),
            "--name", "cli-lib", "--version", "1.0.0",
            "--arch", platform.machine(), "-o", str(lib_archive),
        ],
        cwd=TPM_PROJECT_DIR, check=True, capture_output=True, text=True,
    )

    app_source = workspace / "cli-app-source"
    app_payload = app_source / "usr" / "share" / "cli-app" / "version.txt"
    app_payload.parent.mkdir(parents=True, exist_ok=True)
    app_payload.write_text("cli-app 1.0.0\n", encoding="utf-8")
    app_archive = workspace / "cli-app-1.0.0.tpk"
    subprocess.run(
        [
            sys.executable, "-m", "tpm", "build", str(app_source),
            "--name", "cli-app", "--version", "1.0.0",
            "--arch", platform.machine(), "--depends", "cli-lib>=1.0.0",
            "-o", str(app_archive),
        ],
        cwd=TPM_PROJECT_DIR, check=True, capture_output=True, text=True,
    )

    root = new_root("cli", workspace)
    subprocess.run(
        [sys.executable, "-m", "tpm", "install", str(app_archive),
         "--root", str(root), "--repo", str(repo)],
        cwd=TPM_PROJECT_DIR, check=True, capture_output=True, text=True,
    )
    packages = load_database(root)["packages"]
    assert set(packages) == {"cli-lib", "cli-app"}
    assert packages["cli-app"]["depends"] == ["cli-lib>=1.0.0"]
    print("[PASS] CLI --depends and --repo built and installed the dependency graph")

def test_constraint_parser():
    assert parse_dependency("libfoo>=1.2.0") == {
        "name": "libfoo", "operator": ">=", "version": "1.2.0"
    }
    assert parse_dependency("libfoo=1.2.0")["operator"] == "=="
    print("[PASS] Dependency constraint parser")


def test_local_repo_install_and_remove_guard(workspace):
    print("\n===== LOCAL REPOSITORY INSTALL / REMOVE GUARD =====")
    repo = workspace / "repo-success"
    repo.mkdir()
    lib = make_package(workspace, "libmath", "1.2.0")
    app = make_package(workspace, "calculator", "1.0.0", ["libmath>=1.2.0"])
    (repo / lib.name).write_bytes(lib.read_bytes())

    root = new_root("success", workspace)
    result = install_with_dependencies(app, root, [repo])
    assert result["dependencies_installed"] == 1
    database = load_database(root)
    assert set(database["packages"]) == {"libmath", "calculator"}
    assert database["packages"]["calculator"]["depends"] == ["libmath>=1.2.0"]
    count, problems = verify_installed(root)
    assert count == 2 and not problems, problems
    print("[PASS] Missing dependency selected from local repository and installed first")
    print("[PASS] Dependency metadata persisted in the installed database")
    print("[PASS] Installed dependency graph verifies")

    try:
        remove_package("libmath", root)
    except UninstallError as exc:
        assert "required" in str(exc).lower() or "depend" in str(exc).lower()
        print(f"[PASS] Removing a required dependency was blocked: {exc}")
    else:
        raise AssertionError("TPM allowed removal of a required dependency")

    remove_package("calculator", root)
    remove_package("libmath", root)
    assert load_database(root)["packages"] == {}
    print("[PASS] Dependents can be removed before their dependencies")


def test_missing_dependency(workspace):
    print("\n===== MISSING DEPENDENCY =====")
    app = make_package(workspace, "orphan-app", "1.0.0", ["libnotfound>=1.0.0"])
    root = new_root("missing", workspace)
    try:
        install_with_dependencies(app, root, [])
    except DependencyError as exc:
        assert "No compatible local package" in str(exc)
        print(f"[PASS] Missing dependency rejected: {exc}")
    else:
        raise AssertionError("Package with missing dependency was installed")
    assert load_database(root)["packages"] == {}
    print("[PASS] No partial installation was left behind")


def test_incompatible_installed_dependency(workspace):
    print("\n===== INCOMPATIBLE INSTALLED DEPENDENCY =====")
    old_lib = make_package(workspace, "libcodec", "1.0.0")
    app = make_package(workspace, "video-tool", "1.0.0", ["libcodec>=2.0.0"])
    root = new_root("incompatible", workspace)
    install_package(old_lib, root)
    try:
        install_with_dependencies(app, root, [])
    except DependencyError as exc:
        assert "incompatible" in str(exc).lower()
        print(f"[PASS] Incompatible installed version rejected: {exc}")
    else:
        raise AssertionError("TPM accepted an incompatible installed dependency")
    packages = load_database(root)["packages"]
    assert set(packages) == {"libcodec"}
    print("[PASS] Existing package was not modified")


def test_dependency_cycle(workspace):
    print("\n===== DEPENDENCY CYCLE =====")
    repo = workspace / "repo-cycle"
    repo.mkdir()
    package_a = make_package(workspace, "cycle-a", "1.0.0", ["cycle-b>=1.0.0"])
    package_b = make_package(workspace, "cycle-b", "1.0.0", ["cycle-a>=1.0.0"])
    (repo / package_b.name).write_bytes(package_b.read_bytes())
    root = new_root("cycle", workspace)

    try:
        install_with_dependencies(package_a, root, [repo])
    except DependencyError as exc:
        assert "cycle" in str(exc).lower()
        print(f"[PASS] Circular dependency rejected: {exc}")
    else:
        raise AssertionError("TPM accepted a dependency cycle")
    assert load_database(root)["packages"] == {}
    print("[PASS] No packages were installed")


def test_upgrade_preserves_dependents(workspace):
    print("\n===== UPGRADE DEPENDENCY COMPATIBILITY =====")
    core_v2 = make_package(workspace, "libcore", "2.0.0")
    client = make_package(workspace, "core-client", "1.0.0", ["libcore<3.0.0"])
    core_v3 = make_package(workspace, "libcore", "3.0.0")
    root = new_root("reverse-upgrade", workspace)
    install_package(core_v2, root)
    install_package(client, root)

    try:
        upgrade_package(core_v3, root)
    except UpgradeError as exc:
        assert "dependents" in str(exc).lower()
        print(f"[PASS] Upgrade that breaks an installed dependent was blocked: {exc}")
    else:
        raise AssertionError("TPM allowed an upgrade that violates a dependent constraint")

    packages = load_database(root)["packages"]
    assert packages["libcore"]["version"] == "2.0.0"
    assert packages["core-client"]["version"] == "1.0.0"
    print("[PASS] Previous package versions and database were preserved")


def test_direct_install_requires_dependencies(workspace):
    print("\n===== DIRECT INSTALL DEPENDENCY CHECK =====")
    package = make_package(workspace, "direct-app", "1.0.0", ["direct-lib>=1.0.0"])
    root = new_root("direct", workspace)
    try:
        install_package(package, root)
    except Exception as exc:
        assert "dependency" in str(exc).lower()
        print(f"[PASS] Low-level installer refuses missing dependencies: {exc}")
    else:
        raise AssertionError("Low-level installer bypassed dependency checks")
    assert load_database(root)["packages"] == {}



def test_dependency_transaction_rollback(workspace):
    """A failed top-level install must remove dependencies installed in this operation."""
    print("\n===== DEPENDENCY GRAPH TRANSACTION ROLLBACK =====")
    repository = workspace / "repo-rollback"
    repository.mkdir()

    dependency_archive = make_package(workspace, "librollback", "1.0.0")
    (repository / dependency_archive.name).write_bytes(dependency_archive.read_bytes())
    application_archive = make_package(
        workspace, "rollback-app", "1.0.0", ["librollback>=1.0.0"]
    )
    root = new_root("manager-rollback", workspace)
    real_install = manager_module.install_package
    attempted = []

    def fail_on_application(archive, target_root):
        manifest = validate_package(archive)
        attempted.append(manifest["name"])
        if manifest["name"] == "rollback-app":
            raise OSError("injected failure after dependency installation")
        return real_install(archive, target_root)

    try:
        with patch.object(manager_module, "install_package", side_effect=fail_on_application):
            install_with_dependencies(application_archive, root, [repository])
    except OSError as exc:
        if "injected failure after dependency installation" not in str(exc):
            raise
        print(f"[PASS] Top-level package failure injected: {exc}")
    else:
        raise AssertionError("Injected top-level installation failure did not occur")

    assert attempted == ["librollback", "rollback-app"], attempted
    assert load_database(root)["packages"] == {}, "Dependency registration survived rollback"
    assert not (root / "usr/share/librollback/version.txt").exists(), "Dependency payload survived rollback"
    assert not (root / "usr/share/rollback-app/version.txt").exists(), "Application payload unexpectedly exists"
    print("[PASS] Dependency installed earlier in the graph was removed")
    print("[PASS] Installed-package database returned to an empty state")

    result = install_with_dependencies(application_archive, root, [repository])
    count, problems = verify_installed(root)
    assert result["dependencies_installed"] == 1
    assert count == 2 and not problems, problems
    print("[PASS] Normal dependency-graph installation succeeds after rollback")


def main():
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    test_constraint_parser()
    with tempfile.TemporaryDirectory(prefix="tpm-cli-fixtures-", dir=BUILD_DIR) as temp:
        test_cli_build_and_local_repo_install(Path(temp))
    with tempfile.TemporaryDirectory(prefix="tpm-dependency-fixtures-", dir=BUILD_DIR) as temp:
        workspace = Path(temp)
        test_local_repo_install_and_remove_guard(workspace)
        test_missing_dependency(workspace)
        test_incompatible_installed_dependency(workspace)
        test_dependency_cycle(workspace)
        test_upgrade_preserves_dependents(workspace)
        test_direct_install_requires_dependencies(workspace)
        test_dependency_transaction_rollback(workspace)
    print("\nTPM DEPENDENCY TESTS PASSED")


if __name__ == "__main__":
    main()
