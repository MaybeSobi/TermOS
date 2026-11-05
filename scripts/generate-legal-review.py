#!/usr/bin/env python3
"""Create a compact, reviewable Buildroot legal-info evidence bundle.

This tool preserves Buildroot's declared metadata and performs conservative
availability checks. It does NOT decide whether a license obligation is met.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from pathlib import Path
from typing import Iterable


REQUIRED_COLUMNS = ("package", "version", "license", "license files", "source archive")
COPY_FILES = ("README", "manifest.csv", "host-manifest.csv", "buildroot.config", "legal-info.sha256")


def normalized(value: object) -> str:
    return re.sub(r"\\s+", " ", str(value or "").strip()).lower()


def read_manifest(path: Path, scope: str, legal_info: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError(f"{path.name}: missing CSV header")
        fields = {normalized(name): name for name in reader.fieldnames}
        missing = [name for name in REQUIRED_COLUMNS if name not in fields]
        if missing:
            raise ValueError(f"{path.name}: missing required columns: {', '.join(missing)}")

        rows: list[dict[str, str]] = []
        source_root = legal_info / ("host-sources" if scope == "host" else "sources")
        for raw in reader:
            row = {key: str(raw.get(original) or "").strip() for key, original in fields.items()}
            package = row["package"]
            if not package:
                continue
            version = row["version"]
            license_name = row["license"]
            license_files = row["license files"]
            source_archive = row["source archive"]

            if normalized(license_name) in {"", "unknown", "n/a", "not defined"}:
                license_review = "manual-identification-required"
            else:
                license_review = "declared-license-requires-human-review"

            if normalized(license_files) in {"", "not saved", "unknown"}:
                license_text_status = "not-collected-or-not-declared"
            else:
                license_text_status = "declared-in-manifest-check-bundle"

            if normalized(source_archive) in {"", "not saved", "unknown"}:
                source_status = "not-saved-or-not-declared"
            else:
                basename = Path(source_archive).name
                matches = list(source_root.rglob(basename)) if source_root.exists() else []
                source_status = "present-in-legal-info" if matches else "archive-not-found-by-name"

            rows.append({
                "scope": scope,
                "package": package,
                "version": version,
                "license": license_name,
                "license_files": license_files,
                "license_text_status": license_text_status,
                "source_archive": source_archive,
                "source_status": source_status,
                "license_review": license_review,
            })
        return rows


def csv_text(rows: list[dict[str, str]]) -> str:
    import io
    output = io.StringIO(newline="")
    columns = [
        "scope", "package", "version", "license", "license_files",
        "license_text_status", "source_archive", "source_status", "license_review",
    ]
    writer = csv.DictWriter(output, fieldnames=columns, lineterminator="\\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def markdown_table(rows: list[dict[str, str]]) -> str:
    lines = [
        "| Package | Version | Buildroot-declared license | License files (manifest) | Source archive status |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        def cell(value: str) -> str:
            return value.replace("|", r"\\|").replace("\\n", " ")
        lines.append(
            f"| {cell(row['package'])} | {cell(row['version'])} | "
            f"{cell(row['license'])} | {cell(row['license_files'])} | "
            f"{cell(row['source_status'])} |"
        )
    return "\\n".join(lines)


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
    (output / "components.csv").write_text(csv_text(all_rows), encoding="utf-8")
    (output / "source-archive-index.txt").write_text(
        "\\n".join(
            f"{scope}/{path.relative_to(legal_info / folder).as_posix()}\\t{path.stat().st_size} bytes"
            for scope, folder in (("target", "sources"), ("host", "host-sources"))
            for path in sorted((legal_info / folder).rglob("*")) if path.is_file()
        ) + "\\n",
        encoding="utf-8",
    )

    unknown = [row for row in all_rows if row["license_review"] == "manual-identification-required"]
    unsaved_sources = [row for row in all_rows if row["source_status"] != "present-in-legal-info"]
    missing_licenses = [row for row in all_rows if row["license_text_status"] == "not-collected-or-not-declared"]

    report = [
        "# TermOS 0.2.0 — Third-party notices and inventory",
        "",
        "> Generated from Buildroot legal-info metadata. This is an inventory and triage aid, not a legal opinion or compliance certificate.",
        "",
        "## Scope",
        "",
        "- Target components: `manifest.csv` (included in the generated image according to Buildroot's package metadata).",
        "- Host components: `host-manifest.csv` (build-time tools; not automatically part of the target image).",
        "- License texts: `licenses/` and `host-licenses/` as collected by Buildroot.",
        "- Source archive index: `source-archive-index.txt`.",
        "",
        "## Automated triage",
        "",
        f"- Target packages: {len(target_rows)}",
        f"- Host packages: {len(host_rows)}",
        f"- Entries with unknown/empty declared license: {len(unknown)}",
        f"- Entries without a source archive located by the manifest filename: {len(unsaved_sources)}",
        f"- Entries whose license-file field is empty/unknown/not saved: {len(missing_licenses)}",
        "",
        "These counts are flags for manual review. A missing source archive is not by itself a legal violation for every license, and a saved archive is not proof that all corresponding-source requirements are satisfied.",
        "",
        "## Target components",
        "",
        markdown_table(target_rows),
        "",
        "## Host components",
        "",
        markdown_table(host_rows),
        "",
        "## Review rules",
        "",
        "1. Compare every declared license with the actual upstream license text and the version used.",
        "2. Determine obligations separately for the target image and host-only build tools.",
        "3. For copyleft components, verify complete corresponding source, applicable Buildroot patches, configuration, and installation/build scripts as required by the specific license.",
        "4. Resolve every warning in the adjacent Buildroot `README`; inspect `.legal-info` hashes when present.",
        "5. Do not use this generated table as a legal certification. Buildroot explicitly documents that its package metadata may be inaccurate or incomplete and requires human review.",
        "",
    ]
    (output / "THIRD_PARTY_NOTICES.md").write_text("\\n".join(report), encoding="utf-8")

    summary = {
        "target_package_count": len(target_rows),
        "host_package_count": len(host_rows),
        "unknown_license_entries": len(unknown),
        "source_archive_not_found_entries": len(unsaved_sources),
        "license_file_field_missing_entries": len(missing_licenses),
        "human_review_required": True,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
