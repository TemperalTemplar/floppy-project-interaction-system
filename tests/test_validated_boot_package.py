
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "tools" / "floppyctl.py"
VALIDATOR_PATH = ROOT / "tools" / "validate_floppy.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("floppyctl_fs08", CLI_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load tools/floppyctl.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CLI = load_cli()


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_floppy_pre_tr021_followup",
        VALIDATOR_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load tools/validate_floppy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()

EXPECTED_BOOT_PACKAGE_PATHS = (
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
    "specs/v2-architecture-compatibility.md",
    "specs/v2-compatibility-profile.json",
    "system-manifest.json",
    "tools/floppyctl.py",
    "tools/initialize_project.py",
    "tools/validate_floppy.py",
)


def digest_tree(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = "symlink:" + os.readlink(path)
        elif path.is_file():
            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif path.is_dir():
            result[relative] = "directory"
    return result


def git(root: Path, *args: str) -> str:
    environment = os.environ.copy()
    if args and args[0] == "commit":
        environment["GIT_AUTHOR_DATE"] = "2000-01-01T00:00:00+00:00"
        environment["GIT_COMMITTER_DATE"] = "2000-01-01T00:00:00+00:00"
    completed = subprocess.run(
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
        env=environment,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stdout + completed.stderr)
    return completed.stdout.strip()


def make_repo(base: Path, files: dict[str, bytes] | None = None) -> Path:
    root = base / "repo"
    root.mkdir()
    selected = files or {
        "alpha.txt": b"alpha",
        "nested/beta.txt": b"beta",
    }
    for relative, data in selected.items():
        path = root.joinpath(*relative.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (root / "VERSION").write_text("1.2.3-dev\n", encoding="utf-8")
    git(root, "init")
    git(root, "config", "user.email", "fs08@example.invalid")
    git(root, "config", "user.name", "FS08 Tests")
    git(root, "add", ".")
    git(root, "commit", "-m", "fixture")
    return root


SMALL_INVENTORY = ("VERSION", "alpha.txt", "nested/beta.txt")


def build_small(root: Path, destination: Path):
    with mock.patch.object(
        CLI,
        "BOOT_PACKAGE_FILE_PATHS",
        SMALL_INVENTORY,
    ):
        return CLI.build_boot_package(root, destination)


def verify_small(archive_path: Path, manifest_path: Path):
    with mock.patch.object(
        CLI,
        "BOOT_PACKAGE_FILE_PATHS",
        SMALL_INVENTORY,
    ):
        return CLI.verify_boot_package(archive_path, manifest_path)


def verify_paths(payload: dict):
    return (
        Path(payload["archive"]["path"]),
        Path(payload["manifest"]["path"]),
    )


def write_manifest(path: Path, value: dict) -> None:
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


def rebuild_archive(
    path: Path,
    entries: list[tuple[str, bytes]],
    *,
    mutate_metadata: bool = False,
) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, data in entries:
            info = zipfile.ZipInfo(
                name,
                (1981, 1, 1, 0, 0, 0)
                if mutate_metadata
                else CLI.BOOT_PACKAGE_FIXED_TIMESTAMP,
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


def update_archive_record(manifest_path: Path, archive_bytes: bytes) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["archive"]["size"] = len(archive_bytes)
    manifest["archive"]["sha256"] = hashlib.sha256(archive_bytes).hexdigest()
    write_manifest(manifest_path, manifest)
    return manifest


class ValidatedBootPackageTests(unittest.TestCase):
    def test_project_lifecycle_state_is_in_validated_boot_inventory(self) -> None:
        self.assertIn(
            "project-seed/.floppy/lifecycle-state.json",
            CLI.BOOT_PACKAGE_FILE_PATHS,
        )

    def test_explicit_inventory_matches_source_boundary(self) -> None:
        self.assertEqual(CLI.BOOT_PACKAGE_FILE_PATHS, EXPECTED_BOOT_PACKAGE_PATHS)
        self.assertEqual(
            list(CLI.BOOT_PACKAGE_FILE_PATHS),
            sorted(CLI.BOOT_PACKAGE_FILE_PATHS),
        )
        self.assertEqual(len(CLI.BOOT_PACKAGE_FILE_PATHS), 52)
        for relative in CLI.BOOT_PACKAGE_FILE_PATHS:
            self.assertTrue((ROOT / relative).is_file(), relative)
            self.assertNotEqual(relative, ".gitignore")
            self.assertFalse(relative.startswith((".floppy/", "legacy/", "tests/")))

    def test_unapproved_repository_content_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_repo(Path(td))
            unexpected = root / "unexpected.txt"
            unexpected.write_text("no", encoding="utf-8")
            git(root, "add", "unexpected.txt")
            git(root, "commit", "-m", "unexpected")
            with mock.patch.object(
                CLI,
                "BOOT_PACKAGE_FILE_PATHS",
                ("VERSION", "alpha.txt", "nested/beta.txt"),
            ):
                with self.assertRaisesRegex(
                    CLI.CliError,
                    "^unexpected package source content: unexpected.txt$",
                ):
                    CLI.build_boot_package(root, Path(td))

    def test_stable_ordering_forward_slashes_and_nested_content(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_repo(Path(td))
            payload = build_small(root, Path(td))
            archive_path, manifest_path = verify_paths(payload)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            paths = [entry["path"] for entry in manifest["entries"]]
            self.assertEqual(paths, ["VERSION", "alpha.txt", "nested/beta.txt"])
            self.assertTrue(all("\\" not in path for path in paths))
            with zipfile.ZipFile(archive_path) as archive:
                self.assertEqual(archive.namelist(), paths)

    def test_build_is_independent_of_current_working_directory(self) -> None:
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as other:
            root = make_repo(Path(td))
            first = Path(td) / "first"
            second = Path(td) / "second"
            first.mkdir()
            second.mkdir()
            old = Path.cwd()
            try:
                os.chdir(root)
                a = build_small(root, first)
                os.chdir(other)
                b = build_small(root, second)
            finally:
                os.chdir(old)
            self.assertEqual(
                Path(a["archive"]["path"]).read_bytes(),
                Path(b["archive"]["path"]).read_bytes(),
            )
            self.assertEqual(
                Path(a["manifest"]["path"]).read_bytes(),
                Path(b["manifest"]["path"]).read_bytes(),
            )

    def test_build_is_independent_of_absolute_checkout_location(self) -> None:
        with tempfile.TemporaryDirectory() as a_td, tempfile.TemporaryDirectory() as b_td:
            first = make_repo(Path(a_td))
            second = make_repo(Path(b_td))
            a = build_small(first, Path(a_td))
            b = build_small(second, Path(b_td))
            self.assertEqual(git(first, "rev-parse", "HEAD"), git(second, "rev-parse", "HEAD"))
            self.assertEqual(
                Path(a["archive"]["path"]).read_bytes(),
                Path(b["archive"]["path"]).read_bytes(),
            )
            self.assertEqual(
                Path(a["manifest"]["path"]).read_bytes(),
                Path(b["manifest"]["path"]).read_bytes(),
            )

    def test_archive_metadata_is_fixed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_repo(Path(td))
            payload = build_small(root, Path(td))
            archive_path, _ = verify_paths(payload)
            with zipfile.ZipFile(archive_path) as archive:
                self.assertEqual(archive.comment, b"")
                for info in archive.infolist():
                    self.assertEqual(info.date_time, CLI.BOOT_PACKAGE_FIXED_TIMESTAMP)
                    self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
                    self.assertEqual(info.create_system, 3)
                    self.assertEqual(info.external_attr, CLI.BOOT_PACKAGE_EXTERNAL_ATTR)
                    self.assertEqual(info.comment, b"")
                    self.assertEqual(info.extra, b"")
                    self.assertEqual(info.flag_bits, 0)

    def test_repeated_builds_are_byte_identical_and_reused(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_repo(Path(td))
            first = build_small(root, Path(td))
            archive_path, manifest_path = verify_paths(first)
            archive_bytes = archive_path.read_bytes()
            manifest_bytes = manifest_path.read_bytes()
            second = build_small(root, Path(td))
            self.assertEqual(second["archive"]["state"], "reused")
            self.assertEqual(second["manifest"]["state"], "reused")
            self.assertEqual(archive_path.read_bytes(), archive_bytes)
            self.assertEqual(manifest_path.read_bytes(), manifest_bytes)

    def test_empty_and_invalid_inventory_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_repo(Path(td))
            with mock.patch.object(CLI, "BOOT_PACKAGE_FILE_PATHS", ()):
                with self.assertRaisesRegex(CLI.CliError, "inventory is empty"):
                    CLI.build_boot_package(root, Path(td))
            with mock.patch.object(
                CLI,
                "BOOT_PACKAGE_FILE_PATHS",
                ("VERSION", "../escape"),
            ):
                with self.assertRaises(CLI.CliError):
                    CLI.build_boot_package(root, Path(td))

    def test_unsafe_absolute_drive_duplicate_and_case_paths_are_rejected(self) -> None:
        unsafe = ("../x", "/x", r"C:\x", "C:/x", r"\\server\share\x", "a\\b", "name:stream")
        for value in unsafe:
            with self.subTest(value=value):
                with self.assertRaises(CLI.CliError):
                    CLI._validated_archive_path(value)
        with self.assertRaisesRegex(CLI.CliError, "duplicate logical scan path"):
            CLI._finalize_scan_entries(
                [{"path": "a", "type": "file"}, {"path": "a", "type": "file"}]
            )
        with self.assertRaisesRegex(CLI.CliError, "case collision"):
            CLI._finalize_scan_entries(
                [{"path": "A", "type": "file"}, {"path": "a", "type": "file"}]
            )

    def test_symlink_or_reparse_point_is_rejected_where_supported(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_repo(Path(td))
            outside = Path(td) / "outside.txt"
            outside.write_text("secret", encoding="utf-8")
            link = root / "linked.txt"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            git(root, "add", "linked.txt")
            git(root, "commit", "-m", "linked")
            with mock.patch.object(
                CLI,
                "BOOT_PACKAGE_FILE_PATHS",
                ("VERSION", "alpha.txt", "nested/beta.txt"),
            ):
                with self.assertRaisesRegex(
                    CLI.CliError,
                    "unsafe scan link or reparse point",
                ):
                    CLI.build_boot_package(root, Path(td))

    def test_archive_and_per_entry_sha256_verify(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_repo(Path(td))
            payload = build_small(root, Path(td))
            archive_path, manifest_path = verify_paths(payload)
            result = verify_small(archive_path, manifest_path)
            self.assertTrue(result["verified"])
            self.assertEqual(result["entries"], 3)

    def test_modified_zip_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_repo(Path(td))
            payload = build_small(root, Path(td))
            archive_path, manifest_path = verify_paths(payload)
            archive_path.write_bytes(archive_path.read_bytes() + b"x")
            with self.assertRaisesRegex(CLI.CliError, "archive (size|SHA-256) mismatch"):
                verify_small(archive_path, manifest_path)

    def test_noncanonical_manifest_serialization_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_repo(Path(td))
            payload = build_small(root, Path(td))
            archive_path, manifest_path = verify_paths(payload)
            manifest_path.write_bytes(manifest_path.read_bytes() + b" ")
            with self.assertRaisesRegex(
                CLI.CliError,
                "serialization is not deterministic",
            ):
                verify_small(archive_path, manifest_path)

    def test_modified_manifest_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_repo(Path(td))
            payload = build_small(root, Path(td))
            archive_path, manifest_path = verify_paths(payload)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["entries"][0]["sha256"] = "0" * 64
            write_manifest(manifest_path, manifest)
            with self.assertRaisesRegex(CLI.CliError, "member SHA-256 mismatch"):
                verify_small(archive_path, manifest_path)

    def test_missing_and_extra_members_are_rejected(self) -> None:
        for mode in ("missing", "extra"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as td:
                root = make_repo(Path(td))
                payload = build_small(root, Path(td))
                archive_path, manifest_path = verify_paths(payload)
                entries = [
                    ("VERSION", b"1.2.3-dev\n"),
                    ("alpha.txt", b"alpha"),
                    ("nested/beta.txt", b"beta"),
                ]
                if mode == "missing":
                    entries.pop()
                else:
                    entries.append(("extra.txt", b"extra"))
                data = rebuild_archive(archive_path, entries)
                update_archive_record(manifest_path, data)
                expected = "missing" if mode == "missing" else "unexpected"
                with self.assertRaisesRegex(CLI.CliError, f"archive member is {expected}"):
                    verify_small(archive_path, manifest_path)

    def test_duplicate_case_collision_and_unsafe_archive_entries_are_rejected(self) -> None:
        cases = {
            "duplicate": [("VERSION", b"1"), ("VERSION", b"2")],
            "case": [("VERSION", b"1"), ("version", b"2")],
            "unsafe": [("../escape", b"x")],
        }
        for label, entries in cases.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as td:
                root = make_repo(Path(td))
                payload = build_small(root, Path(td))
                archive_path, manifest_path = verify_paths(payload)
                data = rebuild_archive(archive_path, entries)
                update_archive_record(manifest_path, data)
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest["entries"] = [
                    {
                        "path": name,
                        "size": len(data_value),
                        "sha256": hashlib.sha256(data_value).hexdigest(),
                    }
                    for name, data_value in entries
                ]
                write_manifest(manifest_path, manifest)
                with self.assertRaises(CLI.CliError):
                    verify_small(archive_path, manifest_path)

    def test_modified_metadata_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_repo(Path(td))
            payload = build_small(root, Path(td))
            archive_path, manifest_path = verify_paths(payload)
            entries = [
                ("VERSION", b"1.2.3-dev\n"),
                ("alpha.txt", b"alpha"),
                ("nested/beta.txt", b"beta"),
            ]
            data = rebuild_archive(archive_path, entries, mutate_metadata=True)
            update_archive_record(manifest_path, data)
            with self.assertRaisesRegex(CLI.CliError, "timestamp mismatch"):
                verify_small(archive_path, manifest_path)

    def test_artifact_count_is_exactly_one_zip_and_one_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_repo(Path(td))
            build_small(root, Path(td))
            artifacts = sorted(
                path.name
                for path in Path(td).iterdir()
                if path.is_file()
            )
            self.assertEqual(
                len([name for name in artifacts if name.endswith(".zip")]),
                1,
            )
            self.assertEqual(
                len(
                    [
                        name
                        for name in artifacts
                        if name.endswith(".checksums.json")
                    ]
                ),
                1,
            )

    def test_source_files_remain_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_repo(Path(td))
            before = digest_tree(root)
            payload = build_small(root, Path(td))
            archive_path, manifest_path = verify_paths(payload)
            verify_small(archive_path, manifest_path)
            after = digest_tree(root)
            self.assertEqual(before, after)

    def test_differing_artifact_collision_is_rejected_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = make_repo(Path(td))
            payload = build_small(root, Path(td))
            archive_path, _ = verify_paths(payload)
            archive_path.write_bytes(b"collision")
            with self.assertRaisesRegex(CLI.CliError, "artifact collision differs"):
                build_small(root, Path(td))
            self.assertEqual(archive_path.read_bytes(), b"collision")

    def test_existing_fs07_scan_behavior_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "nested").mkdir()
            (root / "alpha.txt").write_text("a", encoding="utf-8")
            (root / "nested" / "beta.txt").write_text("b", encoding="utf-8")
            entries = CLI.scan_package_content(root, root)
            self.assertEqual(
                entries,
                [
                    {"path": "alpha.txt", "type": "file"},
                    {"path": "nested", "type": "directory"},
                    {"path": "nested/beta.txt", "type": "file"},
                ],
            )

class HistoricalOperationEvidenceTests(unittest.TestCase):
    BRANCH_PREFIX = "pre-tr021-historical-evidence"

    @staticmethod
    def operation_evidence(operation: str) -> dict:
        return {
            "operation": operation,
            "section": "FS-13",
            "implementation_scope_exercised": False,
            "exact_control_paths": [".floppy/manifest.json"],
            "transition_sequence": [],
        }

    def make_integrity_repo(
        self,
        evidence: dict | None,
    ) -> tuple[tempfile.TemporaryDirectory[str], Path, dict, str]:
        td = tempfile.TemporaryDirectory()
        root = Path(td.name) / "repo"
        root.mkdir()
        git(root, "init")
        git(root, "config", "user.email", "pre-tr021@example.invalid")
        git(root, "config", "user.name", "PRE-TR021 Tests")
        branch = git(root, "branch", "--show-current")
        manifest = {
            "status": "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE",
            "active_work_authorization": None,
            "repository_writer": None,
            "writer_authorization_reference": None,
            "continuation_point": {
                "active_work_authorization": None,
                "repository_writer": None,
                "writer_authorization_reference": None,
            },
            "authority": {
                "active_implementation_section": None,
                "repository_writer": None,
                "writer_authorization_reference": None,
            },
            "fs_13_work_package": {
                "id": "FS-13",
                "section": "FS-13",
                "path": ".floppy/templates/Floppy-E-FS-13.draft.md",
                "branch": branch,
            },
        }
        if evidence is not None:
            manifest["git_integrity_operation"] = evidence
        manifest_path = root / ".floppy" / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        write_manifest(manifest_path, manifest)
        git(root, "add", "--", ".")
        git(root, "commit", "-m", "baseline")
        return td, root, manifest, branch

    def validate(
        self,
        root: Path,
        manifest: dict,
        environment: dict[str, str] | None = None,
    ) -> list[str]:
        return VALIDATOR.validate_authorization_git_integrity(
            root,
            manifest,
            {} if environment is None else environment,
        )

    def test_historical_unchanged_operation_evidence_does_not_replay(self) -> None:
        evidence = self.operation_evidence("CLOSEOUT_PROPOSAL_CONTROL")
        td, root, manifest, _ = self.make_integrity_repo(evidence)
        with td:
            (root / "unrelated-product.txt").write_text(
                "unrelated product change\n",
                encoding="utf-8",
            )
            self.assertEqual([], self.validate(root, manifest))

    def test_new_operation_evidence_is_still_validated(self) -> None:
        td, root, manifest, _ = self.make_integrity_repo(None)
        with td:
            candidate = json.loads(json.dumps(manifest))
            candidate["git_integrity_operation"] = self.operation_evidence(
                "CLOSEOUT_PROPOSAL_CONTROL"
            )
            write_manifest(root / ".floppy" / "manifest.json", candidate)
            errors = self.validate(root, candidate)
            self.assertIn("GIT_INTEGRITY_EXPECTED_HEAD_MISSING", errors)

    def test_changed_operation_evidence_is_still_validated(self) -> None:
        original = self.operation_evidence("CLOSEOUT_PROPOSAL_CONTROL")
        td, root, manifest, _ = self.make_integrity_repo(original)
        with td:
            candidate = json.loads(json.dumps(manifest))
            candidate["git_integrity_operation"] = self.operation_evidence(
                "CLOSEOUT_APPLICATION_CONTROL"
            )
            write_manifest(root / ".floppy" / "manifest.json", candidate)
            errors = self.validate(root, candidate)
            self.assertIn("GIT_INTEGRITY_EXPECTED_HEAD_MISSING", errors)

    def test_explicit_control_operation_overrides_historical_evidence(self) -> None:
        evidence = self.operation_evidence("CLOSEOUT_PROPOSAL_CONTROL")
        td, root, manifest, branch = self.make_integrity_repo(evidence)
        with td:
            head = git(root, "rev-parse", "HEAD")
            errors = self.validate(
                root,
                manifest,
                {
                    "FLOPPY_CONTROL_OPERATION": "CLOSEOUT_APPLICATION_CONTROL",
                    "FLOPPY_CONTROL_BRANCH": branch,
                    "FLOPPY_EXPECTED_HEAD": head,
                },
            )
            self.assertIn("GIT_INTEGRITY_CONTROL_OPERATION_MISMATCH", errors)

    def test_explicit_operation_missing_required_head_still_fails(self) -> None:
        evidence = self.operation_evidence("CLOSEOUT_PROPOSAL_CONTROL")
        td, root, manifest, branch = self.make_integrity_repo(evidence)
        with td:
            errors = self.validate(
                root,
                manifest,
                {
                    "FLOPPY_CONTROL_OPERATION": "CLOSEOUT_APPLICATION_CONTROL",
                    "FLOPPY_CONTROL_BRANCH": branch,
                },
            )
            self.assertIn("GIT_INTEGRITY_EXPECTED_HEAD_MISSING", errors)

    def test_git_trust_is_process_local_only(self) -> None:
        import inspect

        helper_source = inspect.getsource(git)
        self.assertIn(
            'f"safe.directory={root.as_posix()}"',
            helper_source,
        )
        self.assertNotIn("--global", helper_source)
        self.assertNotIn("safe.directory=*", helper_source)



if __name__ == "__main__":
    unittest.main()
