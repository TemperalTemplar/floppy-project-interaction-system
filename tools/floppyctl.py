#!/usr/bin/env python3
"""Thin read-only CLI for registered Floppy records and validation."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

MANIFEST_PATH = Path(".floppy/manifest.json")
DEFAULT_VALIDATOR = Path(__file__).with_name("validate_floppy.py")


class CliError(ValueError):
    """Concise deterministic command failure."""


def _error(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 2


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CliError(f"{label} is missing: {path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CliError(f"{label} is unreadable: {path}") from exc
    if not isinstance(value, dict):
        raise CliError(f"{label} must contain a JSON object: {path}")
    return value


def _root_path(value: str | None) -> Path:
    root = Path(value or ".").expanduser().resolve()
    if not root.is_dir():
        raise CliError(f"repository root is not a directory: {root}")
    return root


def _none(value: Any) -> str:
    if value is None or value == "":
        return "NONE"
    return str(value)


def _registered_records(root: Path, manifest: dict[str, Any]) -> dict[str, Path]:
    records = manifest.get("records")
    if not isinstance(records, dict):
        raise CliError("manifest registered-record map is missing")

    result: dict[str, Path] = {}
    for name, relative in records.items():
        if not isinstance(name, str) or not name:
            raise CliError("manifest contains an invalid registered-record name")
        if not isinstance(relative, str) or not relative:
            raise CliError(f"registered record has no path: {name}")

        candidate = (root / relative).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise CliError(f"registered record escapes repository root: {name}") from exc
        result[name] = candidate
    return result


def command_status(root: Path) -> int:
    manifest = _read_json(root / MANIFEST_PATH, "control manifest")
    roadmap_config = manifest.get("roadmap")
    if not isinstance(roadmap_config, dict):
        raise CliError("manifest roadmap registration is missing")

    roadmap_relative = roadmap_config.get("machine_readable")
    if not isinstance(roadmap_relative, str) or not roadmap_relative:
        roadmap_relative = ".floppy/roadmap/roadmap.json"
    roadmap_path = (root / roadmap_relative).resolve()
    try:
        roadmap_path.relative_to(root)
    except ValueError as exc:
        raise CliError("registered roadmap escapes repository root") from exc
    roadmap = _read_json(roadmap_path, "registered roadmap")

    authority = manifest.get("authority")
    if not isinstance(authority, dict):
        raise CliError("manifest authority record is missing")

    active = manifest.get("active_work_authorization")
    if active is not None and not isinstance(active, dict):
        raise CliError("active authorization record is invalid")

    continuation = manifest.get("continuation_point")
    if not isinstance(continuation, dict):
        continuation = {}

    lifecycle = manifest.get("status", roadmap.get("lifecycle_state"))
    authority_state = authority.get(
        "implementation_authority",
        authority.get("authority_state"),
    )
    active_section = authority.get(
        "active_implementation_section",
        roadmap.get("active_implementation_section"),
    )
    current_section = authority.get(
        "current_authorized_section",
        roadmap.get("current_authorized_section"),
    )

    authorization_id = (
        active.get("authorization_id")
        if isinstance(active, dict)
        else continuation.get("active_work_authorization")
    )
    writer = (
        active.get("repository_writer")
        if isinstance(active, dict)
        else continuation.get("repository_writer")
    )

    print(f"lifecycle_state={_none(lifecycle)}")
    print(f"authority={_none(authority_state)}")
    print(f"active_implementation_section={_none(active_section)}")
    print(f"current_authorized_section={_none(current_section)}")
    print(f"active_authorization={_none(authorization_id)}")
    print(f"repository_writer={_none(writer)}")
    return 0


def command_validate(root: Path, mode: str | None) -> int:
    selected_mode = mode
    if selected_mode is None:
        selected_mode = "source" if (root / "system-manifest.json").is_file() else "project"
    if selected_mode not in {"source", "project"}:
        raise CliError(f"invalid validation mode: {selected_mode}")

    validator = DEFAULT_VALIDATOR.resolve()
    if not validator.is_file():
        raise CliError(f"existing validator is missing: {validator}")

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(validator),
            str(root),
            "--mode",
            selected_mode,
        ],
        cwd=root,
        env=env,
        check=False,
    )
    return result.returncode


def command_inspect(root: Path, selection: str) -> int:
    manifest = _read_json(root / MANIFEST_PATH, "control manifest")
    records = _registered_records(root, manifest)
    path = records.get(selection)
    if path is None:
        raise CliError(f"unknown registered record: {selection}")
    if not path.is_file():
        raise CliError(f"registered record is missing: {selection}")
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise CliError(f"registered record is unreadable: {selection}") from exc
    sys.stdout.write(content)
    if content and not content.endswith("\n"):
        sys.stdout.write("\n")
    return 0


def _parse(argv: list[str]) -> tuple[Path, str, list[str]]:
    root_value: str | None = None
    remaining: list[str] = []
    index = 0
    while index < len(argv):
        item = argv[index]
        if item == "--root":
            if root_value is not None:
                raise CliError("--root may be provided only once")
            if index + 1 >= len(argv):
                raise CliError("--root requires a path")
            root_value = argv[index + 1]
            index += 2
            continue
        remaining.append(item)
        index += 1

    if not remaining:
        raise CliError("command is required: status, validate, or inspect")
    command = remaining[0]
    if command not in {"status", "validate", "inspect"}:
        raise CliError(f"unknown command: {command}")
    return _root_path(root_value), command, remaining[1:]


def main(argv: list[str] | None = None) -> int:
    try:
        root, command, args = _parse(list(sys.argv[1:] if argv is None else argv))

        if command == "status":
            if args:
                raise CliError("status accepts no arguments")
            return command_status(root)

        if command == "inspect":
            if len(args) != 1:
                raise CliError("inspect requires exactly one registered record")
            return command_inspect(root, args[0])

        mode: str | None = None
        if args:
            if len(args) != 2 or args[0] != "--mode":
                raise CliError("validate accepts only --mode source|project")
            mode = args[1]
        return command_validate(root, mode)
    except CliError as exc:
        return _error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
