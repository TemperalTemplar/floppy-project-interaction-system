#!/usr/bin/env python3
"""Thin read-only CLI for registered Floppy records and validation."""

from __future__ import annotations

import hashlib
import io
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
    "schemas/drafts/bce-lifecycle-state.schema.json",
    "schemas/drafts/bce-lifecycle-transition.schema.json",
    "schemas/drafts/bce-work-authorization.schema.json",
    "schemas/floppy-fields.md",
    "specs/lifecycle-state-model.md",
    "specs/lifecycle-transition-table.json",
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
    if command not in {"status", "validate", "inspect", "scan", "package", "verify-package"}:
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