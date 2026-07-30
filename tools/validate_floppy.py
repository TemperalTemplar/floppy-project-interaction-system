#!/usr/bin/env python3
"""Validate either the Floppy source repository or an initialized project."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SOURCE_REQUIRED = [
    "VERSION",
    "README.md",
    "ABOUT.md",
    "BOOTSTRAP.md",
    "system-manifest.json",
    "orchestrator/Floppy_Z.md",
    "orchestrator/README.md",
    "onboarding/Floppy_1E.md",
    "onboarding/README.md",
    "protocols/00-source-repository-policy.md",
    "protocols/01-new-project-onboarding.md",
    "protocols/02-project-intake.md",
    "protocols/03-active-session.md",
    "protocols/04-everyday-closeout.md",
    "protocols/05-revision-application.md",
    "project-seed/.floppy/manifest.json",
    "project-seed/.floppy/roadmap/roadmap.json",
    "project-seed/.floppy/roadmap/roadmap.md",
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
    ".floppy/roadmap/roadmap.json",
    ".floppy/roadmap/roadmap.md",
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        if manifest:
            if manifest.get("entrypoints", {}).get("about") != "ABOUT.md":
                errors.append("system manifest does not register canonical ABOUT.md")
            architecture = manifest.get("architecture", {})
            if architecture.get("name") != "BCE — Bootable Context Environment":
                errors.append("system manifest does not identify the BCE architecture")
            if architecture.get("about_path") != "ABOUT.md":
                errors.append("system manifest BCE about path is invalid")

            orchestrator = manifest.get("orchestrator", {})
            orchestrator_path = orchestrator.get("canonical_path")
            if not orchestrator_path or not (root / orchestrator_path).is_file():
                errors.append("system manifest orchestrator path is missing")
            elif orchestrator.get("sha256") != sha256(root / orchestrator_path):
                errors.append("canonical Floppy Z digest does not match system manifest")

            builder = manifest.get("initial_project_roadmap_builder", {})
            builder_path = builder.get("canonical_path")
            if not builder_path or not (root / builder_path).is_file():
                errors.append("system manifest Floppy 1E path is missing")
            elif builder.get("sha256") != sha256(root / builder_path):
                errors.append("canonical Floppy 1E digest does not match system manifest")
            if builder.get("implementation_authority") is not False:
                errors.append("Floppy 1E must not grant implementation authority")
            if builder.get("mutable_during_project_work") is not False:
                errors.append("Floppy 1E must be immutable during project work")

    if args.mode == "project" and not errors:
        manifest = validate_json(root / ".floppy/manifest.json", errors)
        roadmap = validate_json(root / ".floppy/roadmap/roadmap.json", errors)
        if manifest:
            for relative in manifest.get("required_read_order", []):
                if not (root / relative).is_file():
                    errors.append(f"manifest read-order file missing: {relative}")
            system = manifest.get("system", {})
            if system.get("source_read_only_during_project_work") is not True:
                errors.append("project manifest does not enforce source read-only boundary")
            if system.get("about") != "ABOUT.md":
                errors.append("project manifest does not preserve canonical ABOUT provenance")
            if system.get("architecture") != "BCE — Bootable Context Environment":
                errors.append("project manifest does not identify the BCE architecture")
            floppies = manifest.get("floppies", {})
            if set(floppies) != {"A", "B", "C", "D", "E"}:
                errors.append("project manifest must map project Floppies A through E only")
            onboarding = manifest.get("onboarding", {})
            if onboarding.get("controller") != "onboarding/Floppy_1E.md":
                errors.append("project manifest does not reference canonical Floppy 1E")
            if onboarding.get("implementation_authority") is not False:
                errors.append("project manifest incorrectly grants Floppy 1E implementation authority")
            roadmap_paths = manifest.get("roadmap", {})
            for key in ("machine_readable", "user_readable"):
                relative = roadmap_paths.get(key)
                if not relative or not (root / relative).is_file():
                    errors.append(f"project roadmap path missing or invalid: {key}")
        if roadmap:
            if roadmap.get("current_authorized_section") is not None:
                errors.append("new project roadmap must not authorize a section during initialization")
            controller = roadmap.get("source_controller", {})
            if controller.get("mutable_in_project") is not False:
                errors.append("project roadmap must preserve canonical Floppy 1E as read-only")

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"VALIDATION PASSED: {args.mode} at {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
