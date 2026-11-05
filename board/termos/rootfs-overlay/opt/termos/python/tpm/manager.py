"""High-level package operations that coordinate dependency installation."""

from pathlib import Path

from .database import load_database, validate_root
from .dependencies import DependencyError, resolve_install_plan
from .installer import install_package
from .uninstaller import remove_package


def install_with_dependencies(package_path, root_path, repository_dirs=None):
    """Install a package plus missing local dependencies in dependency order.

    If a later package fails, packages installed by this operation are removed
    in reverse order. Packages that were already present before the operation
    are never touched.
    """
    root = validate_root(root_path)
    installed_before = load_database(root)["packages"]
    plan = resolve_install_plan(package_path, repository_dirs or [], installed_before)

    installed_now = []
    try:
        for archive, manifest in plan:
            install_package(archive, root)
            installed_now.append(manifest["name"])
    except Exception as exc:
        rollback_errors = []
        for name in reversed(installed_now):
            try:
                remove_package(name, root)
            except Exception as rollback_exc:
                rollback_errors.append(f"{name}: {rollback_exc}")
        if rollback_errors:
            raise DependencyError(
                f"Dependency installation failed ({exc}); rollback was incomplete: "
                + "; ".join(rollback_errors)
            ) from exc
        raise

    root_manifest = plan[-1][1]
    return {
        "manifest": root_manifest,
        "dependencies_installed": max(0, len(plan) - 1),
        "installed": installed_now,
    }
