import platform

import pytest

from tpm.package import build_package


@pytest.fixture
def workspace(tmp_path):
    """An isolated temporary workspace for one test."""
    return tmp_path


def _build_fixture(workspace, name, version, files, description):
    source = workspace / f"source-{name}-{version}"
    output = workspace / f"{name}-{version}.tpk"

    for relative, (text, mode) in files.items():
        target = source.joinpath(*relative.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        target.chmod(mode)

    build_package(
        source=source,
        output=output,
        name=name,
        version=version,
        architecture=platform.machine(),
        description=description,
    )
    return output


@pytest.fixture
def package(workspace):
    """A two-file package used by rollback tests."""
    return _build_fixture(
        workspace,
        "hello-termos",
        "1.0.0",
        {
            "usr/bin/hello-termos": (
                "#!/bin/sh\necho TPM pytest fixture\n", 0o755
            ),
            "usr/share/doc/hello-termos/README.txt": (
                "Temporary TPM rollback fixture.\n", 0o644
            ),
        },
        "Temporary TPM rollback test package",
    )


@pytest.fixture
def package_v1(workspace):
    return _build_fixture(
        workspace,
        "hello-upgrade",
        "1.0.0",
        {
            "usr/bin/hello-upgrade": (
                "#!/bin/sh\necho Version 1\n", 0o755
            ),
            "usr/share/doc/hello-upgrade/kept.txt": (
                "old documentation\n", 0o644
            ),
            "usr/share/doc/hello-upgrade/obsolete.txt": (
                "obsolete file\n", 0o644
            ),
        },
        "TPM upgrade integration test",
    )


@pytest.fixture
def package_v2(workspace):
    return _build_fixture(
        workspace,
        "hello-upgrade",
        "1.1.0",
        {
            "usr/bin/hello-upgrade": (
                "#!/bin/sh\necho Version 2\n", 0o755
            ),
            "usr/share/doc/hello-upgrade/kept.txt": (
                "updated documentation\n", 0o644
            ),
            "usr/share/doc/hello-upgrade/added.txt": (
                "new documentation\n", 0o644
            ),
        },
        "TPM upgrade integration test",
    )
