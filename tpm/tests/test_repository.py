import json
import tempfile
from pathlib import Path

from tpm.package import build_package
from tpm.repository import (
    RepositoryError, build_index, generate_keypair, load_index,
    search_packages, sign_index, verify_index_signature, verify_repository,
)


def create_package(repo, name, version, description):
    source = repo.parent / f"src-{name}-{version}"
    file_path = source / "usr" / "share" / name / "README.txt"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(f"{name} {version}\\n", encoding="utf-8")
    output = repo / f"{name}-{version}.tpk"
    build_package(source, output, name, version, "all", description)
    return output


def expect_rejection(call, label):
    try:
        call()
    except RepositoryError as exc:
        print(f"[PASS] {label}: {exc}")
        return
    raise AssertionError(f"Expected repository rejection: {label}")


def main():
    print("TPM STAGE 7 + 8: REPOSITORY INDEX AND ED25519 SECURITY")
    with tempfile.TemporaryDirectory(prefix="tpm-repo-test-") as temporary:
        work = Path(temporary)
        repo = work / "repo"
        repo.mkdir()
        create_package(repo, "libmath", "1.2.0", "Math support library")
        create_package(repo, "calculator", "1.0.0", "Command line calculator")

        index_path, index = build_index(repo, repository_name="TermOS Test Repository")
        loaded = load_index(index_path)
        assert len(loaded["packages"]) == 2
        print("[PASS] Repository index generated with package metadata, sizes and SHA-256")

        keys = work / "keys"
        keys.mkdir()
        private_key, public_key = keys / "repo-ed25519-private.pem", keys / "repo-ed25519-public.pem"
        generate_keypair(private_key, public_key)
        assert private_key.stat().st_mode & 0o777 == 0o600
        print("[PASS] Ed25519 key pair generated; private key permissions are 0600")

        sign_index(index_path, private_key)
        verify_index_signature(index_path, public_key)
        print("[PASS] Ed25519 detached signature verified")

        matches, report = search_packages(repo, "math", public_key=public_key)
        assert len(matches) == 1 and matches[0]["name"] == "libmath"
        assert report["archives_verified"] == 2
        print("[PASS] Search returned the matching package only after signature and archive verification")

        wrong_private, wrong_public = keys / "wrong-private.pem", keys / "wrong-public.pem"
        generate_keypair(wrong_private, wrong_public)
        expect_rejection(lambda: verify_repository(repo, public_key=wrong_public), "Wrong trusted key rejected")

        original_index = index_path.read_bytes()
        changed = json.loads(original_index.decode("utf-8"))
        changed["repository"]["name"] = "Attacker Repository"
        index_path.write_text(json.dumps(changed, indent=2), encoding="utf-8")
        expect_rejection(lambda: verify_repository(repo, public_key=public_key), "Modified repository index rejected")
        index_path.write_bytes(original_index)
        verify_repository(repo, public_key=public_key)
        print("[PASS] Restored signed index verifies again")

        package_path = repo / loaded["packages"][0]["filename"]
        original_package = package_path.read_bytes()
        altered = bytearray(original_package)
        altered[-1] = (altered[-1] + 1) % 256
        package_path.write_bytes(altered)
        expect_rejection(lambda: verify_repository(repo, public_key=public_key), "Package archive tampering detected by signed SHA-256")
        package_path.write_bytes(original_package)
        verify_repository(repo, public_key=public_key)
        print("[PASS] Restored package archive hash matches the signed index")

        unsigned = work / "unsigned"
        unsigned.mkdir()
        create_package(unsigned, "tinyapp", "1.0.0", "Unsigned test package")
        build_index(unsigned)
        expect_rejection(lambda: search_packages(unsigned, "tinyapp"), "Unsigned repository rejected by default")
        results, unsigned_report = search_packages(unsigned, "tinyapp", allow_unsigned=True)
        assert len(results) == 1 and unsigned_report["signature"].startswith("unsigned")
        print("[PASS] Unsigned repository accepted only with explicit --allow-unsigned")

    print("\nTPM REPOSITORY AND SIGNATURE TESTS PASSED")


def test_repository_index_and_ed25519_security():
    """Run repository index and signature integration checks under pytest."""
    main()


if __name__ == "__main__":
    main()
