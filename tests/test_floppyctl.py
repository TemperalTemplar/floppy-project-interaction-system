from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "floppyctl.py"
VALIDATOR = ROOT / "tools" / "validate_floppy.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FloppyCtlTests(unittest.TestCase):
    def run_cli(
        self,
        *args: str,
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, "-B", str(CLI), *args],
            cwd=cwd or ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def run_validator(
        self,
        target: Path,
        mode: str,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(VALIDATOR),
                str(target),
                "--mode",
                mode,
            ],
            cwd=target,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def fixture(
        self,
        root: Path,
        *,
        active: bool = True,
        traversal: bool = False,
    ) -> dict[Path, bytes]:
        floppy = root / ".floppy"
        roadmap_dir = floppy / "roadmap"
        records_dir = floppy / "records"
        roadmap_dir.mkdir(parents=True)
        records_dir.mkdir(parents=True)

        selected = records_dir / "selected.json"
        selected.write_text(
            '{"record":"selected","value":7}\n',
            encoding="utf-8",
        )
        roadmap = roadmap_dir / "roadmap.json"
        roadmap.write_text(
            json.dumps(
                {
                    "lifecycle_state": (
                        "LC-SECTION-IMPLEMENTATION-IN-PROGRESS"
                        if active
                        else "LC-VERIFICATION-COMPLETE-ACCEPTANCE-PENDING"
                    ),
                    "active_implementation_section": "FS-04" if active else None,
                    "current_authorized_section": "FS-04" if active else None,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        manifest = floppy / "manifest.json"
        record_path = (
            "../../outside.json"
            if traversal
            else ".floppy/records/selected.json"
        )
        manifest.write_text(
            json.dumps(
                {
                    "status": (
                        "LC-SECTION-IMPLEMENTATION-IN-PROGRESS"
                        if active
                        else "LC-VERIFICATION-COMPLETE-ACCEPTANCE-PENDING"
                    ),
                    "authority": {
                        "implementation_authority": (
                            "EXACT_SECTION_IMPLEMENTATION_AUTHORIZATION"
                            if active
                            else "NO_ACTIVE_WORK_AUTHORIZATION"
                        ),
                        "active_implementation_section": "FS-04" if active else None,
                        "current_authorized_section": "FS-04" if active else None,
                    },
                    "active_work_authorization": (
                        {
                            "authorization_id": "FS_04_IMPLEMENTATION",
                            "repository_writer": "FS_04_WORKING_MODEL",
                        }
                        if active
                        else None
                    ),
                    "continuation_point": {
                        "active_work_authorization": None,
                        "repository_writer": None,
                    },
                    "roadmap": {
                        "machine_readable": ".floppy/roadmap/roadmap.json",
                        "user_readable": ".floppy/roadmap/roadmap.md",
                    },
                    "records": {
                        "selected_record": record_path,
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        watched = [manifest, roadmap, selected]
        return {path: path.read_bytes() for path in watched}

    def test_status_reports_lifecycle_and_authority_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            before = self.fixture(root)
            result = self.run_cli("--root", str(root), "status")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                result.stdout.splitlines(),
                [
                    "lifecycle_state=LC-SECTION-IMPLEMENTATION-IN-PROGRESS",
                    "authority=EXACT_SECTION_IMPLEMENTATION_AUTHORIZATION",
                    "active_implementation_section=FS-04",
                    "current_authorized_section=FS-04",
                    "active_authorization=FS_04_IMPLEMENTATION",
                    "repository_writer=FS_04_WORKING_MODEL",
                ],
            )
            self.assertEqual(
                before,
                {path: path.read_bytes() for path in before},
            )

    def test_status_reports_cleared_authority_as_none(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.fixture(root, active=False)
            result = self.run_cli("status", "--root", str(root))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("active_authorization=NONE\n", result.stdout)
            self.assertIn("repository_writer=NONE\n", result.stdout)

    def test_inspect_displays_only_registered_record_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            before = self.fixture(root)
            result = self.run_cli(
                "--root",
                str(root),
                "inspect",
                "selected_record",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                result.stdout,
                '{"record":"selected","value":7}\n',
            )
            self.assertEqual(
                before,
                {path: path.read_bytes() for path in before},
            )

    def test_inspect_rejects_unknown_selection_concisely(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.fixture(root)
            result = self.run_cli(
                "--root",
                str(root),
                "inspect",
                "missing",
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(
                result.stderr,
                "ERROR: unknown registered record: missing\n",
            )

    def test_inspect_rejects_registered_path_outside_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.fixture(root, traversal=True)
            result = self.run_cli(
                "--root",
                str(root),
                "inspect",
                "selected_record",
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(
                result.stderr,
                "ERROR: registered record escapes repository root: "
                "selected_record\n",
            )

    def test_missing_inspect_argument_fails_concisely(self) -> None:
        result = self.run_cli("inspect")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(
            result.stderr,
            "ERROR: inspect requires exactly one registered record\n",
        )

    def test_unknown_command_fails_concisely(self) -> None:
        result = self.run_cli("write")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, "ERROR: unknown command: write\n")

    def test_missing_command_fails_concisely(self) -> None:
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(
            result.stderr,
            "ERROR: command is required: status, validate, inspect, or initialize\n",
        )

    def test_initialize_dry_run_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "project"
            target.mkdir()
            result = self.run_cli(
                "initialize",
                "--target",
                str(target),
                "--project-name",
                "CLI Project",
                "--source-repository",
                "owner/floppy-source",
                "--dry-run",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DRY RUN: no files changed", result.stdout)
            self.assertIn("lifecycle-state.json", result.stdout)
            self.assertFalse((target / ".floppy").exists())

    def test_initialize_provisions_and_validates_project(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "project"
            target.mkdir()
            result = self.run_cli(
                "initialize",
                "--target",
                str(target),
                "--project-name",
                "CLI Project",
                "--source-repository",
                "owner/floppy-source",
                "--project-repository",
                "owner/project",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((target / ".floppy/lifecycle-state.json").is_file())
            manifest = json.loads(
                (target / ".floppy/manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                manifest["control_state"]["repository"],
                "owner/project",
            )
            validation = self.run_cli(
                "--root",
                str(target),
                "validate",
                "--mode",
                "project",
            )
            self.assertEqual(
                validation.returncode,
                0,
                validation.stdout + validation.stderr,
            )

    def test_initialize_requires_target_and_project_name(self) -> None:
        missing_target = self.run_cli(
            "initialize",
            "--project-name",
            "Project",
        )
        self.assertEqual(missing_target.returncode, 2)
        self.assertEqual(
            missing_target.stderr,
            "ERROR: initialize requires --target\n",
        )
        with tempfile.TemporaryDirectory() as td:
            missing_name = self.run_cli(
                "initialize",
                "--target",
                td,
            )
            self.assertEqual(missing_name.returncode, 2)
            self.assertEqual(
                missing_name.stderr,
                "ERROR: initialize requires --project-name\n",
            )

    def test_initialize_refuses_existing_control_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "project"
            target.mkdir()
            (target / ".floppy").mkdir()
            result = self.run_cli(
                "initialize",
                "--target",
                str(target),
                "--project-name",
                "Project",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("destination already exists", result.stderr)

    def test_status_rejects_arguments_concisely(self) -> None:
        result = self.run_cli("status", "extra")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(
            result.stderr,
            "ERROR: status accepts no arguments\n",
        )

    def test_validate_preserves_source_validator_result_and_diagnostics(
        self,
    ) -> None:
        self.assertFalse((ROOT / ".floppy").exists())
        watched = [
            ROOT / "VERSION",
            ROOT / "system-manifest.json",
            ROOT / "project-seed" / ".floppy" / "manifest.json",
            ROOT / "project-seed" / ".floppy" / "roadmap" / "roadmap.json",
            VALIDATOR,
            CLI,
        ]
        before = {path: digest(path) for path in watched}
        direct = self.run_validator(ROOT, "source")
        wrapped = self.run_cli(
            "--root",
            str(ROOT),
            "validate",
            "--mode",
            "source",
        )
        self.assertEqual(wrapped.returncode, direct.returncode)
        self.assertEqual(wrapped.stdout, direct.stdout)
        self.assertEqual(wrapped.stderr, direct.stderr)
        self.assertEqual(
            before,
            {path: digest(path) for path in watched},
        )
        self.assertFalse((ROOT / ".floppy").exists())

    def test_validate_preserves_failure_result_and_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            direct = self.run_validator(target, "project")
            wrapped = self.run_cli(
                "--root",
                str(target),
                "validate",
                "--mode",
                "project",
            )
            self.assertNotEqual(direct.returncode, 0)
            self.assertEqual(wrapped.returncode, direct.returncode)
            self.assertEqual(wrapped.stdout, direct.stdout)
            self.assertEqual(wrapped.stderr, direct.stderr)

    def test_validate_rejects_invalid_mode_concisely(self) -> None:
        result = self.run_cli("validate", "--mode", "other")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(
            result.stderr,
            "ERROR: invalid validation mode: other\n",
        )

    def test_validate_rejects_unrecognized_arguments(self) -> None:
        result = self.run_cli("validate", "--other")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(
            result.stderr,
            "ERROR: validate accepts only --mode source|project\n",
        )


if __name__ == "__main__":
    unittest.main()
