#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path.cwd()
SELF = Path(__file__).resolve()

STD = ROOT / "02-standards/_global/STD-GLB-004-event-driven.md"
SAD = ROOT / "04-system/scnehaux-ui-platform/scnehaux-ui-platform.sad.md"

BASE_COMMIT = "aef4b4ce41ae6d511e7055e3729f22ff793d08a9"
STD_REPO_PATH = "02-standards/_global/STD-GLB-004-event-driven.md"

def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Refusing patch {label}: expected exactly 1 occurrence, found {count}")
    return text.replace(old, new, 1)

def main():
    if not STD.exists() or not SAD.exists():
        raise SystemExit("Run this helper from the scnehaux-architecture repository root")

    # Restore the approved STD exactly to the known-good pre-ADR-rebaseline baseline.
    try:
        std_baseline = subprocess.check_output(
            ["git", "show", f"{BASE_COMMIT}:{STD_REPO_PATH}"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Unable to read STD baseline from {BASE_COMMIT}: {exc}")

    current_std = STD.read_text(encoding="utf-8")
    bad_marker = "The mechanism is the waiver register, not a decision record."
    if bad_marker not in current_std:
        raise SystemExit("Refusing STD restore: expected accidental waiver-register text is missing")

    STD.write_text(std_baseline, encoding="utf-8", newline="\n")
    print(f"RESTORED: {STD}")

    # Align SAD-003 with cross-repository local package consumption.
    sad = SAD.read_text(encoding="utf-8")

    guards = [
        "id: SAD-003",
        "version: 1.0.0",
        "status: approved",
        "consumed by downstream portals via pnpm workspace (local) or the private NPM registry (production)",
        "consumed by all frontend portals across the monorepo",
        "The platform packages are developed within the monorepo and integrated into downstream applications via workspace linkages, then published for production.",
    ]
    for marker in guards:
        if marker not in sad:
            raise SystemExit(f"Refusing SAD-003 patch: expected baseline marker missing: {marker!r}")

    sad = replace_once(sad, "version: 1.0.0", "version: 1.0.1", "version")
    sad = replace_once(sad, "last_reviewed: '2026-05-19'", "last_reviewed: '2026-08-25'", "last_reviewed")
    sad = replace_once(
        sad,
        "consumed by downstream portals via pnpm workspace (local) or the private NPM registry (production)",
        "consumed by downstream portals through a governed local-development package linkage (including pnpm workspace when co-located) or the private NPM registry for released/production consumption",
        "system context consumption",
    )
    sad = replace_once(
        sad,
        "consumed by all frontend portals across the monorepo",
        "consumed by downstream frontend portals across repository boundaries",
        "solution context repository scope",
    )
    sad = replace_once(
        sad,
        "The platform packages are developed within the monorepo and integrated into downstream applications via workspace linkages, then published for production.",
        "The UI Platform packages are developed in their governed package workspace. Downstream applications may consume them through explicit local-development linkage, including pnpm workspace when legitimately co-located, while released/production consumers use immutable versioned packages.",
        "deployment consumption",
    )

    # Correct an existing obvious PAD identifier typo while this approved SAD receives a patch bump.
    if "(PAD-PLT-002)" in sad and "parent_pad: PAD-PLT-003" in sad:
        sad = sad.replace("(PAD-PLT-002)", "(PAD-PLT-003)", 1)

    SAD.write_text(sad, encoding="utf-8", newline="\n")
    print(f"ALIGNED: {SAD}")
    print("SAD-003: 1.0.0 -> 1.0.1")
    print("")
    print("ADR-GLB-009 intentionally remains proposed.")
    print("")
    print("Run:")
    print("  make generate-docs")
    print("  git diff --check")
    print("  python -m pytest 06-fitness-function/tests -q")
    print("  git status")
    print("  git add -A")
    print("  git diff --cached --check")
    print('  git commit -m "align repository topology governance"')
    print("  git push origin main")

    try:
        if SELF.parent == ROOT and SELF.exists():
            SELF.unlink()
            print(f"Removed helper: {SELF.name}")
    except OSError as exc:
        print(f"WARN: helper self-delete failed: {exc}", file=sys.stderr)

if __name__ == "__main__":
    main()
