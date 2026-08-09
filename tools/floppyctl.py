#!/usr/bin/env python3
"""Thin read-only CLI for registered Floppy records and validation."""

from __future__ import annotations

import hashlib
import io
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

MANIFEST_PATH = Path(".floppy/manifest.json")
DEFAULT_VALIDATOR = Path(__file__).with_name("validate_floppy.py")

BOOT_PACKAGE_FORMAT = "floppy-validated-boot-package"
BOOT_PACKAGE_FORMAT_VERSION = 1
BOOT_PACKAGE_FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
BOOT_PACKAGE_EXTERNAL_ATTR = (stat.S_IFREG | 0o644) << 16
BOOT_PACKAGE_FILE_PATHS = (
    "ABOUT.md",
    "BOOTSTRAP.md",
    "README.md",
    "VERSION",
    "docs/Architecture.md",
    "docs/Migration-Notes.md",
    "docs/User-Guide.md",
    "docs/getting-started/ChatGPT.md",
    "docs/getting-started/DeepSeek.md",
    "docs/getting-started/Gemini.md",
    "docs/getting-started/Grok.md",
    "docs/getting-started/Other-AI.md",
    "docs/getting-started/README.md",
    "onboarding/Floppy_1E.md",
    "onboarding/README.md",
    "orchestrator/Floppy_Z.md",
    "orchestrator/README.md",
    "project-seed/.floppy/START-HERE.md",
    "project-seed/.floppy/evidence/README.md",
    "project-seed/.floppy/floppies/Floppy-A-HITL.md",
    "project-seed/.floppy/floppies/Floppy-B-Development-Issues.md",
    "project-seed/.floppy/floppies/Floppy-C-Project-Baseline.md",
    "project-seed/.floppy/floppies/Floppy-D-Project-Map.md",
    "project-seed/.floppy/floppies/Floppy-E-Current-Section.md",
    "project-seed/.floppy/handoffs/README.md",
    "project-seed/.floppy/lifecycle-state.json",
    "project-seed/.floppy/manifest.json",
    "project-seed/.floppy/orchestrator-registry.json",
    "project-seed/.floppy/revisions/README.md",
    "project-seed/.floppy/roadmap/roadmap.json",
    "project-seed/.floppy/roadmap/roadmap.md",
    "project-seed/.floppy/templates/orchestrator-handoff.md",
    "project-seed/.floppy/templates/revision-packet.md",
    "project-seed/.floppy/templates/session-handoff.md",
    "protocols/00-source-repository-policy.md",
    "protocols/01-new-project-onboarding.md",
    "protocols/02-project-intake.md",
    "protocols/03-active-session.md",
    "protocols/04-everyday-closeout.md",
    "protocols/05-revision-application.md",
    "schemas/bce/1.0.0/bce-lifecycle-state.schema.json",
    "schemas/bce/1.0.0/bce-lifecycle-transition.schema.json",
    "schemas/bce/1.0.0/bce-work-authorization.schema.json",
    "schemas/bce/1.1.0/bce-lifecycle-state.schema.json",
    "schemas/bce/1.2.0/bce-lifecycle-state.schema.json",
    "schemas/bce/2.0.0/bce-compatibility-profile.schema.json",
    "schemas/drafts/bce-lifecycle-state.schema.json",
    "schemas/drafts/bce-lifecycle-transition.schema.json",
    "schemas/drafts/bce-work-authorization.schema.json",
    "schemas/floppy-fields.md",
    "specs/lifecycle-state-model.md",
    "specs/lifecycle-transition-table.json",
    "specs/lifecycle-write-contract.json",
    "specs/v2-architecture-compatibility.md",
    "specs/v2-compatibility-profile.json",
    "system-manifest.json",
    "tools/floppyctl.py",
    "tools/initialize_project.py",
    "tools/validate_floppy.py",
)
BOOT_PACKAGE_EXCLUDED_EXACT = {
    ".git",
    ".gitignore",
}
BOOT_PACKAGE_EXCLUDED_PREFIXES = (
    ".git/",
    ".floppy/",
    "legacy/",
    "tests/",
)
BOOT_PACKAGE_EXCLUDED_PARTS = {
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".vscode",
    "__pycache__",
}


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


def _normalized_repository_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if (
        not normalized
        or pure.is_absolute()
        or any(part in {"", ".", ".."} for part in pure.parts)
    ):
        raise CliError(f"invalid repository-relative scan path: {value}")
    return pure.as_posix()


def _is_reparse_stat(value: os.stat_result) -> bool:
    attributes = getattr(value, "st_file_attributes", 0)
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def _assert_no_unsafe_component(root: Path, candidate: Path) -> None:
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise CliError("scan root escapes repository root") from exc

    current = root
    for part in relative.parts:
        current = current / part
        try:
            metadata = current.lstat()
        except OSError as exc:
            logical = _normalized_repository_path(
                current.relative_to(root).as_posix()
            )
            raise CliError(f"scan path is unreadable: {logical}") from exc
        if current.is_symlink() or _is_reparse_stat(metadata):
            logical = _normalized_repository_path(
                current.relative_to(root).as_posix()
            )
            raise CliError(f"unsafe scan link or reparse point: {logical}")


def _scan_root_path(repository_root: Path, value: str) -> tuple[Path, str]:
    if not value:
        raise CliError("scan requires a non-empty scan root")

    supplied = Path(value).expanduser()
    if supplied.is_absolute():
        candidate = supplied
    else:
        normalized = value.replace("\\", "/")
        pure = PurePosixPath(normalized)
        if pure.is_absolute() or any(part in {"", ".."} for part in pure.parts):
            raise CliError("scan root escapes repository root")
        candidate = repository_root.joinpath(
            *(part for part in pure.parts if part != ".")
        )

    candidate = Path(os.path.abspath(candidate))
    try:
        relative = candidate.relative_to(repository_root)
    except ValueError as exc:
        raise CliError("scan root escapes repository root") from exc

    _assert_no_unsafe_component(repository_root, candidate)

    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        logical = "." if not relative.parts else relative.as_posix()
        raise CliError(f"scan root is unreadable: {logical}") from exc

    try:
        resolved.relative_to(repository_root)
    except ValueError as exc:
        raise CliError("scan root escapes repository root") from exc

    if not resolved.is_dir():
        logical = "." if not relative.parts else relative.as_posix()
        raise CliError(f"scan root is not a directory: {logical}")

    logical_root = (
        "."
        if not relative.parts
        else _normalized_repository_path(relative.as_posix())
    )
    return resolved, logical_root


def _logical_scan_path(repository_root: Path, path: Path) -> str:
    try:
        relative = path.relative_to(repository_root)
    except ValueError as exc:
        raise CliError("scan traversal escaped repository root") from exc
    return _normalized_repository_path(relative.as_posix())


def _finalize_scan_entries(
    entries: list[dict[str, str]],
) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for entry in entries:
        path = _normalized_repository_path(entry.get("path", ""))
        kind = entry.get("type")
        if kind not in {"directory", "file"}:
            raise CliError(f"unsupported scan entry type: {path}")
        normalized.append({"path": path, "type": kind})

    normalized.sort(key=lambda item: (item["path"], item["type"]))

    counts: dict[str, int] = {}
    folded: dict[str, set[str]] = {}
    for entry in normalized:
        path = entry["path"]
        counts[path] = counts.get(path, 0) + 1
        folded.setdefault(path.casefold(), set()).add(path)

    duplicates = sorted(path for path, count in counts.items() if count > 1)
    if duplicates:
        raise CliError(f"duplicate logical scan path: {duplicates[0]}")

    collisions = sorted(
        sorted(values)
        for values in folded.values()
        if len(values) > 1
    )
    if collisions:
        raise CliError("scan path case collision: " + ", ".join(collisions[0]))

    return normalized


def scan_package_content(
    repository_root: Path,
    scan_root: Path,
    *,
    scandir: Any = os.scandir,
) -> list[dict[str, str]]:
    """Return a deterministic read-only inventory below ``scan_root``."""

    lexical_repository_root = Path(
        os.path.abspath(repository_root.expanduser())
    )
    lexical_scan_root = Path(os.path.abspath(scan_root.expanduser()))
    _assert_no_unsafe_component(
        lexical_repository_root,
        lexical_scan_root,
    )

    try:
        repository_root = lexical_repository_root.resolve(strict=True)
        scan_root = lexical_scan_root.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise CliError("scan root is unreadable") from exc
    try:
        scan_root.relative_to(repository_root)
    except ValueError as exc:
        raise CliError("scan root escapes repository root") from exc

    pending = [scan_root]
    inventory: list[dict[str, str]] = []
    while pending:
        directory = pending.pop()
        try:
            children = list(scandir(directory))
        except OSError as exc:
            logical = (
                "."
                if directory == repository_root
                else _logical_scan_path(repository_root, directory)
            )
            raise CliError(f"scan path is unreadable: {logical}") from exc

        next_directories: list[Path] = []
        for child in children:
            child_path = Path(child.path)
            logical = _logical_scan_path(repository_root, child_path)
            try:
                metadata = child.stat(follow_symlinks=False)
            except OSError as exc:
                raise CliError(f"scan path is unreadable: {logical}") from exc

            if child.is_symlink() or _is_reparse_stat(metadata):
                raise CliError(
                    f"unsafe scan link or reparse point: {logical}"
                )
            if stat.S_ISDIR(metadata.st_mode):
                inventory.append({"path": logical, "type": "directory"})
                next_directories.append(child_path)
            elif stat.S_ISREG(metadata.st_mode):
                inventory.append({"path": logical, "type": "file"})
            else:
                raise CliError(f"unsupported scan entry type: {logical}")

        pending.extend(
            sorted(
                next_directories,
                key=lambda item: _logical_scan_path(
                    repository_root,
                    item,
                ),
                reverse=True,
            )
        )

    return _finalize_scan_entries(inventory)


def command_scan(root: Path, value: str) -> int:
    scan_root, logical_root = _scan_root_path(root, value)
    payload = {
        "entries": scan_package_content(root, scan_root),
        "scan_root": logical_root,
    }
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0



