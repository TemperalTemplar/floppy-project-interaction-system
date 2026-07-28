#!/usr/bin/env python3
"""Validate either the Floppy source repository or an initialized project."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SOURCE_REQUIRED = [
    "VERSION",
    "README.md",
    "BOOTSTRAP.md",
    "system-manifest.json",
    "protocols/00-source-repository-policy.md",
    "protocols/01-new-project-onboarding.md",
    "protocols/02-project-intake.md",
    "protocols/03-active-session.md",
    "protocols/04-everyday-closeout.md",
    "protocols/05-revision-application.md",
    "project-seed/.floppy/manifest.json",
    "tools/initialize_project.py",
]

PROJECT_REQUIRED = [
    ".floppy/manifest.json",
    ".floppy/START-HERE.md",
    ".floppy/floppies/Floppy-A-HITL.md",
    ".floppy/floppies/Floppy-B-Development-Issues.md",
    ".floppy/floppies/Floppy-C-Project-Baseline.md",
    ".floppy/floppies/Floppy-D-Project-Map.md",
    ".floppy/floppies/Floppy-E-Current-Section.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--mode", choices=("source", "project"), required=True)
    return parser.parse_args()


def validate_json(path: Path, errors: list[str]) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return None


def main() -> int:
    args = parse_args()
    root = args.path.expanduser().resolve()
    errors: list[str] = []
    required = SOURCE_REQUIRED if args.mode == "source" else PROJECT_REQUIRED

    for relative in required:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    if args.mode == "source" and not errors:
        manifest = validate_json(root / "system-manifest.json", errors)
        version = (root / "VERSION").read_text(encoding="utf-8").strip()
        if manifest and manifest.get("system_version") != version:
            errors.append("VERSION and system-manifest.json disagree")

    if args.mode == "project" and not errors:
        manifest = validate_json(root / ".floppy/manifest.json", errors)
        if manifest:
            for relative in manifest.get("required_read_order", []):
                if not (root / relative).is_file():
                    errors.append(f"manifest read-order file missing: {relative}")
            if manifest.get("system", {}).get("source_read_only_during_project_work") is not True:
                errors.append("project manifest does not enforce source read-only boundary")
            floppies = manifest.get("floppies", {})
            if set(floppies) != {"A", "B", "C", "D", "E"}:
                errors.append("project manifest must map Floppies A through E")

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"VALIDATION PASSED: {args.mode} at {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
