from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "tools" / "floppyctl.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("floppyctl_fs13", CLI_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load tools/floppyctl.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CLI = load_cli()


def git(root: Path, *args: str) -> str:
    env = os.environ.copy()
    if args and args[0] == "commit":
        env["GIT_AUTHOR_DATE"] = "2000-01-01T00:00:00+00:00"
        env["GIT_COMMITTER_DATE"] = "2000-01-01T00:00:00+00:00"
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={root.as_posix()}",
            "-C",
            str(root),
            *args,
        ],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        env=env,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return result.stdout.strip()


def canonical(path: Path, value: dict) -> None:
    path.write_bytes(
        (
            json.dumps(
                value,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode("utf-8")
    )


def make_project(base: Path, *, source_root: bool = False) -> Path:
    root = base / "project"
    root.mkdir()
    floppy = root / ".floppy"
    (floppy / "roadmap").mkdir(parents=True)
    (floppy / "floppies").mkdir()
    manifest = {
        "project_name": "Portable Project",
        "control_state": {"repository": "owner/project"},
        "system": {
            "source_repository": "owner/floppy",
            "version": "0.4.3-dev",
        },
    }
    if source_root:
        manifest["bce_instance"] = {"self_hosted_control_state": True}
        manifest["clean_source_integration_policy"] = {
            "include_root_control_state_in_cross_project_bce_exports": False
        }
    canonical(floppy / "manifest.json", manifest)
    canonical(
        floppy / "lifecycle-state.json",
        {"state_id": "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE"},
    )
    canonical(floppy / "roadmap/roadmap.json", {"status": "accepted"})
    (floppy / "floppies/Floppy-A-HITL.md").write_text(
        "A\n",
        encoding="utf-8",
    )
    git(root, "init")
    git(root, "config", "user.email", "fs13@example.invalid")
    git(root, "config", "user.name", "FS13 Tests")
    git(root, "add", ".")
    git(root, "commit", "-m", "fixture")
    return root


def artifacts(payload: dict) -> tuple[Path, Path]:
    return Path(payload["archive"]["path"]), Path(payload["manifest"]["path"])


def write_integrity(path: Path, value: dict) -> None:
    canonical(path, value)


def rebuild(path: Path, entries: list[tuple[str, bytes]]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(
        buffer,
        "w",
        compression=zipfile.ZIP_STORED,
    ) as archive:
        for name, data in entries:
            info = zipfile.ZipInfo(
                name,
                CLI.BOOT_PACKAGE_FIXED_TIMESTAMP,
            )
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.create_version = 20
            info.extract_version = 20
            info.flag_bits = 0
            info.internal_attr = 0
            info.external_attr = CLI.BOOT_PACKAGE_EXTERNAL_ATTR
            info.comment = b""
            info.extra = b""
            archive.writestr(info, data)
    data = buffer.getvalue()
    path.write_bytes(data)
    return data


class ExportIntegrityTests(unittest.TestCase):
    def test_exports_only_tracked_floppy_context_and_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_project(base)
            destination = base / "out"
            destination.mkdir()
            payload = CLI.build_context_export(root, destination)
            archive_path, manifest_path = artifacts(payload)
            self.assertEqual(
                payload["context_commit"],
                git(root, "rev-parse", "HEAD"),
            )
            with zipfile.ZipFile(archive_path) as archive:
                names = archive.namelist()
                self.assertEqual(names, sorted(names))
                self.assertTrue(all(name.startswith(".floppy/") for name in names))
            self.assertTrue(
                CLI.verify_context_export(
                    archive_path,
                    manifest_path,
                )["verified"]
            )

    def test_source_self_hosted_control_state_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_project(base, source_root=True)
            destination = base / "out"
            destination.mkdir()
            with self.assertRaisesRegex(
                CLI.CliError,
                "source-development root",
            ):
                CLI.build_context_export(root, destination)

    def test_dirty_repository_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_project(base)
            destination = base / "out"
            destination.mkdir()
            (root / "outside.txt").write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(
                CLI.CliError,
                "repository is not clean",
            ):
                CLI.build_context_export(root, destination)

    def test_ignored_context_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_project(base)
            destination = base / "out"
            destination.mkdir()
            (root / ".gitignore").write_text(
                ".floppy/ignored.txt\n",
                encoding="utf-8",
            )
            git(root, "add", ".gitignore")
            git(root, "commit", "-m", "ignore")
            (root / ".floppy/ignored.txt").write_text(
                "ignored",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                CLI.CliError,
                "untracked or ignored context content",
            ):
                CLI.build_context_export(root, destination)

    def test_symlink_context_is_rejected_where_supported(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_project(base)
            destination = base / "out"
            destination.mkdir()
            target = root / ".floppy/floppies/Floppy-A-HITL.md"
            link = root / ".floppy/link.md"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            git(root, "add", ".floppy/link.md")
            git(root, "commit", "-m", "link")
            with self.assertRaisesRegex(CLI.CliError, "unsafe"):
                CLI.build_context_export(root, destination)

    def test_repeat_export_is_byte_identical_and_reused(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_project(base)
            destination = base / "out"
            destination.mkdir()
            first = CLI.build_context_export(root, destination)
            archive_path, manifest_path = artifacts(first)
            archive_bytes = archive_path.read_bytes()
            manifest_bytes = manifest_path.read_bytes()
            second = CLI.build_context_export(root, destination)
            self.assertEqual(second["archive"]["state"], "reused")
            self.assertEqual(second["manifest"]["state"], "reused")
            self.assertEqual(archive_path.read_bytes(), archive_bytes)
            self.assertEqual(manifest_path.read_bytes(), manifest_bytes)

    def test_differing_artifact_collision_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_project(base)
            destination = base / "out"
            destination.mkdir()
            payload = CLI.build_context_export(root, destination)
            archive_path, _ = artifacts(payload)
            archive_path.write_bytes(b"wrong")
            with self.assertRaisesRegex(
                CLI.CliError,
                "artifact collision differs",
            ):
                CLI.build_context_export(root, destination)

    def test_export_is_checkout_location_and_cwd_independent(self) -> None:
        with (
            tempfile.TemporaryDirectory() as a,
            tempfile.TemporaryDirectory() as b,
            tempfile.TemporaryDirectory() as other,
        ):
            first_root = make_project(Path(a))
            second_root = make_project(Path(b))
            first_out = Path(a) / "out"
            second_out = Path(b) / "out"
            first_out.mkdir()
            second_out.mkdir()
            previous = Path.cwd()
            try:
                os.chdir(other)
                first = CLI.build_context_export(first_root, first_out)
                second = CLI.build_context_export(second_root, second_out)
            finally:
                os.chdir(previous)
            first_archive, first_manifest = artifacts(first)
            second_archive, second_manifest = artifacts(second)
            self.assertEqual(
                git(first_root, "rev-parse", "HEAD"),
                git(second_root, "rev-parse", "HEAD"),
            )
            self.assertEqual(
                first_archive.read_bytes(),
                second_archive.read_bytes(),
            )
            self.assertEqual(
                first_manifest.read_bytes(),
                second_manifest.read_bytes(),
            )

    def test_fixed_zip_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_project(base)
            destination = base / "out"
            destination.mkdir()
            payload = CLI.build_context_export(root, destination)
            archive_path, _ = artifacts(payload)
            with zipfile.ZipFile(archive_path) as archive:
                self.assertEqual(archive.comment, b"")
                for info in archive.infolist():
                    self.assertEqual(
                        info.date_time,
                        CLI.BOOT_PACKAGE_FIXED_TIMESTAMP,
                    )
                    self.assertEqual(
                        info.compress_type,
                        zipfile.ZIP_STORED,
                    )
                    self.assertEqual(info.create_system, 3)
                    self.assertEqual(
                        info.external_attr,
                        CLI.BOOT_PACKAGE_EXTERNAL_ATTR,
                    )
                    self.assertEqual(info.comment, b"")
                    self.assertEqual(info.extra, b"")
                    self.assertEqual(info.flag_bits, 0)

    def test_tampered_archive_hash_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_project(base)
            destination = base / "out"
            destination.mkdir()
            payload = CLI.build_context_export(root, destination)
            archive_path, manifest_path = artifacts(payload)
            archive_path.write_bytes(archive_path.read_bytes() + b"x")
            with self.assertRaisesRegex(
                CLI.CliError,
                "archive (size|SHA-256) mismatch",
            ):
                CLI.verify_context_export(archive_path, manifest_path)

    def test_per_entry_tamper_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_project(base)
            destination = base / "out"
            destination.mkdir()
            payload = CLI.build_context_export(root, destination)
            archive_path, manifest_path = artifacts(payload)
            with zipfile.ZipFile(archive_path) as archive:
                entries = [
                    (info.filename, archive.read(info))
                    for info in archive.infolist()
                ]
            entries[-1] = (
                entries[-1][0],
                entries[-1][1] + b"x",
            )
            data = rebuild(archive_path, entries)
            manifest = json.loads(
                manifest_path.read_text(encoding="utf-8")
            )
            manifest["archive"]["size"] = len(data)
            manifest["archive"]["sha256"] = hashlib.sha256(data).hexdigest()
            write_integrity(manifest_path, manifest)
            with self.assertRaisesRegex(
                CLI.CliError,
                "member (size|SHA-256) mismatch",
            ):
                CLI.verify_context_export(archive_path, manifest_path)

    def test_noncanonical_integrity_manifest_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_project(base)
            destination = base / "out"
            destination.mkdir()
            payload = CLI.build_context_export(root, destination)
            archive_path, manifest_path = artifacts(payload)
            manifest = json.loads(
                manifest_path.read_text(encoding="utf-8")
            )
            manifest_path.write_text(
                json.dumps(manifest, indent=2) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(CLI.CliError, "serialization"):
                CLI.verify_context_export(archive_path, manifest_path)

    def test_missing_extra_duplicate_and_case_collision_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_project(base)
            destination = base / "out"
            destination.mkdir()
            for mode in ("missing", "extra", "duplicate", "case"):
                with self.subTest(mode=mode):
                    for item in destination.iterdir():
                        item.unlink()
                    payload = CLI.build_context_export(root, destination)
                    archive_path, manifest_path = artifacts(payload)
                    with zipfile.ZipFile(archive_path) as archive:
                        entries = [
                            (info.filename, archive.read(info))
                            for info in archive.infolist()
                        ]
                    if mode == "missing":
                        entries = entries[:-1]
                    elif mode == "extra":
                        entries.append((".floppy/extra.txt", b"x"))
                    elif mode == "duplicate":
                        entries.append(entries[0])
                    else:
                        entries.append((entries[0][0].upper(), b"x"))
                    data = rebuild(archive_path, entries)
                    manifest = json.loads(
                        manifest_path.read_text(encoding="utf-8")
                    )
                    manifest["archive"]["size"] = len(data)
                    manifest["archive"]["sha256"] = hashlib.sha256(
                        data
                    ).hexdigest()
                    write_integrity(manifest_path, manifest)
                    with self.assertRaises(CLI.CliError):
                        CLI.verify_context_export(
                            archive_path,
                            manifest_path,
                        )

    def test_identity_lifecycle_and_move_portability(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_project(base)
            destination = base / "out"
            destination.mkdir()
            moved = base / "moved"
            moved.mkdir()
            payload = CLI.build_context_export(root, destination)
            archive_path, manifest_path = artifacts(payload)
            moved_archive = moved / archive_path.name
            moved_manifest = moved / manifest_path.name
            shutil.copy2(archive_path, moved_archive)
            shutil.copy2(manifest_path, moved_manifest)
            result = CLI.verify_context_export(
                moved_archive,
                moved_manifest,
            )
            self.assertTrue(result["verified"])
            self.assertEqual(
                result["lifecycle_state"],
                "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE",
            )
            self.assertEqual(
                result["project"]["repository"],
                "owner/project",
            )

    def test_only_destination_artifacts_are_written(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_project(base)
            destination = base / "out"
            destination.mkdir()
            before = {
                path.relative_to(root).as_posix(): hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
                for path in (root / ".floppy").rglob("*")
                if path.is_file()
            }
            CLI.build_context_export(root, destination)
            after = {
                path.relative_to(root).as_posix(): hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
                for path in (root / ".floppy").rglob("*")
                if path.is_file()
            }
            self.assertEqual(before, after)
            self.assertEqual(len(list(destination.iterdir())), 2)

    def test_cli_argument_errors_are_deterministic(self) -> None:
        export = subprocess.run(
            [sys.executable, "-B", str(CLI_PATH), "export"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(export.returncode, 2)
        self.assertEqual(
            export.stderr,
            "ERROR: export requires exactly one destination directory\n",
        )
        verify = subprocess.run(
            [
                sys.executable,
                "-B",
                str(CLI_PATH),
                "verify-export",
                "one",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(verify.returncode, 2)
        self.assertEqual(
            verify.stderr,
            "ERROR: verify-export requires one ZIP and one integrity manifest\n",
        )


# V2_04_EXPORT_INTEGRITY_TEST
class V204ContinuityExportTests(unittest.TestCase):
    def test_context_export_carries_adopted_continuity_and_succession(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root = make_project(base)
            handoffs = root / ".floppy/handoffs"
            handoffs.mkdir(parents=True, exist_ok=True)
            (root / ".floppy/continuity-overseer.json").write_text(
                "{}\n", encoding="utf-8"
            )
            (handoffs / "orchestrator-succession-000001.json").write_text(
                "{}\n", encoding="utf-8"
            )
            git(root, "add", ".floppy")
            git(root, "commit", "-m", "add continuity context")
            destination = base / "out"
            destination.mkdir()
            payload = CLI.build_context_export(root, destination)
            archive_path, _ = artifacts(payload)
            with zipfile.ZipFile(archive_path) as archive:
                self.assertIn(
                    ".floppy/continuity-overseer.json",
                    archive.namelist(),
                )
                self.assertIn(
                    ".floppy/handoffs/orchestrator-succession-000001.json",
                    archive.namelist(),
                )

if __name__ == "__main__":
    unittest.main()