def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _boot_package_filename(version: str, product_commit: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", version):
        raise CliError("VERSION is not safe for deterministic artifact naming")
    if not re.fullmatch(r"[0-9a-f]{40}", product_commit):
        raise CliError("product commit must be a lowercase 40-character Git SHA")
    return (
        f"floppy-source-{version}-{product_commit}-boot-package.zip"
    )


def _checksum_manifest_filename(version: str, product_commit: str) -> str:
    archive = _boot_package_filename(version, product_commit)
    return archive[:-4] + ".checksums.json"


def _git_read(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={root.as_posix()}",
            "-C",
            str(root),
            *arguments,
        ],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        diagnostic = result.stderr.strip() or result.stdout.strip()
        raise CliError(
            "Git read failed"
            + (f": {diagnostic}" if diagnostic else "")
        )
    return result.stdout.strip()


def _current_product_commit(root: Path) -> str:
    head = _git_read(root, "rev-parse", "HEAD")
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise CliError("unable to resolve a valid product commit")
    status = _git_read(
        root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if status:
        first = sorted(line for line in status.splitlines() if line)[0]
        raise CliError(f"repository is not clean: {first}")
    return head


def _is_known_excluded_package_path(path: str) -> bool:
    if path in BOOT_PACKAGE_EXCLUDED_EXACT:
        return True
    if any(path.startswith(prefix) for prefix in BOOT_PACKAGE_EXCLUDED_PREFIXES):
        return True
    pure = PurePosixPath(path)
    if any(part in BOOT_PACKAGE_EXCLUDED_PARTS for part in pure.parts):
        return True
    name = pure.name
    lower = name.lower()
    if lower.endswith((".pyc", ".pyo", ".swp", ".tmp", "~")):
        return True
    if lower.endswith(".zip") or lower.endswith(".checksums.json"):
        return True
    return False


def _is_inventory_parent(path: str) -> bool:
    prefix = path.rstrip("/") + "/"
    return any(item.startswith(prefix) for item in BOOT_PACKAGE_FILE_PATHS)


def _validate_explicit_package_inventory(root: Path) -> list[str]:
    if not BOOT_PACKAGE_FILE_PATHS:
        raise CliError("boot-package inventory is empty")

    normalized = [
        _normalized_repository_path(path)
        for path in BOOT_PACKAGE_FILE_PATHS
    ]
    if normalized != sorted(normalized):
        raise CliError("boot-package inventory is not deterministically sorted")
    _finalize_scan_entries(
        [{"path": path, "type": "file"} for path in normalized]
    )

    scanned = scan_package_content(root, root)
    unexpected: list[str] = []
    for entry in scanned:
        path = entry["path"]
        kind = entry["type"]
        if kind == "file":
            if path in BOOT_PACKAGE_FILE_PATHS:
                continue
            if _is_known_excluded_package_path(path):
                continue
            unexpected.append(path)
            continue
        if kind == "directory":
            if _is_inventory_parent(path):
                continue
            if _is_known_excluded_package_path(path + "/"):
                continue
            unexpected.append(path + "/")

    if unexpected:
        raise CliError(
            "unexpected package source content: " + sorted(unexpected)[0]
        )

    for path in BOOT_PACKAGE_FILE_PATHS:
        candidate = root.joinpath(*PurePosixPath(path).parts)
        _assert_no_unsafe_component(root, candidate)
        try:
            metadata = candidate.lstat()
        except OSError as exc:
            raise CliError(f"package source file is missing: {path}") from exc
        if candidate.is_symlink() or _is_reparse_stat(metadata):
            raise CliError(
                f"unsafe package source link or reparse point: {path}"
            )
        if not stat.S_ISREG(metadata.st_mode):
            raise CliError(f"package source is not a regular file: {path}")

    return normalized


def _package_entries(root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in _validate_explicit_package_inventory(root):
        data = root.joinpath(*PurePosixPath(path).parts).read_bytes()
        entries.append(
            {
                "path": path,
                "size": len(data),
                "sha256": _sha256_bytes(data),
                "_data": data,
            }
        )
    return entries


def _deterministic_zip_bytes(entries: list[dict[str, Any]]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(
        buffer,
        mode="w",
        compression=zipfile.ZIP_STORED,
        allowZip64=True,
        strict_timestamps=True,
    ) as archive:
        archive.comment = b""
        for entry in entries:
            info = zipfile.ZipInfo(
                filename=entry["path"],
                date_time=BOOT_PACKAGE_FIXED_TIMESTAMP,
            )
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.create_version = 20
            info.extract_version = 20
            info.flag_bits = 0
            info.internal_attr = 0
            info.external_attr = BOOT_PACKAGE_EXTERNAL_ATTR
            info.comment = b""
            info.extra = b""
            archive.writestr(info, entry["_data"])
    return buffer.getvalue()


def _manifest_bytes(
    *,
    version: str,
    product_commit: str,
    archive_filename: str,
    archive_bytes: bytes,
    entries: list[dict[str, Any]],
) -> bytes:
    payload = {
        "archive": {
            "filename": archive_filename,
            "sha256": _sha256_bytes(archive_bytes),
            "size": len(archive_bytes),
        },
        "entries": [
            {
                "path": entry["path"],
                "sha256": entry["sha256"],
                "size": entry["size"],
            }
            for entry in entries
        ],
        "format": BOOT_PACKAGE_FORMAT,
        "format_version": BOOT_PACKAGE_FORMAT_VERSION,
        "product_commit": product_commit,
        "source_version": version,
    }
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _write_or_reuse_exact(path: Path, expected: bytes) -> str:
    if path.exists():
        if not path.is_file():
            raise CliError(f"artifact collision is not a file: {path}")
        try:
            actual = path.read_bytes()
        except OSError as exc:
            raise CliError(f"artifact collision is unreadable: {path}") from exc
        if actual != expected:
            raise CliError(f"artifact collision differs: {path}")
        return "reused"
    try:
        with path.open("xb") as handle:
            handle.write(expected)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise CliError(f"artifact collision appeared: {path}") from exc
    except OSError as exc:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        raise CliError(f"unable to create artifact: {path}") from exc
    return "created"


def build_boot_package(root: Path, destination: Path) -> dict[str, Any]:
    destination = destination.expanduser().resolve()
    if not destination.is_dir():
        raise CliError(
            f"artifact destination is not a directory: {destination}"
        )

    version_path = root / "VERSION"
    try:
        version = version_path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as exc:
        raise CliError("VERSION is unreadable") from exc
    if not version:
        raise CliError("VERSION is empty")

    product_commit = _current_product_commit(root)
    archive_filename = _boot_package_filename(version, product_commit)
    manifest_filename = _checksum_manifest_filename(
        version,
        product_commit,
    )
    archive_path = destination / archive_filename
    manifest_path = destination / manifest_filename

    entries = _package_entries(root)
    archive_bytes = _deterministic_zip_bytes(entries)
    manifest_bytes = _manifest_bytes(
        version=version,
        product_commit=product_commit,
        archive_filename=archive_filename,
        archive_bytes=archive_bytes,
        entries=entries,
    )

    archive_preexisting = archive_path.exists()
    manifest_preexisting = manifest_path.exists()
    archive_state = _write_or_reuse_exact(archive_path, archive_bytes)
    try:
        manifest_state = _write_or_reuse_exact(
            manifest_path,
            manifest_bytes,
        )
    except Exception:
        if not archive_preexisting:
            try:
                archive_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise

    return {
        "archive": {
            "filename": archive_filename,
            "path": str(archive_path),
            "sha256": _sha256_bytes(archive_bytes),
            "size": len(archive_bytes),
            "state": archive_state,
        },
        "entries": len(entries),
        "manifest": {
            "filename": manifest_filename,
            "path": str(manifest_path),
            "sha256": _sha256_bytes(manifest_bytes),
            "size": len(manifest_bytes),
            "state": manifest_state,
        },
        "product_commit": product_commit,
        "source_version": version,
    }


def _validated_archive_path(name: Any) -> str:
    if not isinstance(name, str) or not name:
        raise CliError("archive entry name is invalid")
    if "\\" in name:
        raise CliError(f"archive entry uses backslashes: {name}")
    if ":" in name or any(ord(character) < 32 for character in name):
        raise CliError(f"archive entry contains unsafe characters: {name}")
    if PurePosixPath(name).is_absolute():
        raise CliError(f"archive entry is absolute: {name}")
    if PureWindowsPath(name).drive:
        raise CliError(f"archive entry has a drive prefix: {name}")
    pure = PurePosixPath(name)
    if any(part in {"", ".", ".."} for part in pure.parts):
        raise CliError(f"archive entry is unsafe: {name}")
    normalized = pure.as_posix()
    if normalized != name:
        raise CliError(f"archive entry is not normalized: {name}")
    return normalized


def _read_manifest(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise CliError(f"checksum manifest is unreadable: {path}") from exc
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CliError("checksum manifest is not UTF-8") from exc
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CliError("checksum manifest contains invalid JSON") from exc
    if not isinstance(value, dict):
        raise CliError("checksum manifest must contain a JSON object")
    canonical = (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    if raw != canonical:
        raise CliError("checksum manifest serialization is not deterministic")
    required = {
        "archive",
        "entries",
        "format",
        "format_version",
        "product_commit",
        "source_version",
    }
    if set(value) != required:
        raise CliError("checksum manifest fields are invalid")
    if value.get("format") != BOOT_PACKAGE_FORMAT:
        raise CliError("checksum manifest format is invalid")
    if value.get("format_version") != BOOT_PACKAGE_FORMAT_VERSION:
        raise CliError("checksum manifest version is invalid")
    return value


def verify_boot_package(
    archive_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    archive_path = archive_path.expanduser().resolve()
    manifest_path = manifest_path.expanduser().resolve()
    if archive_path.parent != manifest_path.parent:
        raise CliError("archive and checksum manifest are not adjacent")
    if not archive_path.is_file():
        raise CliError(f"archive is missing: {archive_path}")
    if not manifest_path.is_file():
        raise CliError(f"checksum manifest is missing: {manifest_path}")

    manifest = _read_manifest(manifest_path)
    version = manifest.get("source_version")
    product_commit = manifest.get("product_commit")
    if not isinstance(version, str):
        raise CliError("checksum manifest source version is invalid")
    if not isinstance(product_commit, str):
        raise CliError("checksum manifest product commit is invalid")
    expected_archive_name = _boot_package_filename(
        version,
        product_commit,
    )
    expected_manifest_name = _checksum_manifest_filename(
        version,
        product_commit,
    )
    if archive_path.name != expected_archive_name:
        raise CliError("archive filename does not match manifest identity")
    if manifest_path.name != expected_manifest_name:
        raise CliError("checksum manifest filename is invalid")

    archive_record = manifest.get("archive")
    if not isinstance(archive_record, dict):
        raise CliError("checksum manifest archive record is invalid")
    if set(archive_record) != {"filename", "sha256", "size"}:
        raise CliError("checksum manifest archive fields are invalid")
    if archive_record.get("filename") != archive_path.name:
        raise CliError("checksum manifest archive filename mismatch")

    try:
        archive_bytes = archive_path.read_bytes()
    except OSError as exc:
        raise CliError(f"archive is unreadable: {archive_path}") from exc
    if archive_record.get("size") != len(archive_bytes):
        raise CliError("archive size mismatch")
    if archive_record.get("sha256") != _sha256_bytes(archive_bytes):
        raise CliError("archive SHA-256 mismatch")

    manifest_entries = manifest.get("entries")
    if not isinstance(manifest_entries, list) or not manifest_entries:
        raise CliError("checksum manifest entry inventory is invalid")

    expected: dict[str, dict[str, Any]] = {}
    folded: dict[str, str] = {}
    last_path: str | None = None
    for item in manifest_entries:
        if not isinstance(item, dict):
            raise CliError("checksum manifest entry is invalid")
        if set(item) != {"path", "sha256", "size"}:
            raise CliError("checksum manifest entry fields are invalid")
        path = _validated_archive_path(item.get("path"))
        if last_path is not None and path <= last_path:
            raise CliError("checksum manifest entry ordering is invalid")
        last_path = path
        if path in expected:
            raise CliError(f"duplicate manifest entry: {path}")
        collision = folded.get(path.casefold())
        if collision is not None and collision != path:
            raise CliError(
                f"manifest entry case collision: {collision}, {path}"
            )
        folded[path.casefold()] = path
        size = item.get("size")
        digest = item.get("sha256")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise CliError(f"manifest entry size is invalid: {path}")
        if not isinstance(digest, str) or not re.fullmatch(
            r"[0-9a-f]{64}",
            digest,
        ):
            raise CliError(f"manifest entry SHA-256 is invalid: {path}")
        expected[path] = item

    if list(expected) != list(BOOT_PACKAGE_FILE_PATHS):
        raise CliError(
            "checksum manifest inventory does not match the explicit package profile"
        )

    with zipfile.ZipFile(io.BytesIO(archive_bytes), "r") as archive:
        if archive.comment != b"":
            raise CliError("archive comment is not deterministic")
        actual: dict[str, zipfile.ZipInfo] = {}
        folded_actual: dict[str, str] = {}
        for info in archive.infolist():
            path = _validated_archive_path(info.filename)
            if path.endswith("/") or info.is_dir():
                raise CliError(f"archive contains a directory entry: {path}")
            if path in actual:
                raise CliError(f"duplicate archive entry: {path}")
            collision = folded_actual.get(path.casefold())
            if collision is not None and collision != path:
                raise CliError(
                    f"archive entry case collision: {collision}, {path}"
                )
            folded_actual[path.casefold()] = path
            actual[path] = info

            if info.date_time != BOOT_PACKAGE_FIXED_TIMESTAMP:
                raise CliError(f"archive timestamp mismatch: {path}")
            if info.compress_type != zipfile.ZIP_STORED:
                raise CliError(f"archive compression mismatch: {path}")
            if info.create_system != 3:
                raise CliError(f"archive platform metadata mismatch: {path}")
            if info.external_attr != BOOT_PACKAGE_EXTERNAL_ATTR:
                raise CliError(f"archive permission metadata mismatch: {path}")
            if info.comment != b"" or info.extra != b"":
                raise CliError(f"archive variable metadata present: {path}")
            if info.flag_bits != 0:
                raise CliError(f"archive flag metadata mismatch: {path}")

        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        if missing:
            raise CliError(f"archive member is missing: {missing[0]}")
        if extra:
            raise CliError(f"archive member is unexpected: {extra[0]}")
        if list(actual) != list(expected):
            raise CliError("archive entry ordering is invalid")

        for path, record in expected.items():
            info = actual[path]
            if info.file_size != record["size"]:
                raise CliError(f"archive member size mismatch: {path}")
            data = archive.read(info)
            if len(data) != record["size"]:
                raise CliError(f"archive member size mismatch: {path}")
            if _sha256_bytes(data) != record["sha256"]:
                raise CliError(f"archive member SHA-256 mismatch: {path}")

    return {
        "archive": str(archive_path),
        "entries": len(expected),
        "manifest": str(manifest_path),
        "product_commit": product_commit,
        "source_version": version,
        "verified": True,
    }


def command_package(root: Path, destination: str) -> int:
    payload = build_boot_package(root, Path(destination))
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


def command_verify_package(
    archive_path: str,
    manifest_path: str,
) -> int:
    payload = verify_boot_package(
        Path(archive_path),
        Path(manifest_path),
    )
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0



# === FS-13 PORTABLE CONTEXT EXPORT BEGIN ===
CONTEXT_EXPORT_FORMAT = "floppy-context-export"
CONTEXT_EXPORT_FORMAT_VERSION = 1
CONTEXT_EXPORT_REQUIRED_PATHS = {
    ".floppy/manifest.json",
    ".floppy/lifecycle-state.json",
}

def _context_export_filename(context_commit: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", context_commit):
        raise CliError("context commit must be a lowercase 40-character Git SHA")
    return f"floppy-context-{context_commit}-export.zip"

def _context_integrity_filename(context_commit: str) -> str:
    return _context_export_filename(context_commit)[:-4] + ".integrity.json"

def _git_nul_paths(root: Path, *arguments: str) -> list[str]:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root), *arguments],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        diagnostic = result.stderr.decode("utf-8", "replace").strip()
        raise CliError("Git read failed" + (f": {diagnostic}" if diagnostic else ""))
    try:
        values = result.stdout.decode("utf-8").split("\0")
    except UnicodeDecodeError as exc:
        raise CliError("Git path inventory is not UTF-8") from exc
    return [value for value in values if value]

def _context_identity(
    manifest_bytes: bytes,
    lifecycle_bytes: bytes,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    try:
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        lifecycle = json.loads(lifecycle_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CliError("exported canonical identity records are invalid") from exc
    if not isinstance(manifest, dict) or not isinstance(lifecycle, dict):
        raise CliError("exported canonical identity records must be JSON objects")
    name = manifest.get("project_name")
    if not isinstance(name, str) or not name:
        raise CliError("project manifest project_name is missing")
    control = manifest.get("control_state")
    control = control if isinstance(control, dict) else {}
    system = manifest.get("system")
    system = system if isinstance(system, dict) else {}
    project_repository = control.get("repository")
    source_repository = system.get("source_repository")
    source_version = system.get("version")
    for label, value in (
        ("project repository", project_repository),
        ("source repository", source_repository),
        ("source system version", source_version),
    ):
        if value is not None and not isinstance(value, str):
            raise CliError(f"project manifest {label} is invalid")
    state_id = lifecycle.get("state_id")
    if not isinstance(state_id, str) or not state_id:
        raise CliError("lifecycle state identifier is missing")
    return (
        {"name": name, "repository": project_repository},
        {"repository": source_repository, "system_version": source_version},
        state_id,
    )

def _assert_exportable_project(root: Path) -> dict[str, Any]:
    manifest = _read_json(root / MANIFEST_PATH, "control manifest")
    bce = manifest.get("bce_instance")
    policy = manifest.get("clean_source_integration_policy")
    if (
        isinstance(bce, dict)
        and bce.get("self_hosted_control_state") is True
        and isinstance(policy, dict)
        and policy.get("include_root_control_state_in_cross_project_bce_exports") is False
    ):
        raise CliError("source-development root control state is not exportable")
    return manifest

def _context_entries(
    root: Path,
) -> tuple[str, list[dict[str, Any]], dict[str, Any], dict[str, Any], str]:
    _assert_exportable_project(root)
    context_commit = _current_product_commit(root)
    context_root = root / ".floppy"
    if not context_root.is_dir():
        raise CliError("project control-state directory is missing: .floppy")
    scanned = scan_package_content(root, context_root)
    actual_files = sorted(
        entry["path"] for entry in scanned if entry["type"] == "file"
    )
    tracked = sorted(
        _normalized_repository_path(path)
        for path in _git_nul_paths(root, "ls-files", "-z", "--", ".floppy")
    )
    if not tracked:
        raise CliError("no tracked .floppy context files were found")
    if any(not path.startswith(".floppy/") for path in tracked):
        raise CliError("tracked context inventory escaped .floppy")
    if actual_files != tracked:
        unexpected = sorted(set(actual_files) - set(tracked))
        missing = sorted(set(tracked) - set(actual_files))
        if unexpected:
            raise CliError(f"untracked or ignored context content: {unexpected[0]}")
        raise CliError(f"tracked context file is missing: {missing[0]}")
    missing_required = sorted(CONTEXT_EXPORT_REQUIRED_PATHS - set(tracked))
    if missing_required:
        raise CliError(f"required context file is missing: {missing_required[0]}")
    entries: list[dict[str, Any]] = []
    data_by_path: dict[str, bytes] = {}
    for path in tracked:
        candidate = root.joinpath(*PurePosixPath(path).parts)
        _assert_no_unsafe_component(root, candidate)
        try:
            metadata = candidate.lstat()
        except OSError as exc:
            raise CliError(f"context file is unreadable: {path}") from exc
        if candidate.is_symlink() or _is_reparse_stat(metadata):
            raise CliError(f"unsafe context link or reparse point: {path}")
        if not stat.S_ISREG(metadata.st_mode):
            raise CliError(f"context path is not a regular file: {path}")
        data = candidate.read_bytes()
        data_by_path[path] = data
        entries.append(
            {
                "path": path,
                "size": len(data),
                "sha256": _sha256_bytes(data),
                "_data": data,
            }
        )
    project, source, lifecycle_state = _context_identity(
        data_by_path[".floppy/manifest.json"],
        data_by_path[".floppy/lifecycle-state.json"],
    )
    if _current_product_commit(root) != context_commit:
        raise CliError("repository checkpoint changed while export was prepared")
    return context_commit, entries, project, source, lifecycle_state

def _context_manifest_bytes(
    *,
    context_commit: str,
    archive_filename: str,
    archive_bytes: bytes,
    entries: list[dict[str, Any]],
    project: dict[str, Any],
    source: dict[str, Any],
    lifecycle_state: str,
) -> bytes:
    payload = {
        "archive": {
            "filename": archive_filename,
            "sha256": _sha256_bytes(archive_bytes),
            "size": len(archive_bytes),
        },
        "context_commit": context_commit,
        "entries": [
            {
                "path": entry["path"],
                "sha256": entry["sha256"],
                "size": entry["size"],
            }
            for entry in entries
        ],
        "format": CONTEXT_EXPORT_FORMAT,
        "format_version": CONTEXT_EXPORT_FORMAT_VERSION,
        "lifecycle_state": lifecycle_state,
        "project": project,
        "source": source,
    }
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")

def build_context_export(root: Path, destination: Path) -> dict[str, Any]:
    destination = destination.expanduser().resolve()
    if not destination.is_dir():
        raise CliError(f"artifact destination is not a directory: {destination}")
    (
        context_commit,
        entries,
        project,
        source,
        lifecycle_state,
    ) = _context_entries(root)
    archive_filename = _context_export_filename(context_commit)
    manifest_filename = _context_integrity_filename(context_commit)
    archive_bytes = _deterministic_zip_bytes(entries)
    manifest_bytes = _context_manifest_bytes(
        context_commit=context_commit,
        archive_filename=archive_filename,
        archive_bytes=archive_bytes,
        entries=entries,
        project=project,
        source=source,
        lifecycle_state=lifecycle_state,
    )
    archive_path = destination / archive_filename
    manifest_path = destination / manifest_filename
    archive_preexisting = archive_path.exists()
    archive_state = _write_or_reuse_exact(archive_path, archive_bytes)
    try:
        manifest_state = _write_or_reuse_exact(manifest_path, manifest_bytes)
    except Exception:
        if not archive_preexisting:
            try:
                archive_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise
    return {
        "archive": {
            "filename": archive_filename,
            "path": str(archive_path),
            "sha256": _sha256_bytes(archive_bytes),
            "size": len(archive_bytes),
            "state": archive_state,
        },
        "context_commit": context_commit,
        "entries": len(entries),
        "lifecycle_state": lifecycle_state,
        "manifest": {
            "filename": manifest_filename,
            "path": str(manifest_path),
            "sha256": _sha256_bytes(manifest_bytes),
            "size": len(manifest_bytes),
            "state": manifest_state,
        },
        "project": project,
        "source": source,
    }

def _read_context_integrity(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise CliError(f"integrity manifest is unreadable: {path}") from exc
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CliError("integrity manifest contains invalid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise CliError("integrity manifest must contain a JSON object")
    canonical = (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    if raw != canonical:
        raise CliError("integrity manifest serialization is not deterministic")
    required = {
        "archive",
        "context_commit",
        "entries",
        "format",
        "format_version",
        "lifecycle_state",
        "project",
        "source",
    }
    if set(value) != required:
        raise CliError("integrity manifest fields are invalid")
    if value.get("format") != CONTEXT_EXPORT_FORMAT:
        raise CliError("integrity manifest format is invalid")
    if value.get("format_version") != CONTEXT_EXPORT_FORMAT_VERSION:
        raise CliError("integrity manifest version is invalid")
    return value

def verify_context_export(
    archive_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    archive_path = archive_path.expanduser().resolve()
    manifest_path = manifest_path.expanduser().resolve()
    if archive_path.parent != manifest_path.parent:
        raise CliError("archive and integrity manifest are not adjacent")
    if not archive_path.is_file():
        raise CliError(f"archive is missing: {archive_path}")
    if not manifest_path.is_file():
        raise CliError(f"integrity manifest is missing: {manifest_path}")
    manifest = _read_context_integrity(manifest_path)
    commit = manifest.get("context_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise CliError("integrity manifest context commit is invalid")
    if archive_path.name != _context_export_filename(commit):
        raise CliError("archive filename does not match context identity")
    if manifest_path.name != _context_integrity_filename(commit):
        raise CliError("integrity manifest filename does not match context identity")
    archive_record = manifest.get("archive")
    if (
        not isinstance(archive_record, dict)
        or set(archive_record) != {"filename", "sha256", "size"}
    ):
        raise CliError("integrity archive record is invalid")
    if archive_record.get("filename") != archive_path.name:
        raise CliError("integrity archive filename mismatch")
    try:
        archive_bytes = archive_path.read_bytes()
    except OSError as exc:
        raise CliError(f"archive is unreadable: {archive_path}") from exc
    if archive_record.get("size") != len(archive_bytes):
        raise CliError("archive size mismatch")
    if archive_record.get("sha256") != _sha256_bytes(archive_bytes):
        raise CliError("archive SHA-256 mismatch")
    items = manifest.get("entries")
    if not isinstance(items, list) or not items:
        raise CliError("integrity entry inventory is invalid")
    expected: dict[str, dict[str, Any]] = {}
    folded: dict[str, str] = {}
    last: str | None = None
    for item in items:
        if not isinstance(item, dict) or set(item) != {"path", "sha256", "size"}:
            raise CliError("integrity entry is invalid")
        path = _validated_archive_path(item.get("path"))
        if not path.startswith(".floppy/"):
            raise CliError(f"integrity entry escapes .floppy: {path}")
        if last is not None and path <= last:
            raise CliError("integrity entry ordering is invalid")
        last = path
        if path in expected:
            raise CliError(f"duplicate integrity entry: {path}")
        collision = folded.get(path.casefold())
        if collision is not None and collision != path:
            raise CliError(
                f"integrity entry case collision: {collision}, {path}"
            )
        folded[path.casefold()] = path
        size = item.get("size")
        digest = item.get("sha256")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise CliError(f"integrity entry size is invalid: {path}")
        if not isinstance(digest, str) or not re.fullmatch(
            r"[0-9a-f]{64}", digest
        ):
            raise CliError(f"integrity entry SHA-256 is invalid: {path}")
        expected[path] = item
    missing_required = sorted(CONTEXT_EXPORT_REQUIRED_PATHS - set(expected))
    if missing_required:
        raise CliError(
            f"required context member is missing: {missing_required[0]}"
        )
    data_by_path: dict[str, bytes] = {}
    with zipfile.ZipFile(io.BytesIO(archive_bytes), "r") as archive:
        if archive.comment != b"":
            raise CliError("archive comment is not deterministic")
        actual: dict[str, zipfile.ZipInfo] = {}
        folded_actual: dict[str, str] = {}
        for info in archive.infolist():
            path = _validated_archive_path(info.filename)
            if path.endswith("/") or info.is_dir():
                raise CliError(f"archive contains a directory entry: {path}")
            if not path.startswith(".floppy/"):
                raise CliError(f"archive entry escapes .floppy: {path}")
            if path in actual:
                raise CliError(f"duplicate archive entry: {path}")
            collision = folded_actual.get(path.casefold())
            if collision is not None and collision != path:
                raise CliError(
                    f"archive entry case collision: {collision}, {path}"
                )
            folded_actual[path.casefold()] = path
            actual[path] = info
            if info.date_time != BOOT_PACKAGE_FIXED_TIMESTAMP:
                raise CliError(f"archive timestamp mismatch: {path}")
            if info.compress_type != zipfile.ZIP_STORED:
                raise CliError(f"archive compression mismatch: {path}")
            if info.create_system != 3:
                raise CliError(f"archive platform metadata mismatch: {path}")
            if info.external_attr != BOOT_PACKAGE_EXTERNAL_ATTR:
                raise CliError(f"archive permission metadata mismatch: {path}")
            if info.comment != b"" or info.extra != b"":
                raise CliError(f"archive variable metadata present: {path}")
            if info.flag_bits != 0:
                raise CliError(f"archive flag metadata mismatch: {path}")
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        if missing:
            raise CliError(f"archive member is missing: {missing[0]}")
        if extra:
            raise CliError(f"archive member is unexpected: {extra[0]}")
        if list(actual) != list(expected):
            raise CliError("archive entry ordering is invalid")
        for path, record in expected.items():
            info = actual[path]
            data = archive.read(info)
            if info.file_size != record["size"] or len(data) != record["size"]:
                raise CliError(f"archive member size mismatch: {path}")
            if _sha256_bytes(data) != record["sha256"]:
                raise CliError(f"archive member SHA-256 mismatch: {path}")
            data_by_path[path] = data
    project, source, lifecycle_state = _context_identity(
        data_by_path[".floppy/manifest.json"],
        data_by_path[".floppy/lifecycle-state.json"],
    )
    if manifest.get("project") != project:
        raise CliError("integrity project identity mismatch")
    if manifest.get("source") != source:
        raise CliError("integrity source identity mismatch")
    if manifest.get("lifecycle_state") != lifecycle_state:
        raise CliError("integrity lifecycle-state mismatch")
    return {
        "archive": str(archive_path),
        "context_commit": commit,
        "entries": len(expected),
        "lifecycle_state": lifecycle_state,
        "manifest": str(manifest_path),
        "project": project,
        "source": source,
        "verified": True,
    }

def command_export(root: Path, destination: str) -> int:
    payload = build_context_export(root, Path(destination))
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0

def command_verify_export(
    archive_path: str,
    manifest_path: str,
) -> int:
    payload = verify_context_export(Path(archive_path), Path(manifest_path))
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0
# === FS-13 PORTABLE CONTEXT EXPORT END ===

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



def _load_initializer_module():
    path = Path(__file__).with_name("initialize_project.py")
    spec = importlib.util.spec_from_file_location("floppy_initialize_project", path)
    if spec is None or spec.loader is None:
        raise CliError("unable to load deterministic project initializer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise CliError(f"unable to load deterministic project initializer: {exc}") from exc
    return module


def _parse_initialize_args(args: list[str]) -> dict[str, Any]:
    values: dict[str, Any] = {
        "target": None,
        "project_name": None,
        "source_repository": "SOURCE-REPOSITORY-NOT-YET-RECORDED",
        "project_repository": None,
        "dry_run": False,
    }
    index = 0
    while index < len(args):
        item = args[index]
        if item == "--dry-run":
            if values["dry_run"]:
                raise CliError("initialize --dry-run may be provided only once")
            values["dry_run"] = True
            index += 1
            continue
        option_map = {
            "--target": "target",
            "--project-name": "project_name",
            "--source-repository": "source_repository",
            "--project-repository": "project_repository",
        }
        key = option_map.get(item)
        if key is None:
            raise CliError(
                "initialize accepts --target, --project-name, "
                "--source-repository, --project-repository, and --dry-run"
            )
        if index + 1 >= len(args):
            raise CliError(f"initialize {item} requires a value")
        if values[key] is not None and key not in {"source_repository"}:
            raise CliError(f"initialize {item} may be provided only once")
        values[key] = args[index + 1]
        index += 2

    if values["target"] is None:
        raise CliError("initialize requires --target")
    if values["project_name"] is None:
        raise CliError("initialize requires --project-name")
    return values


def command_initialize(args: list[str]) -> int:
    values = _parse_initialize_args(args)
    module = _load_initializer_module()
    try:
        result = module.provision_project(
            target=Path(values["target"]),
            project_name=values["project_name"],
            source_repository=values["source_repository"],
            project_repository=values["project_repository"],
            dry_run=values["dry_run"],
            source_root=Path(__file__).resolve().parents[1],
        )
    except module.ProvisioningError as exc:
        raise CliError(str(exc)) from exc
    system_version = (
        Path(__file__).resolve().parents[1] / "VERSION"
    ).read_text(encoding="utf-8").strip()
    module.print_result(result, system_version)
    return 0


def command_onboarding(root: Path) -> int:
    """Print the registered V2-02 user-onboarding contract without mutation."""
    manifest = _read_json(root / "system-manifest.json", "system manifest")
    registry = manifest.get("user_onboarding")
    if not isinstance(registry, dict):
        raise CliError("system manifest user-onboarding registry is missing")
    print(json.dumps(registry, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
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
        raise CliError("command is required: status, validate, inspect, or initialize")
    command = remaining[0]
    if command not in {"status", "validate", "inspect", "scan", "package", "verify-package", "export", "verify-export", "onboarding", "initialize"}:
        raise CliError(f"unknown command: {command}")
    return _root_path(root_value), command, remaining[1:]


def _legacy_main(argv: list[str] | None = None) -> int:
    try:
        root, command, args = _parse(list(sys.argv[1:] if argv is None else argv))

        if command == "status":
            if args:
                raise CliError("status accepts no arguments")
            return command_status(root)

        if command == "onboarding":
            if args:
                raise CliError("onboarding accepts no arguments")
            return command_onboarding(root)

        if command == "inspect":
            if len(args) != 1:
                raise CliError("inspect requires exactly one registered record")
            return command_inspect(root, args[0])

        if command == "scan":
            if len(args) != 1:
                raise CliError("scan requires exactly one scan root")
            return command_scan(root, args[0])

        if command == "package":
            if len(args) != 1:
                raise CliError(
                    "package requires exactly one destination directory"
                )
            return command_package(root, args[0])

        if command == "verify-package":
            if len(args) != 2:
                raise CliError(
                    "verify-package requires one ZIP and one checksum manifest"
                )
            return command_verify_package(args[0], args[1])

        if command == "export":
            if len(args) != 1:
                raise CliError("export requires exactly one destination directory")
            return command_export(root, args[0])

        if command == "verify-export":
            if len(args) != 2:
                raise CliError("verify-export requires one ZIP and one integrity manifest")
            return command_verify_export(args[0], args[1])

        if command == "initialize":
            return command_initialize(args)

        mode: str | None = None
        if args:
            if len(args) != 2 or args[0] != "--mode":
                raise CliError("validate accepts only --mode source|project")
            mode = args[1]
        return command_validate(root, mode)
    except CliError as exc:
        return _error(str(exc))


# === FS-09 CONTROLLED LIFECYCLE WRITES BEGIN ===
import argparse as _fs09_argparse
import hashlib as _fs09_hashlib
import inspect as _fs09_inspect
import json as _fs09_json
import os as _fs09_os
import re as _fs09_re
import stat as _fs09_stat
import subprocess as _fs09_subprocess
from pathlib import Path as _FS09Path
from typing import Any as _FS09Any

_FS09_TRANSITION = "TR-004-START-SECTION-IMPLEMENTATION"
_FS09_SOURCE_STATE = "LC-SECTION-AUTHORIZED-NOT-STARTED"
_FS09_DESTINATION_STATE = "LC-SECTION-IMPLEMENTATION-IN-PROGRESS"
_FS09_TARGET = ".floppy/lifecycle-state.json"
_FS09_CONTRACT = "specs/lifecycle-write-contract.json"
_FS09_STATE_SCHEMA = "schemas/bce/1.0.0/bce-lifecycle-state.schema.json"
_FS09_AUTH_SCHEMA = "schemas/bce/1.0.0/bce-work-authorization.schema.json"
_FS09_TEST_HOOK = None


def _fs09_fail(message: str) -> None:
    raise CliError(message)


def _fs09_sha256(data: bytes) -> str:
    return _fs09_hashlib.sha256(data).hexdigest()


def _fs09_canonical_json(value: _FS09Any) -> bytes:
    return (
        _fs09_json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _fs09_load_json_bytes(data: bytes, label: str) -> _FS09Any:
    if data.startswith(b"\xef\xbb\xbf"):
        _fs09_fail(f"{label} must not contain a UTF-8 byte-order mark")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        _fs09_fail(f"{label} is not valid UTF-8: {exc}")
    try:
        return _fs09_json.loads(text)
    except Exception as exc:
        _fs09_fail(f"{label} is not valid JSON: {exc}")


def _fs09_read_json(path: _FS09Path, label: str) -> tuple[_FS09Any, bytes]:
    try:
        data = path.read_bytes()
    except OSError as exc:
        _fs09_fail(f"cannot read {label}: {exc}")
    return _fs09_load_json_bytes(data, label), data


def _fs09_source_root() -> _FS09Path:
    return _FS09Path(__file__).resolve().parents[1]


def _fs09_resolve_ref(schema: dict[str, _FS09Any], ref: str) -> _FS09Any:
    if not ref.startswith("#/"):
        _fs09_fail(f"unsupported JSON Schema reference: {ref}")
    value: _FS09Any = schema
    for raw in ref[2:].split("/"):
        key = raw.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, dict) or key not in value:
            _fs09_fail(f"unresolved JSON Schema reference: {ref}")
        value = value[key]
    return value


def _fs09_type_matches(value: _FS09Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return False


def _fs09_validate_schema(
    value: _FS09Any,
    node: _FS09Any,
    root_schema: dict[str, _FS09Any],
    location: str = "$",
) -> None:
    if not isinstance(node, dict):
        _fs09_fail(f"invalid schema node at {location}")
    if "$ref" in node:
        ref_node = _fs09_resolve_ref(root_schema, node["$ref"])
        _fs09_validate_schema(value, ref_node, root_schema, location)
        return
    if "allOf" in node:
        for child in node["allOf"]:
            _fs09_validate_schema(value, child, root_schema, location)
    if "anyOf" in node:
        failures: list[str] = []
        for child in node["anyOf"]:
            try:
                _fs09_validate_schema(value, child, root_schema, location)
                break
            except CliError as exc:
                failures.append(str(exc))
        else:
            _fs09_fail(f"{location} does not match any permitted schema")
    if "oneOf" in node:
        matches = 0
        for child in node["oneOf"]:
            try:
                _fs09_validate_schema(value, child, root_schema, location)
                matches += 1
            except CliError:
                pass
        if matches != 1:
            _fs09_fail(f"{location} must match exactly one schema")
    if "const" in node and value != node["const"]:
        _fs09_fail(f"{location} must equal {node['const']!r}")
    if "enum" in node and value not in node["enum"]:
        _fs09_fail(f"{location} contains a value outside the accepted enumeration")
    expected_type = node.get("type")
    if expected_type is not None:
        accepted = [expected_type] if isinstance(expected_type, str) else list(expected_type)
        if not any(_fs09_type_matches(value, item) for item in accepted):
            _fs09_fail(f"{location} has the wrong JSON type")
    if isinstance(value, str):
        if "minLength" in node and len(value) < int(node["minLength"]):
            _fs09_fail(f"{location} is shorter than the accepted minimum")
        if "maxLength" in node and len(value) > int(node["maxLength"]):
            _fs09_fail(f"{location} exceeds the accepted maximum")
        if "pattern" in node and _fs09_re.search(str(node["pattern"]), value) is None:
            _fs09_fail(f"{location} does not match the accepted pattern")
    if isinstance(value, list):
        if "minItems" in node and len(value) < int(node["minItems"]):
            _fs09_fail(f"{location} contains too few items")
        if "maxItems" in node and len(value) > int(node["maxItems"]):
            _fs09_fail(f"{location} contains too many items")
        if node.get("uniqueItems"):
            serialized = [_fs09_json.dumps(item, sort_keys=True) for item in value]
            if len(serialized) != len(set(serialized)):
                _fs09_fail(f"{location} contains duplicate items")
        item_schema = node.get("items")
        if item_schema is not None:
            for index, item in enumerate(value):
                _fs09_validate_schema(item, item_schema, root_schema, f"{location}[{index}]")
    if isinstance(value, dict):
        required = node.get("required", [])
        for key in required:
            if key not in value:
                _fs09_fail(f"{location}.{key} is required")
        properties = node.get("properties", {})
        if isinstance(properties, dict):
            for key, child in properties.items():
                if key in value:
                    _fs09_validate_schema(value[key], child, root_schema, f"{location}.{key}")
        if node.get("additionalProperties") is False:
            extras = sorted(set(value) - set(properties))
            if extras:
                _fs09_fail(f"{location} contains unsupported properties: {', '.join(extras)}")


def _fs09_load_contract_and_schemas() -> tuple[dict[str, _FS09Any], str, dict[str, _FS09Any], dict[str, _FS09Any]]:
    source = _fs09_source_root()
    contract, _ = _fs09_read_json(source / _FS09_CONTRACT, "FS-09 lifecycle-write contract")
    state_schema, _ = _fs09_read_json(source / _FS09_STATE_SCHEMA, "FS-02 lifecycle-state schema")
    auth_schema, _ = _fs09_read_json(source / _FS09_AUTH_SCHEMA, "FS-02 work-authorization schema")
    try:
        committed_contract_bytes = subprocess.run(
            [
                "git",
                "-c",
                f"safe.directory={source.as_posix()}",
                "-C",
                str(source),
                "show",
                "HEAD:specs/lifecycle-write-contract.json",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        _fs09_fail(
            f"FS-09 committed lifecycle-write contract blob is unavailable: {exc}"
        )
    committed_contract = _fs09_load_json_bytes(
        committed_contract_bytes,
        "FS-09 committed lifecycle-write contract",
    )
    if committed_contract != contract:
        _fs09_fail(
            "FS-09 checked-out lifecycle-write contract content diverges "
            "from committed content"
        )
    if not isinstance(contract, dict):
        _fs09_fail("FS-09 lifecycle-write contract root must be an object")
    if contract.get("status") != "ACCEPTED_NORMATIVE":
        _fs09_fail("FS-09 lifecycle-write contract is not accepted and normative")
    if contract.get("supported_transitions", [{}])[0].get("transition_id") != _FS09_TRANSITION:
        _fs09_fail("FS-09 lifecycle-write contract does not define the accepted transition")
    if not isinstance(state_schema, dict) or not isinstance(auth_schema, dict):
        _fs09_fail("FS-02 schemas must be JSON objects")
    if committed_contract_bytes != _fs09_canonical_json(committed_contract):
        _fs09_fail("FS-09 lifecycle-write contract serialization is not deterministic")
    return contract, _fs09_sha256(committed_contract_bytes), state_schema, auth_schema


def _fs09_git(root: _FS09Path, *arguments: str, check: bool = True) -> str:
    command = [
        "git",
        "-c",
        f"safe.directory={root}",
        "-C",
        str(root),
        *arguments,
    ]
    result = _fs09_subprocess.run(
        command,
        stdout=_fs09_subprocess.PIPE,
        stderr=_fs09_subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).decode("utf-8", errors="replace").strip()
        _fs09_fail(f"Git command failed ({' '.join(arguments)}): {detail or result.returncode}")
    return result.stdout.decode("utf-8", errors="replace").strip()


def _fs09_normalized_path(path: _FS09Path) -> str:
    return _fs09_os.path.normcase(_fs09_os.path.abspath(_fs09_os.fspath(path)))


def _fs09_same_path(left: _FS09Path, right: _FS09Path) -> bool:
    try:
        return _fs09_os.path.samefile(left, right)
    except OSError:
        return _fs09_normalized_path(left) == _fs09_normalized_path(right)


def _fs09_check_reparse(path: _FS09Path, label: str) -> None:
    try:
        info = path.lstat()
    except OSError as exc:
        _fs09_fail(f"cannot inspect {label}: {exc}")
    if _fs09_stat.S_ISLNK(info.st_mode):
        _fs09_fail(f"{label} must not be a symbolic link")
    attributes = getattr(info, "st_file_attributes", 0)
    reparse_flag = getattr(_fs09_stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    if attributes & reparse_flag:
        _fs09_fail(f"{label} must not be a junction or reparse point")


def _fs09_safe_target(root: _FS09Path) -> _FS09Path:
    if not root.is_absolute():
        _fs09_fail("target project root must be absolute")
    try:
        resolved_root = root.resolve(strict=True)
    except OSError as exc:
        _fs09_fail(f"target project root does not exist: {exc}")
    _fs09_check_reparse(resolved_root, "target project root")
    dot_floppy = resolved_root / ".floppy"
    target = dot_floppy / "lifecycle-state.json"
    if not dot_floppy.is_dir():
        _fs09_fail("target project .floppy directory is missing")
    _fs09_check_reparse(dot_floppy, "target project .floppy directory")
    if not target.exists():
        _fs09_fail("canonical lifecycle-state file is missing; file creation is not supported")
    _fs09_check_reparse(target, "canonical lifecycle-state file")
    if not target.is_file():
        _fs09_fail("canonical lifecycle-state target is not a regular file")
    matches = [
        child.name
        for child in dot_floppy.iterdir()
        if child.name.casefold() == "lifecycle-state.json".casefold()
    ]
    if matches != ["lifecycle-state.json"]:
        _fs09_fail("Windows case-colliding lifecycle-state paths are prohibited")
    try:
        target.resolve(strict=True).relative_to(resolved_root)
    except (OSError, ValueError):
        _fs09_fail("canonical lifecycle-state path escapes the target project")
    return target


def _fs09_project_identity(manifest: dict[str, _FS09Any], root: _FS09Path) -> tuple[str, str]:
    repository = manifest.get("repository") or manifest.get("source_repository")
    system = manifest.get("system")
    if not repository and isinstance(system, dict):
        repository = system.get("source_repository")
    source_version = manifest.get("source_version")
    if not source_version and isinstance(system, dict):
        source_version = system.get("source_version")
    version_path = root / "VERSION"
    if not source_version and version_path.is_file():
        source_version = version_path.read_text(encoding="utf-8").strip()
    if not isinstance(repository, str) or not repository:
        _fs09_fail("target project identity is missing from .floppy/manifest.json")
    if not isinstance(source_version, str) or not source_version:
        _fs09_fail("target project source version is missing")
    return repository, source_version


def _fs09_hook(name: str, context: dict[str, _FS09Any]) -> None:
    hook = globals().get("_FS09_TEST_HOOK")
    if callable(hook):
        hook(name, context)


def _fs09_prepare(
    root: _FS09Path,
    *,
    transition: str,
    authorization_reference: str,
    repository_writer: str,
    expected_branch: str,
    expected_head: str,
) -> dict[str, _FS09Any]:
    if transition != _FS09_TRANSITION:
        _fs09_fail(f"unsupported lifecycle transition: {transition}")
    if not _fs09_re.fullmatch(r"[0-9a-f]{40}", expected_head):
        _fs09_fail("expected HEAD must be an exact lowercase 40-character Git commit")
    target = _fs09_safe_target(root)
    resolved_root = root.resolve(strict=True)
    branch = _fs09_git(resolved_root, "branch", "--show-current")
    if not branch:
        _fs09_fail("detached HEAD is prohibited")
    if branch != expected_branch:
        _fs09_fail(f"wrong branch: expected {expected_branch}, found {branch}")
    head = _fs09_git(resolved_root, "rev-parse", "HEAD")
    if head != expected_head:
        _fs09_fail(f"wrong HEAD: expected {expected_head}, found {head}")
    status = _fs09_git(resolved_root, "status", "--porcelain=v1", "--untracked-files=all")
    if status:
        _fs09_fail("target repository must be clean; staged, tracked, and untracked changes are prohibited")

    contract, contract_digest, state_schema, auth_schema = _fs09_load_contract_and_schemas()
    manifest, _ = _fs09_read_json(resolved_root / ".floppy/manifest.json", "target project manifest")
    registry, _ = _fs09_read_json(resolved_root / ".floppy/orchestrator-registry.json", "target project orchestrator registry")
    if not isinstance(manifest, dict) or not isinstance(registry, dict):
        _fs09_fail("target project authority and writer records must be JSON objects")
    project_repository, source_version = _fs09_project_identity(manifest, resolved_root)

    authorization = manifest.get("active_work_authorization")
    if not isinstance(authorization, dict):
        _fs09_fail("active lifecycle authorization is missing")
    _fs09_validate_schema(authorization, auth_schema, auth_schema)
    if authorization.get("authorization_kind") != "section_implementation":
        _fs09_fail("active authorization has the wrong kind")
    human = authorization.get("human_authority")
    if not isinstance(human, dict) or human.get("issued_explicitly") is not True:
        _fs09_fail("active authorization was not explicitly issued by human authority")
    if authorization.get("authorization_id") != authorization_reference:
        _fs09_fail("authorization reference does not match the active authorization")
    if authorization.get("repository") != project_repository:
        _fs09_fail("authorization repository does not match the target project")
    if authorization.get("source_version") != source_version:
        _fs09_fail("authorization source version does not match the target project")
    if authorization.get("branch") != expected_branch:
        _fs09_fail("authorization branch does not match the expected branch")
    auth_worktree = authorization.get("worktree")
    if not isinstance(auth_worktree, str) or not _fs09_same_path(_FS09Path(auth_worktree), resolved_root):
        _fs09_fail("authorization worktree does not match the exact target root")
    required_head = authorization.get("required_head")
    if required_head not in (None, "THIS_COMMIT", expected_head):
        _fs09_fail("authorization required HEAD does not match the expected HEAD")
    base = authorization.get("base_checkpoint")
    if not isinstance(base, str) or not _fs09_re.fullmatch(r"[0-9a-f]{40}", base):
        _fs09_fail("authorization base checkpoint is malformed")
    ancestor = _fs09_subprocess.run(
        [
            "git", "-c", f"safe.directory={resolved_root}", "-C", str(resolved_root),
            "merge-base", "--is-ancestor", base, expected_head,
        ],
        stdout=_fs09_subprocess.PIPE,
        stderr=_fs09_subprocess.PIPE,
        check=False,
    )
    if ancestor.returncode != 0:
        _fs09_fail("authorization base checkpoint is stale or is not an ancestor of expected HEAD")
    scope = authorization.get("exact_file_scope")
    if not isinstance(scope, list) or _FS09_TARGET not in scope:
        _fs09_fail("active authorization exact_file_scope omits the normative lifecycle target")

    assignments = registry.get("current_assignments")
    if not isinstance(assignments, dict):
        _fs09_fail("orchestrator registry current assignments are missing")
    if assignments.get("current_section_working_model") != repository_writer:
        _fs09_fail("registered section working model does not match the invocation writer")
    if assignments.get("repository_writer") != repository_writer:
        _fs09_fail("registered repository writer does not match the invocation writer")
    if assignments.get("writer_authorization_reference") != authorization_reference:
        _fs09_fail("registered writer authorization reference is stale or mismatched")
    if authorization.get("repository_writer") not in (None, repository_writer):
        _fs09_fail("authorization repository writer does not match the registered writer")
    if authorization.get("writer_authorization_reference") not in (None, authorization_reference):
        _fs09_fail("authorization writer reference does not match the invocation")
    if authorization.get("working_model_id") not in (None, repository_writer):
        _fs09_fail("authorization working model does not match the registered writer")

    state, state_bytes = _fs09_read_json(target, "canonical lifecycle-state file")
    if not isinstance(state, dict):
        _fs09_fail("canonical lifecycle-state root must be an object")
    if state_bytes != _fs09_canonical_json(state):
        _fs09_fail("canonical lifecycle-state serialization is not deterministic")
    _fs09_validate_schema(state, state_schema, state_schema)
    if state.get("state_id") != _FS09_SOURCE_STATE:
        _fs09_fail("canonical lifecycle-state is not the accepted TR-004 source state")
    section = authorization.get("section")
    if not isinstance(section, str) or not section:
        _fs09_fail("active authorization section is missing")
    if state.get("section") != section:
        _fs09_fail("lifecycle-state section does not match the active authorization")
    if state.get("authorization_id") != authorization_reference:
        _fs09_fail("lifecycle-state authorization_id does not match active authority")
    if state.get("base_checkpoint") != base:
        _fs09_fail("lifecycle-state base checkpoint does not match active authority")
    dimensions = state.get("dimensions")
    accepted_source = contract["supported_transitions"][0]["source_dimensions"]
    if dimensions != accepted_source:
        _fs09_fail("lifecycle-state dimensions do not match the accepted TR-004 source profile")
    if state.get("active_implementation_sections") != [section]:
        _fs09_fail("lifecycle-state active section does not match the authorized section")

    proposed = {
        "state_id": _FS09_DESTINATION_STATE,
        "section": section,
        "authorization_id": authorization_reference,
        "base_checkpoint": base,
        "dimensions": contract["supported_transitions"][0]["destination_dimensions"],
        "active_implementation_sections": [section],
        "evidence": [
            f"AUTHORIZATION:{authorization_reference}",
            f"START_CHECKPOINT:{expected_head}",
            f"APPLIED_TRANSITION:{_FS09_TRANSITION}",
        ],
    }
    _fs09_validate_schema(proposed, state_schema, state_schema)
    proposed_bytes = _fs09_canonical_json(proposed)
    current_digest = _fs09_sha256(state_bytes)
    proposed_digest = _fs09_sha256(proposed_bytes)

    plan_core = {
        "target_project_identity": project_repository,
        "target_branch": branch,
        "target_head": head,
        "authorization_reference": authorization_reference,
        "registered_repository_writer": repository_writer,
        "transition_id": transition,
        "exact_target_path": _FS09_TARGET,
        "operation": "REPLACE",
        "expected_current_sha256": current_digest,
        "proposed_replacement_sha256": proposed_digest,
        "proposed_byte_size": len(proposed_bytes),
        "contract_sha256": contract_digest,
        "validation_result": "PASSED",
        "application_permitted": True,
    }
    plan_digest = _fs09_sha256(_fs09_canonical_json(plan_core))
    return {
        "root": resolved_root,
        "target": target,
        "state_bytes": state_bytes,
        "proposed_bytes": proposed_bytes,
        "current_mode": target.stat().st_mode,
        "plan_core": plan_core,
        "plan_sha256": plan_digest,
    }


def _fs09_sync_file(handle: _FS09Any) -> None:
    handle.flush()
    _fs09_os.fsync(handle.fileno())


def _fs09_sync_directory(directory: _FS09Path) -> None:
    if _fs09_os.name == "nt":
        return
    flags = getattr(_fs09_os, "O_DIRECTORY", 0) | _fs09_os.O_RDONLY
    descriptor = None
    try:
        descriptor = _fs09_os.open(str(directory), flags)
        _fs09_os.fsync(descriptor)
    except OSError:
        pass
    finally:
        if descriptor is not None:
            _fs09_os.close(descriptor)


def _fs09_stage(path: _FS09Path, data: bytes, mode: int, *, restoring: bool = False) -> None:
    label = "restore" if restoring else "stage"
    flags = _fs09_os.O_WRONLY | _fs09_os.O_CREAT | _fs09_os.O_EXCL
    descriptor = None
    try:
        descriptor = _fs09_os.open(str(path), flags, mode & 0o777)
        with _fs09_os.fdopen(descriptor, "wb", closefd=True) as handle:
            descriptor = None
            midpoint = len(data) // 2
            handle.write(data[:midpoint])
            _fs09_hook(f"during_{label}_write", {"path": path, "handle": handle})
            handle.write(data[midpoint:])
            _fs09_sync_file(handle)
        try:
            _fs09_os.chmod(path, mode & 0o777)
        except OSError:
            pass
    except FileExistsError:
        _fs09_fail(f"exclusive {label} file already exists")
    except CliError:
        raise
    except OSError as exc:
        _fs09_fail(f"{label} file write failed: {exc}")
    finally:
        if descriptor is not None:
            _fs09_os.close(descriptor)


def _fs09_apply(prepared: dict[str, _FS09Any]) -> None:
    target: _FS09Path = prepared["target"]
    original: bytes = prepared["state_bytes"]
    proposed: bytes = prepared["proposed_bytes"]
    expected_digest = prepared["plan_core"]["expected_current_sha256"]
    proposed_digest = prepared["plan_core"]["proposed_replacement_sha256"]
    mode = int(prepared["current_mode"])
    stage = target.with_name(".lifecycle-state.json.fs09-stage")
    restore = target.with_name(".lifecycle-state.json.fs09-restore")
    for candidate in (stage, restore):
        if candidate.exists():
            _fs09_fail(f"temporary lifecycle-write file collision: {candidate.name}")
    replaced = False
    try:
        _fs09_hook("before_stage", {"target": target})
        _fs09_stage(stage, proposed, mode)
        _fs09_hook("after_stage", {"target": target, "stage": stage})
        if _fs09_sha256(stage.read_bytes()) != proposed_digest:
            _fs09_fail("staged replacement SHA-256 verification failed")
        _fs09_hook("after_validation", {"target": target, "stage": stage})
        if _fs09_sha256(target.read_bytes()) != expected_digest:
            _fs09_fail("canonical lifecycle-state changed after planning")
        _fs09_hook("before_replace", {"target": target, "stage": stage})
        _fs09_hook("replacement", {"target": target, "stage": stage})
        _fs09_os.replace(stage, target)
        replaced = True
        _fs09_sync_directory(target.parent)
        _fs09_hook("before_final_verify", {"target": target})
        final = target.read_bytes()
        if len(final) != len(proposed) or _fs09_sha256(final) != proposed_digest:
            _fs09_fail("final lifecycle-state verification failed")
    except Exception as primary:
        if replaced:
            try:
                if restore.exists():
                    restore.unlink()
                _fs09_stage(restore, original, mode, restoring=True)
                _fs09_hook("before_restore_replace", {"target": target, "restore": restore})
                _fs09_os.replace(restore, target)
                _fs09_sync_directory(target.parent)
                restored = target.read_bytes()
                if len(restored) != len(original) or _fs09_sha256(restored) != expected_digest:
                    _fs09_fail("restored lifecycle-state verification failed")
            except Exception as restoration:
                raise CliError(
                    "HIGH-SEVERITY: lifecycle-state restoration failed after apply failure: "
                    f"{restoration}"
                ) from restoration
            raise CliError(f"lifecycle-state apply failed; original bytes restored: {primary}") from primary
        if isinstance(primary, CliError):
            raise
        raise CliError(f"lifecycle-state apply failed before replacement: {primary}") from primary
    finally:
        for candidate in (stage, restore):
            try:
                if candidate.exists():
                    candidate.unlink()
            except OSError:
                pass


def _fs09_operation(
    root: _FS09Path,
    *,
    mode: str,
    transition: str,
    authorization_reference: str,
    repository_writer: str,
    expected_branch: str,
    expected_head: str,
    plan_sha256: str | None = None,
) -> dict[str, _FS09Any]:
    prepared = _fs09_prepare(
        root,
        transition=transition,
        authorization_reference=authorization_reference,
        repository_writer=repository_writer,
        expected_branch=expected_branch,
        expected_head=expected_head,
    )
    result = dict(prepared["plan_core"])
    result["plan_sha256"] = prepared["plan_sha256"]
    if mode == "dry-run":
        if plan_sha256 is not None:
            _fs09_fail("--plan-sha256 is not accepted during dry-run")
        result["operation_mode"] = "DRY_RUN"
        result["applied"] = False
        return result
    if mode != "apply":
        _fs09_fail("operation mode must be dry-run or apply")
    if not isinstance(plan_sha256, str) or plan_sha256 != prepared["plan_sha256"]:
        _fs09_fail("apply requires the exact current dry-run plan SHA-256")
    _fs09_apply(prepared)
    result["operation_mode"] = "APPLY"
    result["applied"] = True
    return result


def _fs09_parse_cli(arguments: list[str]) -> _FS09Any:
    parser = _fs09_argparse.ArgumentParser(prog="floppyctl")
    parser.add_argument("--root", required=True)
    subparsers = parser.add_subparsers(dest="command", required=True)
    lifecycle = subparsers.add_parser("lifecycle-write")
    lifecycle.add_argument("--mode", required=True, choices=("dry-run", "apply"))
    lifecycle.add_argument("--transition", required=True)
    lifecycle.add_argument("--authorization-reference", required=True)
    lifecycle.add_argument("--repository-writer", required=True)
    lifecycle.add_argument("--expected-branch", required=True)
    lifecycle.add_argument("--expected-head", required=True)
    lifecycle.add_argument("--plan-sha256")
    return parser.parse_args(arguments)


def _fs09_cli(arguments: list[str]) -> int:
    try:
        namespace = _fs09_parse_cli(arguments)
        result = _fs09_operation(
            _FS09Path(namespace.root),
            mode=namespace.mode,
            transition=namespace.transition,
            authorization_reference=namespace.authorization_reference,
            repository_writer=namespace.repository_writer,
            expected_branch=namespace.expected_branch,
            expected_head=namespace.expected_head,
            plan_sha256=namespace.plan_sha256,
        )
        print(
            _fs09_json.dumps(
                result,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    except SystemExit as exc:
        return int(exc.code)
    except CliError as exc:
        return _error(str(exc))



# === FS-12 VALIDATED FINAL-PROJECT CLOSURE BEGIN ===
_FS12_FINAL_RECORD = ".floppy/closeouts/FINAL-PROJECT-CLOSURE.md"
_FS12_FINAL_PATHS = (
    ".floppy/README.md",
    ".floppy/START-HERE.md",
    _FS12_FINAL_RECORD,
    ".floppy/floppies/Floppy-D-Project-Map.md",
    ".floppy/floppies/Floppy-E-Current-Section.md",
    ".floppy/lifecycle-state.json",
    ".floppy/manifest.json",
    ".floppy/orchestrator-registry.json",
    ".floppy/roadmap/roadmap.json",
    ".floppy/roadmap/roadmap.md",
)
_FS12_PROPOSAL_BEGIN = "<!-- FINAL_PROJECT_CLOSURE_PROPOSAL_BEGIN -->"
_FS12_PROPOSAL_END = "<!-- FINAL_PROJECT_CLOSURE_PROPOSAL_END -->"
_FS12_APPLICATION_BEGIN = "<!-- FINAL_PROJECT_CLOSURE_APPLICATION_BEGIN -->"
_FS12_APPLICATION_END = "<!-- FINAL_PROJECT_CLOSURE_APPLICATION_END -->"
_FS12_TEST_HOOK = None


def _fs12_canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _fs12_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fs12_git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root), *args], text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        raise CliError(result.stderr.strip() or result.stdout.strip() or "Git command failed")
    return result.stdout.strip()


def _fs12_final_route(state_id: str, action: str) -> tuple[str, str, str]:
    routes = {
        ("propose", "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE"): ("TR-021-PROPOSE-FINAL-CLOSURE-NO-MIGRATION", "LC-PROJECT-CLOSURE-PROPOSED-NO-MIGRATION", "NONE"),
        ("propose", "LC-MIGRATION-APPLIED-VERIFICATION-COMPLETE"): ("TR-014-PROPOSE-FINAL-CLOSURE", "LC-PROJECT-CLOSURE-PROPOSED", "APPLIED_VERIFICATION_COMPLETE"),
        ("apply", "LC-PROJECT-CLOSURE-PROPOSED-NO-MIGRATION"): ("TR-022-APPLY-FINAL-CLOSURE-NO-MIGRATION", "LC-PROJECT-FINALLY-CLOSED-NO-MIGRATION", "NONE"),
        ("apply", "LC-PROJECT-CLOSURE-PROPOSED"): ("TR-015-APPLY-FINAL-CLOSURE", "LC-PROJECT-FINALLY-CLOSED", "APPLIED_VERIFICATION_COMPLETE"),
    }
    try:
        return routes[(action, state_id)]
    except KeyError as exc:
        raise CliError(f"final-closure {action} is not legal from {state_id}") from exc


def _fs12_assert_final_ready(root: Path, manifest: dict[str, Any], registry: dict[str, Any], roadmap: dict[str, Any]) -> None:
    if manifest.get("active_work_authorization") is not None or manifest.get("active_control_work_authorization") is not None:
        raise CliError("final closure requires no active authorization")
    if manifest.get("repository_writer") is not None or manifest.get("writer_authorization_reference") is not None:
        raise CliError("final closure requires no repository writer")
    assignments = registry.get("current_assignments")
    if not isinstance(assignments, dict) or any(assignments.get(k) is not None for k in ("current_section_working_model", "repository_writer", "writer_authorization_reference")):
        raise CliError("final closure requires a cleared canonical orchestrator registry")
    sections = roadmap.get("sections")
    if not isinstance(sections, list) or not sections:
        raise CliError("final closure requires a non-empty canonical roadmap section inventory")
    open_sections = [str(x.get("id")) for x in sections if isinstance(x, dict) and x.get("status") != "CLOSED"]
    if open_sections:
        raise CliError("final closure is blocked by open required sections: " + ", ".join(open_sections))


def _fs12_proposal_bytes(record_bytes: bytes) -> tuple[bytes, str]:
    text = record_bytes.decode("utf-8")
    start = text.find(_FS12_PROPOSAL_BEGIN)
    end = text.find(_FS12_PROPOSAL_END)
    if start < 0 or end < 0 or end <= start:
        raise CliError("canonical final-closure proposal block is missing")
    end += len(_FS12_PROPOSAL_END)
    block = text[start:end].encode("utf-8")
    return block, _fs12_digest(block)


def _fs12_prepare_final_closure(root: Path, *, action: str, expected_branch: str, expected_head: str, evidence: list[str], proposal_sha256: str | None, authorization_reference: str | None) -> dict[str, Any]:
    root = root.expanduser().resolve()
    if _fs12_git(root, "branch", "--show-current") != expected_branch:
        raise CliError("final-closure branch mismatch")
    if _fs12_git(root, "rev-parse", "HEAD") != expected_head:
        raise CliError("final-closure HEAD mismatch")
    if _fs12_git(root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise CliError("final-closure target repository must be clean")
    if action not in {"propose", "apply"}:
        raise CliError("final-closure action must be propose or apply")
    if action == "propose" and authorization_reference is not None:
        raise CliError("final-closure proposal does not accept application authority")
    if action == "apply" and authorization_reference != "FINAL_CLOSURE_APPLICATION":
        raise CliError("final-closure application requires FINAL_CLOSURE_APPLICATION authority")
    lifecycle = _read_json(root / ".floppy/lifecycle-state.json", "canonical lifecycle state")
    manifest = _read_json(root / ".floppy/manifest.json", "canonical manifest")
    registry = _read_json(root / ".floppy/orchestrator-registry.json", "canonical orchestrator registry")
    roadmap = _read_json(root / ".floppy/roadmap/roadmap.json", "canonical roadmap")
    _fs12_assert_final_ready(root, manifest, registry, roadmap)
    transition, target_state, migration = _fs12_final_route(str(lifecycle.get("state_id")), action)
    dims = dict(lifecycle.get("dimensions") or {})
    if dims.get("migration") != migration:
        raise CliError("canonical migration disposition does not match final-closure route")
    candidates: dict[str, bytes] = {}
    record_path = root / _FS12_FINAL_RECORD
    if action == "propose":
        if record_path.exists():
            raise CliError("final-closure proposal record already exists")
        inventory = sorted(set(x.strip() for x in evidence if isinstance(x, str) and x.strip()))
        if not inventory:
            raise CliError("final-closure proposal requires final evidence inventory")
        proposal = {"source_state_id": lifecycle["state_id"], "proposal_transition_id": transition, "target_proposal_state_id": target_state, "migration_disposition": migration, "final_evidence_inventory": inventory, "proposal_base_checkpoint": expected_head, "proposal_commit": "THIS_COMMIT", "canonical_proposal_sha256": "EXTERNAL_FIELD", "exact_proposed_path_set": list(_FS12_FINAL_PATHS)}
        proposal_json = _fs12_canonical(proposal).decode("utf-8").rstrip("\n")
        record = f"# Final Project Closure\n\n{_FS12_PROPOSAL_BEGIN}\n```json\n{proposal_json}\n```\n{_FS12_PROPOSAL_END}\n"
        block_digest = _fs12_digest(record[record.index(_FS12_PROPOSAL_BEGIN):record.index(_FS12_PROPOSAL_END)+len(_FS12_PROPOSAL_END)].encode("utf-8"))
        record += f"\nCanonical proposal SHA-256: `{block_digest}`\n"
        candidates[_FS12_FINAL_RECORD] = record.encode("utf-8")
        proposal_meta = {"record": _FS12_FINAL_RECORD, "transition": transition, "target_state": target_state, "migration": migration, "proposal_base_checkpoint": expected_head, "proposal_commit": "THIS_COMMIT", "proposal_sha256": block_digest, "evidence_inventory": inventory, "status": "PROPOSED"}
        manifest["final_closure_proposal"] = proposal_meta
        registry["final_closure_proposal"] = proposal_meta
        roadmap["final_closure"] = proposal_meta
    else:
        if not record_path.is_file():
            raise CliError("reviewed final-closure proposal record is missing")
        record_bytes = record_path.read_bytes()
        block, actual_digest = _fs12_proposal_bytes(record_bytes)
        metadata = manifest.get("final_closure_proposal")
        if not isinstance(metadata, dict) or metadata.get("proposal_sha256") != actual_digest:
            raise CliError("canonical proposal metadata or SHA-256 is inconsistent")
        if proposal_sha256 != actual_digest:
            raise CliError("application proposal SHA-256 does not match reviewed proposal")
        if metadata.get("target_state") != lifecycle.get("state_id") or metadata.get("migration") != migration:
            raise CliError("cross-route or stale final-closure application is prohibited")
        if _FS12_APPLICATION_BEGIN in record_bytes.decode("utf-8"):
            raise CliError("final-closure application already exists")
        proposal_commit = _fs12_git(root, "log", "-1", "--format=%H", "--", _FS12_FINAL_RECORD)
        application = {"application_transition_id": transition, "source_proposal_state_id": lifecycle["state_id"], "target_final_state_id": target_state, "migration_disposition": migration, "proposal_commit": proposal_commit, "proposal_sha256": actual_digest, "reviewed_final_checkpoint": expected_head, "authorization_reference": authorization_reference}
        appendix = f"\n{_FS12_APPLICATION_BEGIN}\n```json\n{_fs12_canonical(application).decode('utf-8').rstrip()}\n```\n{_FS12_APPLICATION_END}\n"
        candidates[_FS12_FINAL_RECORD] = record_bytes + appendix.encode("utf-8")
        manifest["final_closure_application"] = {**application, "record": _FS12_FINAL_RECORD, "status": "APPLIED"}
        registry["final_closure_application"] = manifest["final_closure_application"]
        roadmap["final_closure"] = manifest["final_closure_application"]
    dims["acceptance"] = "ACCEPTED"
    dims["final_closure"] = "PROPOSED" if action == "propose" else "FINALLY_CLOSED"
    lifecycle.update({"state_id": target_state, "section": None, "authorization_id": None, "base_checkpoint": expected_head, "dimensions": dims, "active_implementation_sections": []})
    lifecycle["evidence"] = list(lifecycle.get("evidence") or []) + [f"APPLIED_TRANSITION:{transition}", f"FINAL_CLOSURE_CHECKPOINT:{expected_head}"]
    manifest["status"] = target_state
    manifest.setdefault("authority", {}).update({"last_applied_transition": transition, "authority_state": "NO_ACTIVE_WORK_AUTHORIZATION", "active_work_authorization": None, "active_implementation_authorization": None, "active_migration_authorization": None, "active_implementation_section": None, "current_authorized_section": None, "authorization_id": None, "repository_writer": None, "writer_authorization_reference": None})
    manifest["active_work_authorization"] = None; manifest["active_control_work_authorization"] = None; manifest["repository_writer"] = None; manifest["writer_authorization_reference"] = None
    roadmap["lifecycle_state"] = target_state; roadmap["last_applied_transition"] = transition; roadmap["current_authorized_section"] = None; roadmap["active_implementation_section"] = None
    registry.setdefault("current_assignments", {}).update({"current_section_working_model": None, "repository_writer": None, "writer_authorization_reference": None})
    candidates[".floppy/lifecycle-state.json"] = _fs12_canonical(lifecycle)
    candidates[".floppy/manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    candidates[".floppy/orchestrator-registry.json"] = _fs12_canonical(registry)
    candidates[".floppy/roadmap/roadmap.json"] = (json.dumps(roadmap, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    human = f"\n\n## Final-project closure\n\n```text\nTransition: {transition}\nState: {target_state}\nMigration: {migration}\nOperation: {action.upper()}\n```\n"
    for relative in (".floppy/README.md", ".floppy/START-HERE.md", ".floppy/floppies/Floppy-D-Project-Map.md", ".floppy/floppies/Floppy-E-Current-Section.md", ".floppy/roadmap/roadmap.md"):
        candidates[relative] = (root / relative).read_bytes().rstrip() + human.encode("utf-8")
    if set(candidates) != set(_FS12_FINAL_PATHS):
        raise CliError("internal final-closure candidate path inventory mismatch")
    hashes = {path: _fs12_digest(data) for path, data in sorted(candidates.items())}
    plan_core = {"action": action, "transition": transition, "source_state": lifecycle.get("state_id") if False else ("reviewed-proposal" if action == "apply" else proposal.get("source_state_id")), "target_state": target_state, "migration_disposition": migration, "expected_branch": expected_branch, "expected_head": expected_head, "exact_paths": list(_FS12_FINAL_PATHS), "candidate_sha256": hashes, "proposal_sha256": manifest.get("final_closure_proposal", {}).get("proposal_sha256"), "authorization_reference": authorization_reference}
    return {"root": root, "candidates": candidates, "plan_core": plan_core, "plan_sha256": _fs12_digest(_fs12_canonical(plan_core))}


def _fs12_apply_candidates(prepared: dict[str, Any]) -> None:
    root: Path = prepared["root"]
    candidates: dict[str, bytes] = prepared["candidates"]
    originals: dict[str, bytes | None] = {p: ((root / p).read_bytes() if (root / p).exists() else None) for p in candidates}
    staged: dict[str, Path] = {}
    replaced: list[str] = []
    try:
        for relative, data in candidates.items():
            target = root / relative; target.parent.mkdir(parents=True, exist_ok=True)
            stage = target.with_name(target.name + ".fs12-stage")
            if stage.exists(): stage.unlink()
            stage.write_bytes(data)
            if _fs12_digest(stage.read_bytes()) != _fs12_digest(data): raise CliError(f"staged final-closure digest mismatch: {relative}")
            staged[relative] = stage
        hook = globals().get("_FS12_TEST_HOOK")
        if callable(hook): hook("before_replace", {"root": root, "candidates": candidates})
        for relative in _FS12_FINAL_PATHS:
            os.replace(staged[relative], root / relative); replaced.append(relative)
            if callable(hook): hook("after_replace", {"path": relative, "count": len(replaced)})
        for relative, data in candidates.items():
            if (root / relative).read_bytes() != data: raise CliError(f"final-closure write verification failed: {relative}")
    except Exception as exc:
        restoration: list[str] = []
        for relative in reversed(replaced):
            target = root / relative; original = originals[relative]
            try:
                if original is None:
                    if target.exists(): target.unlink()
                else:
                    restore = target.with_name(target.name + ".fs12-restore")
                    if restore.exists(): restore.unlink()
                    restore.write_bytes(original); os.replace(restore, target)
            except Exception as restore_exc:
                restoration.append(f"{relative}: {restore_exc}")
        if restoration: raise CliError("HIGH-SEVERITY: final-closure rollback failed: " + "; ".join(restoration)) from exc
        if isinstance(exc, CliError): raise
        raise CliError(f"final-closure apply failed; original bytes restored: {exc}") from exc
    finally:
        for path in staged.values():
            try:
                if path.exists(): path.unlink()
            except OSError: pass


def _fs12_final_closure_operation(root: Path, *, mode: str, action: str, expected_branch: str, expected_head: str, evidence: list[str] | None = None, plan_sha256: str | None = None, proposal_sha256: str | None = None, authorization_reference: str | None = None) -> dict[str, Any]:
    prepared = _fs12_prepare_final_closure(root, action=action, expected_branch=expected_branch, expected_head=expected_head, evidence=list(evidence or []), proposal_sha256=proposal_sha256, authorization_reference=authorization_reference)
    result = dict(prepared["plan_core"]); result["plan_sha256"] = prepared["plan_sha256"]
    if mode == "dry-run":
        if plan_sha256 is not None: raise CliError("--plan-sha256 is not accepted during dry-run")
        result.update({"operation_mode": "DRY_RUN", "applied": False}); return result
    if mode != "apply": raise CliError("final-closure mode must be dry-run or apply")
    if plan_sha256 != prepared["plan_sha256"]: raise CliError("apply requires the exact current dry-run plan SHA-256")
    _fs12_apply_candidates(prepared); result.update({"operation_mode": "APPLY", "applied": True}); return result


def _fs12_final_closure_cli(arguments: list[str]) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="floppyctl")
    parser.add_argument("--root", required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    final = sub.add_parser("final-closure")
    final.add_argument("--mode", required=True, choices=("dry-run", "apply")); final.add_argument("--action", required=True, choices=("propose", "apply")); final.add_argument("--expected-branch", required=True); final.add_argument("--expected-head", required=True); final.add_argument("--evidence", action="append", default=[]); final.add_argument("--proposal-sha256"); final.add_argument("--authorization-reference"); final.add_argument("--plan-sha256")
    try:
        ns = parser.parse_args(arguments)
        value = _fs12_final_closure_operation(Path(ns.root), mode=ns.mode, action=ns.action, expected_branch=ns.expected_branch, expected_head=ns.expected_head, evidence=ns.evidence, proposal_sha256=ns.proposal_sha256, authorization_reference=ns.authorization_reference, plan_sha256=ns.plan_sha256)
        print(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))); return 0
    except SystemExit as exc: return int(exc.code)
    except CliError as exc: return _error(str(exc))
# === FS-12 VALIDATED FINAL-PROJECT CLOSURE END ===

def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if "lifecycle-write" in arguments:
        return _fs09_cli(arguments)
    if "final-closure" in arguments:
        return _fs12_final_closure_cli(arguments)
    signature = _fs09_inspect.signature(_legacy_main)
    if len(signature.parameters) == 0:
        if argv is None:
            return _legacy_main()
        original = sys.argv
        try:
            sys.argv = [original[0], *arguments]
            return _legacy_main()
        finally:
            sys.argv = original
    return _legacy_main(arguments)
# === FS-09 CONTROLLED LIFECYCLE WRITES END ===

if __name__ == "__main__":
    raise SystemExit(main())