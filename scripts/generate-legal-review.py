#!/usr/bin/env python3
"""Create a compact Buildroot legal-info review bundle; this is not a legal opinion."""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from pathlib import Path

REQUIRED_COLUMNS = ("package", "version", "license", "license files", "source archive")
COPY_FILES = ("README", "manifest.csv", "host-manifest.csv", "buildroot.config", "legal-info.sha256")


def normalized(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).lower()


def read_manifest(path: Path, scope: str, legal_info: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError(f"{path.name}: missing CSV header")
        fields = {normalized(name): name for name in reader.fieldnames}
        missing = [name for name in REQUIRED_COLUMNS if name not in fields]
        if missing:
            raise ValueError(f"{path.name}: missing required columns: {', '.join(missing)}")

        source_root = legal_info / ("host-sources" if scope == "host" else "sources")
        rows: list[dict[str, str]] = []
        for raw in reader:
            row = {key: str(raw.get(original) or "").strip() for key, original in fields.items()}
            package = row["package"]
            if not package:
                continue
            license_name = row["license"]
            license_files = row["license files"]
            source_archive = row["source archive"]

            license_review = (
                "manual-identification-required"
                if normalized(license_name) in {"", "unknown", "n/a", "not defined"}
                else "declared-license-requires-human-review"
            )
            license_text_status = (
                "not-collected-or-not-declared"
                if normalized(license_files) in {"", "not saved", "unknown"}
                else "declared-in-manifest-check-bundle"
            )
            if normalized(source_archive) in {"", "not saved", "unknown"}:
                source_status = "not-saved-or-not-declared"
            else:
                basename = Path(source_archive).name
                matches = list(source_root.rglob(basename)) if source_root.exists() else []
                source_status = "present-in-legal-info" if matches else "archive-not-found-by-name"

            rows.append({
                "scope": scope,
                "package": package,
                "version": row["version"],
                "license": license_name,
                "license_files": license_files,
                "license_text_status": license_text_status,
                "source_archive": source_archive,
                "source_status": source_status,
                "license_review": license_review,
            })
        return rows


def write_components_csv(rows: list[dict[str, str]], output: Path) -> None:
    columns = [
        "scope", "package", "version", "license", "license_files",
        "license_text_status", "source_archive", "source_status", "license_review",
    ]
    with (output / "components.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict[str, str]]) -> str:
    lines = [
        "| Package | Version | Buildroot-declared license | License files (manifest) | Source archive status |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        def cell(value: str) -> str:
            return value.replace("|", r"\|").replace("\n", " ")
        lines.append(
            f"| {cell(row['package'])} | {cell(row['version'])} | "
            f"{cell(row['license'])} | {cell(row['license_files'])} | "
            f"{cell(row['source_status'])} |"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legal-info", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    legal_info = args.legal_info.resolve()
    output = args.output.resolve()

    for required in ("README", "manifest.csv", "host-manifest.csv", "buildroot.config"):
        if not (legal_info / required).is_file():
            raise SystemExit(f"Missing required legal-info evidence: {required}")

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    for name in COPY_FILES:
        source = legal_info / name
        if source.is_file():
            shutil.copy2(source, output / name)
    for directory in ("licenses", "host-licenses"):
        source = legal_info / directory
        if source.is_dir():
            shutil.copytree(source, output / directory)

    target_rows = read_manifest(legal_info / "manifest.csv", "target", legal_info)
    host_rows = read_manifest(legal_info / "host-manifest.csv", "host", legal_info)
    all_rows = target_rows + host_rows
    write_components_csv(all_rows, output)

    index_lines = []
    for scope, folder in (("target", "sources"), ("host", "host-sources")):
        source_root = legal_info / folder
        if source_root.exists():
            for path in sorted(source_root.rglob("*")):
                if path.is_file():
                    relative = path.relative_to(source_root).as_posix()
                    index_lines.append(f"{scope}/{relative}\t{path.stat().st_size} bytes")
    (output / "source-archive-index.txt").write_text(
        "\n".join(index_lines) + ("\n" if index_lines else ""), encoding="utf-8"
    )

    unknown = [r for r in all_rows if r["license_review"] == "manual-identification-required"]
    missing_sources = [r for r in all_rows if r["source_status"] != "present-in-legal-info"]
    missing_licenses = [r for r in all_rows if r["license_text_status"] == "not-collected-or-not-declared"]

    report = [
        "# TermOS 0.2.0 — Third-party notices and inventory",
        "",
        "> Generated from Buildroot legal-info metadata. Inventory and triage only; not a legal opinion or compliance certificate.",
        "",
        "## Scope",
        "",
        "- Target components: manifest.csv, as declared by Buildroot.",
        "- Host components: host-manifest.csv; build-time tools are not automatically part of the target image.",
        "- Collected license texts: licenses/ and host-licenses/.",
        "- Source archive index: source-archive-index.txt.",
        "",
        "## Automated triage",
        "",
        f"- Target package entries: {len(target_rows)}",
        f"- Host package entries: {len(host_rows)}",
        f"- Entries with unknown/empty declared license: {len(unknown)}",
        f"- Entries without a source archive located by manifest filename: {len(missing_sources)}",
        f"- Entries whose license-file field is empty/unknown/not saved: {len(missing_licenses)}",
        "",
        "These counts are review flags. A source archive not saved is not automatically a violation for every license; a saved archive does not prove that all corresponding-source requirements are met.",
        "",
        "## Target components",
        "",
        markdown_table(target_rows),
        "",
        "## Host components",
        "",
        markdown_table(host_rows),
        "",
        "## Required human review",
        "",
        "1. Compare each declared license with the actual upstream license text for the exact version.",
        "2. Determine obligations separately for target components and host-only build tools.",
        "3. For copyleft components, verify complete corresponding source, applicable Buildroot patches, configuration, and build/installation scripts as required by the specific license.",
        "4. Resolve every warning in the adjacent Buildroot README; inspect legal-info.sha256 when present.",
        "5. Do not use this generated table as legal certification. Buildroot warns that package metadata may be inaccurate or incomplete and requires human review.",
        "",
    ]
    (output / "THIRD_PARTY_NOTICES.md").write_text("\n".join(report), encoding="utf-8")
    summary = {
        "target_package_count": len(target_rows),
        "host_package_count": len(host_rows),
        "unknown_license_entries": len(unknown),
        "source_archive_not_found_entries": len(missing_sources),
        "license_file_field_missing_entries": len(missing_licenses),
        "human_review_required": True,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
