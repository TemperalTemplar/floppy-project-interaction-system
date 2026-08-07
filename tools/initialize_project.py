#!/usr/bin/env python3
"""Provision a deterministic project-owned .floppy control-state directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

SYSTEM_VERSION_TOKEN = "0.4.1-dev"
TOKEN_PROJECT = "{{PROJECT_NAME}}"
TOKEN_SOURCE = "{{SOURCE_REPOSITORY}}"

STAGE_NAME = ".floppy-provision-stage"
DESTINATION_NAME = ".floppy"
INITIAL_STATE_ID = "LC-ONBOARDING-REQUIRED"
INITIAL_STATE_SCHEMA = "schemas/bce/1.0.0/bce-lifecycle-state.schema.json"
CANONICAL_JSON_PROFILE = "UTF-8/LF/canonical-json-v1"


class ProvisioningError(ValueError):
    """Raised when deterministic project provisioning cannot proceed safely."""


@dataclass(frozen=True)
class ProjectIdentity:
    repository: str
    branch: str | None
    worktree: str
    checkpoint: str | None


@dataclass(frozen=True)
class ProvisioningResult:
    target: Path
    destination: Path
    created_paths: tuple[str, ...]
    tree_sha256: str
    identity: ProjectIdentity
    dry_run: bool


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        required=True,
        type=Path,
        help="Existing project repository directory",
    )
    parser.add_argument(
        "--project-name",
        required=True,
        help="Human-readable project name",
    )
    parser.add_argument(
        "--source-repository",
        default="SOURCE-REPOSITORY-NOT-YET-RECORDED",
        help="Floppy source repository URL or owner/name",
    )
    parser.add_argument(
        "--project-repository",
        default=None,
        help="Project repository URL or owner/name; defaults to Git origin or LOCAL::<name>",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the exact plan without writing",
    )
    return parser.parse_args(argv)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_reparse_stat(metadata: os.stat_result) -> bool:
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(getattr(metadata, "st_file_attributes", 0) & flag)


def _check_no_reparse(path: Path, label: str) -> None:
    try:
        metadata = path.stat(follow_symlinks=False)
    except OSError as exc:
        raise ProvisioningError(f"cannot inspect {label}: {path}: {exc}") from exc
    if path.is_symlink() or _is_reparse_stat(metadata):
        raise ProvisioningError(f"{label} must not be a symlink or reparse point: {path}")


def _safe_existing_directory(path: Path, label: str) -> Path:
    expanded = path.expanduser()
    if not expanded.exists() or not expanded.is_dir():
        raise ProvisioningError(f"{label} must be an existing directory: {expanded}")
    resolved = expanded.resolve(strict=True)
    current = resolved
    while True:
        _check_no_reparse(current, label)
        if current.parent == current:
            break
        current = current.parent
    return resolved


def _safe_seed_files(seed: Path) -> list[Path]:
    _check_no_reparse(seed, "project seed")
    files: list[Path] = []
    for path in sorted(seed.rglob("*"), key=lambda item: item.relative_to(seed).as_posix()):
        _check_no_reparse(path, "project seed entry")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ProvisioningError(f"project seed entry is not a regular file: {path}")
        relative = path.relative_to(seed)
        if relative.is_absolute() or ".." in relative.parts:
            raise ProvisioningError(f"project seed path escapes the seed: {relative}")
        files.append(path)
    return files


def _git_read(target: Path, *arguments: str) -> str | None:
    try:
        completed = subprocess.run(
            [
                "git",
                "-c",
                f"safe.directory={target.as_posix()}",
                "-C",
                str(target),
                *arguments,
            ],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return value or None


def resolve_project_identity(target: Path, project_repository: str | None) -> ProjectIdentity:
    root = _git_read(target, "rev-parse", "--show-toplevel")
    if root is not None:
        git_root = Path(root).resolve(strict=True)
        if git_root != target:
            raise ProvisioningError(
                f"target must be the Git worktree root: expected {git_root}, found {target}"
            )
        branch = _git_read(target, "symbolic-ref", "--quiet", "--short", "HEAD")
        checkpoint = _git_read(target, "rev-parse", "--verify", "HEAD")
        if checkpoint is not None and not (
            len(checkpoint) == 40 and all(character in "0123456789abcdef" for character in checkpoint)
        ):
            raise ProvisioningError("Git returned a non-canonical HEAD checkpoint")
        origin = _git_read(target, "config", "--get", "remote.origin.url")
    else:
        branch = None
        checkpoint = None
        origin = None

    repository = (project_repository or origin or f"LOCAL::{target.name}").strip()
    if not repository:
        raise ProvisioningError("project repository identity cannot be blank")

    return ProjectIdentity(
        repository=repository,
        branch=branch,
        worktree=str(target),
        checkpoint=checkpoint,
    )


def render_text(
    source: Path,
    destination: Path,
    project_name: str,
    source_repo: str,
    system_version: str,
) -> None:
    text = source.read_text(encoding="utf-8")
    text = text.replace(TOKEN_PROJECT, project_name)
    text = text.replace(TOKEN_SOURCE, source_repo)
    text = text.replace(SYSTEM_VERSION_TOKEN, system_version)
    destination.write_text(text, encoding="utf-8", newline="\n")


def _initial_lifecycle_state(identity: ProjectIdentity) -> dict[str, Any]:
    return {
        "state_id": INITIAL_STATE_ID,
        "section": None,
        "authorization_id": None,
        "base_checkpoint": identity.checkpoint,
        "dimensions": {
            "roadmap": "ONBOARDING_REQUIRED",
            "work_package": "NOT_ACCEPTED",
            "authority": "NO_ACTIVE_WORK_AUTHORIZATION",
            "implementation": "NOT_STARTED",
            "verification": "NOT_STARTED",
            "acceptance": "PENDING",
            "closeout": "NOT_PROPOSED",
            "migration": "NONE",
            "final_closure": "OPEN",
        },
        "active_implementation_sections": [],
        "evidence": [
            "Deterministic project control state provisioned",
            "No implementation authority granted during initialization",
        ],
    }


def _update_control_records(
    dot_floppy: Path,
    *,
    project_name: str,
    source_repository: str,
    system_version: str,
    identity: ProjectIdentity,
) -> None:
    manifest_path = dot_floppy / "manifest.json"
    registry_path = dot_floppy / "orchestrator-registry.json"
    lifecycle_path = dot_floppy / "lifecycle-state.json"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["initialized_by"] = "tools/initialize_project.py"
    manifest["system"]["version"] = system_version
    manifest["system"]["source_repository"] = source_repository
    manifest["project_name"] = project_name
    manifest["control_state"] = {
        "provisioning_version": 1,
        "status": "PROVISIONED",
        "lifecycle_state": ".floppy/lifecycle-state.json",
        "lifecycle_state_schema": INITIAL_STATE_SCHEMA,
        "orchestrator_registry": ".floppy/orchestrator-registry.json",
        "repository": identity.repository,
        "branch": identity.branch,
        "worktree": identity.worktree,
        "checkpoint": identity.checkpoint,
        "serialization": CANONICAL_JSON_PROFILE,
        "implementation_authority": False,
    }
    manifest["records"] = {
        **(manifest.get("records") if isinstance(manifest.get("records"), dict) else {}),
        "lifecycle_state": ".floppy/lifecycle-state.json",
        "orchestrator_registry": ".floppy/orchestrator-registry.json",
    }

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["project_checkpoint"] = {
        "repository": identity.repository,
        "branch": identity.branch,
        "worktree": identity.worktree,
        "checkpoint": identity.checkpoint,
    }
    registry["provisioning"] = {
        "version": 1,
        "status": "PROVISIONED",
        "serialization": CANONICAL_JSON_PROFILE,
        "initialized_by": "tools/initialize_project.py",
    }

    lifecycle = _initial_lifecycle_state(identity)

    manifest_path.write_bytes(canonical_json_bytes(manifest))
    registry_path.write_bytes(canonical_json_bytes(registry))
    lifecycle_path.write_bytes(canonical_json_bytes(lifecycle))


def _validate_staged_control_state(
    dot_floppy: Path,
    *,
    project_name: str,
    identity: ProjectIdentity,
) -> None:
    manifest = json.loads((dot_floppy / "manifest.json").read_text(encoding="utf-8"))
    registry = json.loads((dot_floppy / "orchestrator-registry.json").read_text(encoding="utf-8"))
    lifecycle = json.loads((dot_floppy / "lifecycle-state.json").read_text(encoding="utf-8"))

    if manifest.get("project_name") != project_name:
        raise ProvisioningError("staged manifest project name mismatch")
    control = manifest.get("control_state")
    if not isinstance(control, dict) or control.get("status") != "PROVISIONED":
        raise ProvisioningError("staged manifest control-state record is invalid")
    expected_checkpoint = {
        "repository": identity.repository,
        "branch": identity.branch,
        "worktree": identity.worktree,
        "checkpoint": identity.checkpoint,
    }
    if registry.get("project_checkpoint") != expected_checkpoint:
        raise ProvisioningError("staged registry checkpoint does not match the project identity")
    if lifecycle != _initial_lifecycle_state(identity):
        raise ProvisioningError("staged lifecycle state is not the deterministic initial state")
    assignments = registry.get("current_assignments")
    if not isinstance(assignments, dict):
        raise ProvisioningError("staged registry assignments are missing")
    if assignments.get("repository_writer") is not None:
        raise ProvisioningError("initialization must not assign a repository writer")
    if assignments.get("writer_authorization_reference") is not None:
        raise ProvisioningError("initialization must not assign a writer authorization reference")

    for path in (dot_floppy / "manifest.json", dot_floppy / "orchestrator-registry.json", dot_floppy / "lifecycle-state.json"):
        parsed = json.loads(path.read_text(encoding="utf-8"))
        if path.read_bytes() != canonical_json_bytes(parsed):
            raise ProvisioningError(f"staged JSON is not canonically serialized: {path.name}")


def _tree_digest(dot_floppy: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(dot_floppy.rglob("*"), key=lambda item: item.relative_to(dot_floppy).as_posix()):
        if not path.is_file():
            continue
        relative = path.relative_to(dot_floppy).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def provision_project(
    *,
    target: Path,
    project_name: str,
    source_repository: str = "SOURCE-REPOSITORY-NOT-YET-RECORDED",
    project_repository: str | None = None,
    dry_run: bool = False,
    source_root: Path | None = None,
    hook: Callable[[str, dict[str, Any]], None] | None = None,
) -> ProvisioningResult:
    target_root = _safe_existing_directory(target, "target")
    source = (source_root or Path(__file__).resolve().parents[1]).resolve(strict=True)
    seed = source / "project-seed" / DESTINATION_NAME
    if not seed.is_dir():
        raise ProvisioningError(f"source seed is missing: {seed}")
    _check_no_reparse(source, "Floppy source repository")
    files = _safe_seed_files(seed)

    if target_root == source or source in target_root.parents:
        raise ProvisioningError("refusing to initialize inside the Floppy source repository")

    destination = target_root / DESTINATION_NAME
    stage_root = target_root / STAGE_NAME
    if destination.exists() or destination.is_symlink():
        raise ProvisioningError(f"destination already exists; no files were changed: {destination}")
    if stage_root.exists() or stage_root.is_symlink():
        raise ProvisioningError(f"staging path already exists; no files were changed: {stage_root}")

    name = project_name.strip()
    source_repo = source_repository.strip()
    if not name:
        raise ProvisioningError("project name cannot be blank")
    if not source_repo:
        raise ProvisioningError("source repository cannot be blank")

    system_version = (source / "VERSION").read_text(encoding="utf-8").strip()
    identity = resolve_project_identity(target_root, project_repository)
    created_paths = tuple(
        sorted(
            {path.relative_to(seed).as_posix() for path in files}
            | {"lifecycle-state.json"}
        )
    )

    if dry_run:
        return ProvisioningResult(
            target=target_root,
            destination=destination,
            created_paths=created_paths,
            tree_sha256="DRY-RUN",
            identity=identity,
            dry_run=True,
        )

    stage_dot_floppy = stage_root / DESTINATION_NAME
    replaced = False
    context = {
        "target": target_root,
        "destination": destination,
        "stage_root": stage_root,
        "identity": identity,
    }

    try:
        stage_dot_floppy.mkdir(parents=True, exist_ok=False)
        if hook is not None:
            hook("stage-created", context)

        for source_path in files:
            relative = source_path.relative_to(seed)
            destination_path = stage_dot_floppy / relative
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                render_text(
                    source_path,
                    destination_path,
                    name,
                    source_repo,
                    system_version,
                )
            except UnicodeDecodeError:
                shutil.copyfile(source_path, destination_path)

        _update_control_records(
            stage_dot_floppy,
            project_name=name,
            source_repository=source_repo,
            system_version=system_version,
            identity=identity,
        )
        _validate_staged_control_state(
            stage_dot_floppy,
            project_name=name,
            identity=identity,
        )
        if hook is not None:
            hook("staged-and-validated", context)

        os.replace(stage_dot_floppy, destination)
        replaced = True
        if hook is not None:
            hook("destination-replaced", context)

        _validate_staged_control_state(
            destination,
            project_name=name,
            identity=identity,
        )
        tree_sha256 = _tree_digest(destination)
    except Exception:
        if replaced and destination.exists():
            shutil.rmtree(destination, ignore_errors=True)
        shutil.rmtree(stage_root, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)

    return ProvisioningResult(
        target=target_root,
        destination=destination,
        created_paths=created_paths,
        tree_sha256=tree_sha256,
        identity=identity,
        dry_run=False,
    )


def print_result(result: ProvisioningResult, system_version: str) -> None:
    print(f"Floppy source version: {system_version}")
    print(f"Project target: {result.target}")
    print(f"Will create: {result.destination}")
    print(f"Files: {len(result.created_paths)}")
    for relative in result.created_paths:
        prefix = "PLAN" if result.dry_run else "CREATED"
        print(f"  {prefix} {result.destination / relative}")
    if result.dry_run:
        print("DRY RUN: no files changed")
    else:
        print(f"Control-state tree SHA-256: {result.tree_sha256}")
        print("Initialization complete.")
        print(
            "Next action: load canonical Floppy 1E and run new-project roadmap "
            "onboarding; project implementation is not yet authorized."
        )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_root = Path(__file__).resolve().parents[1]
    try:
        result = provision_project(
            target=args.target,
            project_name=args.project_name,
            source_repository=args.source_repository,
            project_repository=args.project_repository,
            dry_run=args.dry_run,
            source_root=source_root,
        )
    except ProvisioningError as exc:
        fail(str(exc))
    system_version = (source_root / "VERSION").read_text(encoding="utf-8").strip()
    print_result(result, system_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
