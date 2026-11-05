"""Dependency metadata, constraints, and local package resolution for TPM."""

import platform
import re
from pathlib import Path

PACKAGE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9+_.-]{0,127}$")
DEPENDENCY_RE = re.compile(
    r"^(?P<name>[a-z0-9][a-z0-9+_.-]{0,127})"
    r"(?:(?P<operator>>=|<=|==|>|<|=)(?P<version>[0-9]+(?:\.[0-9]+){0,7}))?$"
)
MAX_DEPENDENCIES = 256
MAX_REPOSITORY_PACKAGES = 2000


class DependencyError(Exception):
    """Raised when package dependencies cannot be satisfied safely."""


def version_key(value):
    """Convert a numeric dotted version into a comparable tuple."""
    if not isinstance(value, str) or len(value) > 128:
        raise DependencyError(f"Invalid version: {value!r}")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){0,7}", value):
        raise DependencyError(
            f"Unsupported version {value!r}; use numeric dotted versions such as 1.2.3"
        )
    parts = [int(part) for part in value.split(".")]
    if any(part > 2_147_483_647 for part in parts):
        raise DependencyError("Version component is too large")
    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


def parse_dependency(spec):
    """Parse 'name', 'name>=1.2.0', 'name==1.2.0', etc."""
    if not isinstance(spec, str):
        raise DependencyError("Dependency specifications must be strings")
    match = DEPENDENCY_RE.fullmatch(spec)
    if not match:
        raise DependencyError(
            f"Invalid dependency {spec!r}; examples: libfoo or libfoo>=1.2.0"
        )
    name = match.group("name")
    operator = match.group("operator")
    version = match.group("version")
    if operator == "=":
        operator = "=="
    if version is not None:
        version_key(version)
    return {"name": name, "operator": operator, "version": version}


def validate_dependencies(items, package_name=None):
    """Validate and canonicalize dependency strings; missing means no dependencies."""
    if items is None:
        return []
    if not isinstance(items, (list, tuple)):
        raise DependencyError("Manifest 'depends' must be a list of dependency strings")
    if len(items) > MAX_DEPENDENCIES:
        raise DependencyError(f"A package may declare at most {MAX_DEPENDENCIES} dependencies")

    result = []
    seen = set()
    for item in items:
        parsed = parse_dependency(item)
        if package_name and parsed["name"] == package_name:
            raise DependencyError(f"Package cannot depend on itself: {package_name}")
        canonical = (
            parsed["name"]
            + (parsed["operator"] + parsed["version"] if parsed["operator"] else "")
        )
        if canonical in seen:
            raise DependencyError(f"Duplicate dependency: {canonical}")
        seen.add(canonical)
        result.append(canonical)
    return result


def dependency_satisfied(spec, installed_version):
    parsed = parse_dependency(spec)
    if parsed["operator"] is None:
        return True
    try:
        actual = version_key(installed_version)
        required = version_key(parsed["version"])
    except DependencyError:
        return False

    operator = parsed["operator"]
    if operator == ">=":
        return actual >= required
    if operator == "<=":
        return actual <= required
    if operator == ">":
        return actual > required
    if operator == "<":
        return actual < required
    if operator == "==":
        return actual == required
    raise DependencyError(f"Unsupported dependency operator: {operator}")


def check_installed_dependencies(depends, installed_packages, package_name=None):
    for spec in validate_dependencies(depends, package_name=package_name):
        parsed = parse_dependency(spec)
        record = installed_packages.get(parsed["name"])
        if record is None:
            raise DependencyError(
                f"Missing dependency: {spec}. Install it first or provide a local --repo."
            )
        installed_version = record.get("version")
        if not dependency_satisfied(spec, installed_version):
            raise DependencyError(
                f"Dependency version mismatch: {spec}; "
                f"installed {parsed['name']} is {installed_version!r}"
            )


def find_dependents(package_name, installed_packages, exclude=None):
    """Return installed package/spec pairs that declare a dependency on package_name."""
    blockers = []
    for other_name, record in installed_packages.items():
        if other_name == exclude or other_name == package_name:
            continue
        depends = validate_dependencies(record.get("depends", []), package_name=other_name)
        for spec in depends:
            if parse_dependency(spec)["name"] == package_name:
                blockers.append((other_name, spec))
    return blockers


