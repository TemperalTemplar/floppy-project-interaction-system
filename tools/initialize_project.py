#!/usr/bin/env python3
"""Initialize a project-owned .floppy directory from this source seed."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

SYSTEM_VERSION = "0.2.0-dev"
TOKEN_PROJECT = "{{PROJECT_NAME}}"
TOKEN_SOURCE = "{{SOURCE_REPOSITORY}}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path, help="Existing project repository directory")
    parser.add_argument("--project-name", required=True, help="Human-readable project name")
    parser.add_argument("--source-repository", default="SOURCE-REPOSITORY-NOT-YET-RECORDED", help="Source repo URL or owner/name")
    parser.add_argument("--dry-run", action="store_true", help="Show planned actions without writing")
    return parser.parse_args()


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def render_text(source: Path, destination: Path, project_name: str, source_repo: str) -> None:
    text = source.read_text(encoding="utf-8")
    text = text.replace(TOKEN_PROJECT, project_name).replace(TOKEN_SOURCE, source_repo)
    destination.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    args = parse_args()
    target = args.target.expanduser().resolve()
    source_root = Path(__file__).resolve().parents[1]
    seed = source_root / "project-seed" / ".floppy"
    destination = target / ".floppy"

    if not target.exists() or not target.is_dir():
        fail(f"target must be an existing directory: {target}")
    if target == source_root or source_root in target.parents:
        fail("refusing to initialize inside the Floppy source repository")
    if not seed.is_dir():
        fail(f"source seed is missing: {seed}")
    if destination.exists():
        fail(f"destination already exists; no files were changed: {destination}")
    if not args.project_name.strip():
        fail("project name cannot be blank")

    files = sorted(p for p in seed.rglob("*") if p.is_file())
    print(f"Floppy source version: {SYSTEM_VERSION}")
    print(f"Project target: {target}")
    print(f"Will create: {destination}")
    print(f"Files: {len(files)}")

    if args.dry_run:
        for source in files:
            print(f"  CREATE {destination / source.relative_to(seed)}")
        print("DRY RUN: no files changed")
        return 0

    destination.mkdir(parents=False)
    try:
        for source in files:
            relative = source.relative_to(seed)
            dest = destination / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                render_text(source, dest, args.project_name.strip(), args.source_repository.strip())
            except UnicodeDecodeError:
                shutil.copy2(source, dest)

        manifest_path = destination / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["initialized_by"] = "tools/initialize_project.py"
        manifest["system"]["version"] = SYSTEM_VERSION
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise

    print("Initialization complete.")
    print("Next action: run the new-project onboarding protocol; project implementation is not yet authorized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
