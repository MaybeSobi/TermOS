import argparse
import json
import sys
from pathlib import Path

from .database import DatabaseError, initialize_root
from .dependencies import DependencyError
from .manager import install_with_dependencies
from .installer import InstallError, install_package, list_installed, verify_installed
from .package import PackageError, build_package, package_info
from .uninstaller import UninstallError, remove_package
from .upgrade import UpgradeError, upgrade_package
from .repository import RepositoryError, build_index, generate_keypair, sign_index, verify_repository, search_packages


def main():
    parser = argparse.ArgumentParser(
        prog="tpm",
        description="TermOS Package Manager",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build", help="Build a TPK package")
    build.add_argument("source", type=Path)
    build.add_argument("--name", required=True)
    build.add_argument("--version", required=True)
    build.add_argument("--arch", default="x86_64")
    build.add_argument("--description", default="")
    build.add_argument(
        "--depends", action="append", default=[], metavar="SPEC",
        help="Package dependency, e.g. libfoo>=1.2.0 (repeatable)",
    )
    build.add_argument("-o", "--output", type=Path, required=True)

    info = commands.add_parser("info", help="Inspect and verify a TPK package")
    info.add_argument("package", type=Path)

    init_root = commands.add_parser("init-root", help="Initialize a dedicated TPM sandbox")
    init_root.add_argument("--root", type=Path, required=True)

    install = commands.add_parser("install", help="Install a package into a TPM sandbox")
    install.add_argument("package", type=Path)
    install.add_argument("--root", type=Path, required=True)
    install.add_argument(
        "--repo", type=Path, action="append", default=[],
        help="Local directory containing dependency .tpk files (repeatable)",
    )

    listing = commands.add_parser("list", help="List installed packages")
    listing.add_argument("--root", type=Path, required=True)

    verify = commands.add_parser("verify", help="Verify installed package files")
    verify.add_argument("--root", type=Path, required=True)
    verify.add_argument("name", nargs="?", help="Optional package name")

    remove = commands.add_parser("remove", help="Remove an installed package")
    remove.add_argument("name", help="Installed package name")
    remove.add_argument("--root", type=Path, required=True)
    remove.add_argument(
        "--keep-modified",
        action="store_true",
        help="Keep modified files instead of deleting them",
    )

    upgrade = commands.add_parser("upgrade", help="Upgrade an installed package")
    upgrade.add_argument("package", type=Path, help="New .tpk package file")
    upgrade.add_argument("--root", type=Path, required=True)

    install.add_argument("--repo-key", type=Path, action="append", default=[], help="Trusted public key for each signed --repo directory (one key may be reused)")
    # TPM_STAGE7_8_REPOSITORY_PARSERS
    repo_parser = commands.add_parser("repo", help="Build and secure a local package repository")
    repo_actions = repo_parser.add_subparsers(dest="repo_action", required=True)

    repo_index = repo_actions.add_parser("index", help="Create or refresh repository.json")
    repo_index.add_argument("directory", type=Path, help="Directory containing .tpk archives")
    repo_index.add_argument("--name", default="TermOS", help="Repository display name")
    repo_index.add_argument("--output", type=Path, help="Index output path")

    repo_keygen = repo_actions.add_parser("keygen", help="Generate an Ed25519 repository key pair")
    repo_keygen.add_argument("--private-key", type=Path, required=True)
    repo_keygen.add_argument("--public-key", type=Path, required=True)
    repo_keygen.add_argument("--force", action="store_true", help="Replace existing key files")

    repo_sign = repo_actions.add_parser("sign", help="Sign a repository index with Ed25519")
    repo_sign.add_argument("index", type=Path)
    repo_sign.add_argument("--private-key", type=Path, required=True)
    repo_sign.add_argument("--signature", type=Path)

    repo_verify = repo_actions.add_parser("verify", help="Verify index signature and package hashes")
    repo_verify.add_argument("index", type=Path)
    repo_verify.add_argument("--public-key", type=Path)
    repo_verify.add_argument("--signature", type=Path)
    repo_verify.add_argument("--allow-unsigned", action="store_true")

    search_parser = commands.add_parser("search", help="Search packages in a verified local repository")
    search_parser.add_argument("query")
    search_parser.add_argument("--repo", type=Path, required=True)
    search_parser.add_argument("--index", default="repository.json")
    search_parser.add_argument("--public-key", type=Path)
    search_parser.add_argument("--signature", type=Path)
    search_parser.add_argument("--allow-unsigned", action="store_true")

    args = parser.parse_args()

    try:
        if args.command == "build":
            manifest = build_package(
                source=args.source,
                output=args.output,
                name=args.name,
                version=args.version,
                architecture=args.arch,
                description=args.description,
                depends=args.depends,
            )
            print(f"Package created: {args.output}")
            print(f"Files: {len(manifest['files'])}")

        elif args.command == "info":
            manifest = package_info(args.package)
            print(json.dumps(manifest, indent=2, ensure_ascii=False))
            print("\nPackage integrity: OK")

        elif args.command == "init-root":
            root = initialize_root(args.root)
            print(f"TPM sandbox initialized: {root}")

        elif args.command == "install":
            # TPM_STAGE7_8_VERIFY_DEPENDENCY_REPOS
            repo_paths = getattr(args, "repo", None) or []
            repo_keys = getattr(args, "repo_key", None) or []
            if repo_keys:
                if not repo_paths:
                    raise RepositoryError("--repo-key requires at least one --repo directory")
                if len(repo_keys) == 1:
                    repo_keys = repo_keys * len(repo_paths)
                elif len(repo_keys) != len(repo_paths):
                    raise RepositoryError("Provide one --repo-key per --repo, or one key to reuse")
                for repo_path, trusted_key in zip(repo_paths, repo_keys):
                    report = verify_repository(repo_path, public_key=trusted_key)
                    print(f"Verified dependency repository: {report['repository']} ({report['packages']} packages)")
            else:
                for repo_path in repo_paths:
                    if (Path(repo_path) / ("repository.json" + ".sig")).exists():
                        raise RepositoryError("Signed dependency repository requires --repo-key")
                    print(f"warning: unsigned dependency repository: {repo_path}", file=sys.stderr)

            result = install_with_dependencies(args.package, args.root, args.repo)
            manifest = result["manifest"]
            print(f"Installed: {manifest['name']} {manifest['version']}")
            print(f"Files installed: {len(manifest['files'])}")
            if result["dependencies_installed"]:
                print(f"Dependencies installed: {result['dependencies_installed']}")

        elif args.command == "list":
            packages = list_installed(args.root)
            if not packages:
                print("No packages installed.")
            else:
                for name, data in sorted(packages.items()):
                    print(
                        f"{name} {data['version']} "
                        f"[{data['architecture']}] - {len(data['files'])} files"
                    )

        elif args.command == "verify":
            count, problems = verify_installed(args.root, args.name)
            if problems:
                for problem in problems:
                    print(f"[FAIL] {problem}", file=sys.stderr)
                print(f"Verification failed: {len(problems)} problem(s)")
                return 1
            print(f"Verified {count} package(s): OK")

        elif args.command == "remove":
            result = remove_package(args.name, args.root, args.keep_modified)
            print(f"Removed package registration: {result['name']}")
            print(f"Files removed: {result['removed']}")
            if result["missing"]:
                print(f"Already missing: {len(result['missing'])} file(s)")
            if result["modified_kept"]:
                print(
                    f"Modified files kept: {len(result['modified_kept'])} "
                    "(now unmanaged by TPM)"
                )
                for path in result["modified_kept"]:
                    print(f"  kept: {path}")
            if result["cleanup_warning"]:
                print(f"warning: {result['cleanup_warning']}", file=sys.stderr)


        elif args.command == "upgrade":
            result = upgrade_package(args.package, args.root)
            print(
                f"Upgraded: {result['name']} "
                f"{result['old_version']} -> {result['new_version']}"
            )
            print(
                f"Files: {result['added']} added, "
                f"{result['updated']} updated, {result['removed']} removed"
            )


        # TPM_STAGE7_8_REPOSITORY_HANDLERS
        elif args.command == "repo":
            if args.repo_action == "index":
                destination, index_data = build_index(args.directory, args.output, args.name)
                print(f"Repository index created: {destination}")
                print(f"Packages indexed: {len(index_data['packages'])}")
            elif args.repo_action == "keygen":
                private_path, public_path = generate_keypair(args.private_key, args.public_key, args.force)
                print(f"Private key: {private_path} (keep this secret)")
                print(f"Public key:  {public_path} (trusted verification key)")
            elif args.repo_action == "sign":
                signature = sign_index(args.index, args.private_key, args.signature)
                print(f"Repository index signed: {signature}")
            elif args.repo_action == "verify":
                index_file = args.index.expanduser().resolve(strict=True)
                result = verify_repository(
                    index_file.parent, index_name=index_file, public_key=args.public_key,
                    signature_path=args.signature, allow_unsigned=args.allow_unsigned,
                )
                print(f"Repository: {result['repository']}")
                print(f"Packages: {result['packages']}")
                print(f"Package archives verified: {result['archives_verified']}")
                print(f"Signature: {result['signature']}")
        elif args.command == "search":
            matches, verification = search_packages(
                args.repo, args.query, index_name=args.index, public_key=args.public_key,
                signature_path=args.signature, allow_unsigned=args.allow_unsigned,
            )
            print(f"Repository: {verification['repository']} ({verification['signature']})")
            if not matches:
                print("No matching packages.")
            else:
                for item in matches:
                    print(f"{item['name']} {item['version']} [{item['architecture']}] - {item.get('description', '')}")
                    print(f"  archive: {item['filename']}  sha256: {item['sha256']}")

    except (
        PackageError,
        DatabaseError,
        InstallError,
        UninstallError,
        UpgradeError,
        DependencyError,
        OSError,
        ValueError,
    ) as exc:
        print(f"tpm: error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