def check_reverse_dependencies(package_name, new_version, installed_packages):
    """Prevent upgrading a package to a version that breaks installed dependents."""
    blockers = [
        (other_name, spec)
        for other_name, spec in find_dependents(
            package_name, installed_packages, exclude=package_name
        )
        if not dependency_satisfied(spec, new_version)
    ]
    if blockers:
        details = ", ".join(f"{name} requires {spec}" for name, spec in blockers)
        raise DependencyError(
            f"Upgrade to {new_version} would break installed dependents: {details}"
        )


def resolve_install_plan(package_path, repository_dirs, installed_packages):
    """Resolve a package and its missing dependencies from local .tpk repositories.

    Returns a topologically ordered list of (archive_path, manifest) pairs.
    Existing installed dependencies must already satisfy their constraints; this
    first resolver does not silently replace or upgrade installed dependencies.
    """
    from .package import validate_package

    root_archive = Path(package_path).expanduser()
    if not root_archive.is_file() or root_archive.is_symlink():
        raise DependencyError(f"Package archive is missing or unsafe: {root_archive}")
    root_archive = root_archive.resolve()
    root_manifest = validate_package(root_archive)
    root_name = root_manifest.get("name")
    if root_name in installed_packages:
        raise DependencyError(f"Package already installed: {root_name}")

    candidates = {}
    seen_archives = set()

    def add_candidate(archive):
        archive = Path(archive)
        try:
            if archive.is_symlink() or not archive.is_file():
                return
            archive = archive.resolve()
            if archive in seen_archives:
                return
            seen_archives.add(archive)
            manifest = validate_package(archive)
            name = manifest.get("name")
            version = manifest.get("version")
            architecture = manifest.get("architecture")
            if not isinstance(name, str) or not PACKAGE_NAME_RE.fullmatch(name):
                return
            if architecture not in ("all", platform.machine()):
                return
            key = version_key(version)
            candidates.setdefault(name, []).append((key, archive, manifest))
        except (OSError, DependencyError, ValueError):
            return
        except Exception:
            # Invalid or unrelated repository archives are not candidates.
            return

    add_candidate(root_archive)
    archive_count = 0
    for repository in repository_dirs or []:
        repository = Path(repository).expanduser()
        if repository.is_symlink() or not repository.is_dir():
            raise DependencyError(f"Repository must be an existing non-symlink directory: {repository}")
        for archive in sorted(repository.glob("*.tpk")):
            archive_count += 1
            if archive_count > MAX_REPOSITORY_PACKAGES:
                raise DependencyError(
                    f"Local repository exceeds {MAX_REPOSITORY_PACKAGES} package archives"
                )
            add_candidate(archive)

    for values in candidates.values():
        values.sort(key=lambda item: (item[0], str(item[1])), reverse=True)

    visiting = []
    planned = {}
    ordered = []

    def visit(archive, manifest):
        name = manifest["name"]
        if name in planned:
            return
        if name in visiting:
            cycle = " -> ".join(visiting + [name])
            raise DependencyError(f"Dependency cycle detected: {cycle}")

        visiting.append(name)
        for spec in validate_dependencies(manifest.get("depends", []), package_name=name):
            parsed = parse_dependency(spec)
            dependency_name = parsed["name"]

            installed = installed_packages.get(dependency_name)
            if installed is not None:
                if dependency_satisfied(spec, installed.get("version")):
                    continue
                raise DependencyError(
                    f"Installed dependency is incompatible: {spec}; "
                    f"{dependency_name} {installed.get('version')!r} is installed. "
                    "Upgrade it explicitly before installing this package."
                )

            already_planned = planned.get(dependency_name)
            if already_planned is not None:
                if not dependency_satisfied(spec, already_planned["manifest"]["version"]):
                    raise DependencyError(
                        f"Conflicting dependency constraints for {dependency_name}: {spec}"
                    )
                continue

            matching = [
                item for item in candidates.get(dependency_name, [])
                if dependency_satisfied(spec, item[2]["version"])
            ]
            if not matching:
                raise DependencyError(
                    f"No compatible local package found for dependency {spec}. "
                    "Add its .tpk archive to a directory passed with --repo."
                )

            _, dependency_archive, dependency_manifest = matching[0]
            visit(dependency_archive, dependency_manifest)

        visiting.pop()
        planned[name] = {"archive": archive, "manifest": manifest}
        ordered.append((archive, manifest))

    visit(root_archive, root_manifest)
    return ordered
