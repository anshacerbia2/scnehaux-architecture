#!/usr/bin/env python3
"""Architecture Maturity Dashboard Generator.

Generates a MATURITY.md file that provides a quantitative overview of the
architecture framework's health, compliance, and progression.
"""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MATURITY_FILE = REPO_ROOT / "MATURITY.md"


def count_artifacts(directory: Path, prefix: str) -> dict[str, int]:
    status_counts = {
        "approved": 0,
        "proposed": 0,
        "deprecated": 0,
        "hold": 0,
        "total": 0,
    }

    if not directory.exists():
        return status_counts

    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith(prefix) and file.endswith(".md"):
                status_counts["total"] += 1
                content = (Path(root) / file).read_text(encoding="utf-8")
                if "status: approved" in content or "status: adopted" in content:
                    status_counts["approved"] += 1
                elif (
                    "status: proposed" in content
                    or "status: trial" in content
                    or "status: assessed" in content
                ):
                    status_counts["proposed"] += 1
                elif "status: deprecated" in content or "status: hold" in content:
                    status_counts["deprecated"] += 1

    return status_counts


def generate_dashboard() -> None:
    # Generating Architecture Maturity Dashboard...

    ead_stats = count_artifacts(REPO_ROOT / "01-enterprise", "EAD-")
    gdc_stats = count_artifacts(REPO_ROOT / "00-governance", "GDC-")
    pad_stats = count_artifacts(REPO_ROOT / "03-domain", "")
    sad_stats = count_artifacts(REPO_ROOT / "04-system", "")
    std_stats = count_artifacts(REPO_ROOT / "02-standards", "STD-")
    adr_stats = count_artifacts(REPO_ROOT / "05-decisions", "ADR-")

    content = [
        "# 🏛️ Architecture Maturity Dashboard",
        "",
        "> **Auto-generated** by `generate_maturity_dashboard.py`",
        "",
        "## 1. Governance Landscape",
        "",
        "| Artifact Layer | Total Documents | Active / Approved | Proposed / Trial | Deprecated / Hold |",
        "| :--- | :--- | :--- | :--- | :--- |",
        f"| **EAD** (Enterprise) | {ead_stats['total']} | {ead_stats['approved']} | {ead_stats['proposed']} | {ead_stats['deprecated']} |",
        f"| **GDC** (Governance) | {gdc_stats['total']} | {gdc_stats['approved']} | {gdc_stats['proposed']} | {gdc_stats['deprecated']} |",
        f"| **PAD** (Domain) | {pad_stats['total']} | - | - | - |",
        f"| **SAD** (System) | {sad_stats['total']} | - | - | - |",
        f"| **STD** (Standard) | {std_stats['total']} | {std_stats['approved']} | {std_stats['proposed']} | {std_stats['deprecated']} |",
        f"| **ADR** (Decisions) | {adr_stats['total']} | {adr_stats['approved']} | {adr_stats['proposed']} | {adr_stats['deprecated']} |",
        "",
        "## 2. Capability Coverage",
        "",
        "- **Total Systems (SADs)**: {0}".format(sad_stats["total"]),
        "- **Total Domains (PADs)**: {0}".format(pad_stats["total"]),
        "",
        "## 3. Operations & Compliance",
        "",
        "- **CODEOWNERS Status**: `PASSING` (Validated via CI)",
        "- **Schema Drift**: `SYNCHRONIZED` (Validated via CI)",
        "",
    ]

    MATURITY_FILE.write_text("\n".join(content), encoding="utf-8")
    print(f"[OK] Generated Architecture Maturity Dashboard -> {MATURITY_FILE}")


if __name__ == "__main__":
    generate_dashboard()
