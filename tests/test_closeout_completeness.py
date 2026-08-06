from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_floppy.py"
CLI_PATH = ROOT / "tools" / "floppyctl.py"


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_floppy_fs05",
        VALIDATOR_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load tools/validate_floppy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CloseoutCompletenessTests(unittest.TestCase):
    def valid_manifest(self) -> dict:
        return {
            "status": "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE",
            "required_read_order": [],
            "system": {
                "source_read_only_during_project_work": True,
                "about": "ABOUT.md",
                "architecture": "BCE \u2014 Bootable Context Environment",
            },
            "floppies": {key: f"Floppy-{key}" for key in "ABCDE"},
            "onboarding": {
                "controller": "onboarding/Floppy_1E.md",
                "implementation_authority": False,
            },
            "roadmap": {
                "machine_readable": ".floppy/roadmap/roadmap.json",
                "user_readable": ".floppy/roadmap/roadmap.md",
            },
            "records": {
                "fs_04_closeout": ".floppy/closeouts/FS-04-closeout.md",
                "fs_05_work_package_draft": (
                    ".floppy/templates/Floppy-E-FS-05.draft.md"
                ),
            },
            "authority": {
                "implementation_authority": "NO_ACTIVE_WORK_AUTHORIZATION",
                "authority_state": "NO_ACTIVE_WORK_AUTHORIZATION",
                "active_implementation_section": None,
                "current_authorized_section": None,
                "last_applied_transition": (
                    "TR-009-APPLY-SECTION-CLOSEOUT"
                ),
            },
            "continuation_point": {
                "active_work_authorization": None,
                "repository_writer": None,
            },
            "active_work_authorization": None,
            "fs_04_work_package": {
                "section": "FS-04",
                "status": "CLOSED",
                "implementation_complete": True,
                "verification_complete": True,
                "administrator_acceptance": "ACCEPTED",
                "implementation_checkpoint": "product-commit",
                "verification_evidence": {"complete_suite": 62},
                "section_closeout": "APPLIED",
                "closeout_applied": True,
                "closeout_application_transition": (
                    "TR-009-APPLY-SECTION-CLOSEOUT"
                ),
                "repository_writer": None,
            },
            "closeout_proposal": {
                "transition": "TR-008-PROPOSE-SECTION-CLOSEOUT",
                "section": "FS-04",
                "status": "APPROVED_AND_APPLIED",
                "record": ".floppy/closeouts/FS-04-closeout.md",
                "proposal_commit_checkpoint": "proposal-commit",
                "fs_05_draft_path": (
                    ".floppy/templates/Floppy-E-FS-05.draft.md"
                ),
                "fs_05_draft_status": "DRAFT_NOT_AUTHORIZED",
                "fs_05": "NOT AUTHORIZED",
            },
            "closeout_application": {
                "transition": "TR-009-APPLY-SECTION-CLOSEOUT",
                "section": "FS-04",
                "approved_proposal_checkpoint": "proposal-commit",
                "status": "APPLIED",
                "resulting_lifecycle_state": (
                    "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE"
                ),
                "record": ".floppy/closeouts/FS-04-closeout.md",
                "application_commit_checkpoint": "application-commit",
                "authority": "NO_ACTIVE_WORK_AUTHORIZATION",
                "active_implementation_section": None,
                "current_authorized_section": None,
                "repository_writer": None,
                "fs_05": "NOT AUTHORIZED",
                "fs_05_draft_path": (
                    ".floppy/templates/Floppy-E-FS-05.draft.md"
                ),
                "fs_05_draft_status": "DRAFT_NOT_AUTHORIZED",
            },
            "fs_05_work_package": {
                "section": "FS-05",
                "status": "DRAFT_NOT_AUTHORIZED",
                "accepted": False,
                "activation_authorized": False,
                "implementation_authorized": False,
                "active": False,
                "authorization_id": None,
                "repository_writer": None,
            },
        }

    def write_project(self, root: Path, manifest: dict) -> None:
        required = [
            ".floppy/START-HERE.md",
            ".floppy/floppies/Floppy-A-HITL.md",
            ".floppy/floppies/Floppy-B-Development-Issues.md",
            ".floppy/floppies/Floppy-C-Project-Baseline.md",
            ".floppy/floppies/Floppy-D-Project-Map.md",
            ".floppy/floppies/Floppy-E-Current-Section.md",
            ".floppy/roadmap/roadmap.md",
            ".floppy/closeouts/FS-04-closeout.md",
            ".floppy/templates/Floppy-E-FS-05.draft.md",
        ]
        for relative in required:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"fixture: {relative}\n", encoding="utf-8")

        roadmap = {
            "current_authorized_section": None,
            "source_controller": {"mutable_in_project": False},
        }
        (root / ".floppy/roadmap/roadmap.json").write_text(
            json.dumps(roadmap, indent=2) + "\n",
            encoding="utf-8",
        )
        (root / ".floppy/manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )

    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(VALIDATOR_PATH),
                str(root),
                "--mode",
                "project",
            ],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def run_cli(self, root: Path) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(CLI_PATH),
                "--root",
                str(root),
                "validate",
                "--mode",
                "project",
            ],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def assert_one(self, manifest: dict, root: Path, expected: str) -> None:
        self.assertEqual(
            [expected],
            VALIDATOR.validate_closeout_completeness(manifest, root),
        )

    def test_complete_accepted_applied_closeout_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.valid_manifest()
            self.write_project(root, manifest)
            self.assertEqual(
                [],
                VALIDATOR.validate_closeout_completeness(manifest, root),
            )
            result = self.run_validator(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_administrator_acceptance_fails_concisely(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.valid_manifest()
            self.write_project(root, manifest)
            manifest["fs_04_work_package"]["administrator_acceptance"] = "PENDING"
            self.assert_one(
                manifest,
                root,
                "CLOSEOUT_ADMINISTRATOR_ACCEPTANCE_MISSING: FS-04",
            )

    def test_missing_implementation_or_verification_evidence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.valid_manifest()
            self.write_project(root, manifest)

            missing_implementation = copy.deepcopy(manifest)
            missing_implementation["fs_04_work_package"].pop(
                "implementation_checkpoint"
            )
            self.assert_one(
                missing_implementation,
                root,
                "CLOSEOUT_IMPLEMENTATION_EVIDENCE_MISSING: FS-04",
            )

            missing_verification = copy.deepcopy(manifest)
            missing_verification["fs_04_work_package"].pop(
                "verification_evidence"
            )
            self.assert_one(
                missing_verification,
                root,
                "CLOSEOUT_VERIFICATION_EVIDENCE_MISSING: FS-04",
            )

    def test_missing_or_inconsistent_proposal_fails_concisely(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.valid_manifest()
            self.write_project(root, manifest)
            manifest["closeout_proposal"].pop("record")
            self.assert_one(
                manifest,
                root,
                "CLOSEOUT_PROPOSAL_INCOMPLETE: FS-04",
            )

    def test_invalid_application_transition_fails_concisely(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.valid_manifest()
            self.write_project(root, manifest)
            manifest["closeout_application"]["transition"] = (
                "TR-008-PROPOSE-SECTION-CLOSEOUT"
            )
            self.assert_one(
                manifest,
                root,
                "CLOSEOUT_APPLICATION_TRANSITION_INVALID: FS-04",
            )

    def test_missing_required_next_draft_fails_concisely(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.valid_manifest()
            self.write_project(root, manifest)
            (root / ".floppy/templates/Floppy-E-FS-05.draft.md").unlink()
            self.assert_one(
                manifest,
                root,
                "CLOSEOUT_NEXT_DRAFT_MISSING: FS-05",
            )

    def test_next_section_must_remain_inactive_unaccepted_unauthorized(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.valid_manifest()
            self.write_project(root, manifest)

            cases = [
                (
                    "active",
                    True,
                    "CLOSEOUT_NEXT_SECTION_ACTIVE: FS-05",
                ),
                (
                    "accepted",
                    True,
                    "CLOSEOUT_NEXT_SECTION_ACCEPTED: FS-05",
                ),
                (
                    "implementation_authorized",
                    True,
                    "CLOSEOUT_NEXT_SECTION_AUTHORIZED: FS-05",
                ),
            ]
            for field, value, expected in cases:
                with self.subTest(field=field):
                    changed = copy.deepcopy(manifest)
                    changed["fs_05_work_package"][field] = value
                    self.assert_one(changed, root, expected)

    def test_active_authorization_after_closeout_fails_concisely(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.valid_manifest()
            self.write_project(root, manifest)
            manifest["active_work_authorization"] = {
                "authorization_id": "FS_05_IMPLEMENTATION"
            }
            self.assert_one(
                manifest,
                root,
                "CLOSEOUT_ACTIVE_AUTHORIZATION_REMAINS: FS-04",
            )

    def test_repository_writer_after_closeout_fails_concisely(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.valid_manifest()
            self.write_project(root, manifest)
            manifest["fs_04_work_package"]["repository_writer"] = (
                "FS_04_WORKING_MODEL"
            )
            self.assert_one(
                manifest,
                root,
                "CLOSEOUT_REPOSITORY_WRITER_REMAINS: FS-04",
            )

    def test_cli_reports_same_result_and_diagnostics_as_validator(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.valid_manifest()
            manifest["fs_04_work_package"]["administrator_acceptance"] = "PENDING"
            self.write_project(root, manifest)
            direct = self.run_validator(root)
            wrapped = self.run_cli(root)
            self.assertNotEqual(direct.returncode, 0)
            self.assertEqual(wrapped.returncode, direct.returncode)
            self.assertEqual(wrapped.stdout, direct.stdout)
            self.assertEqual(wrapped.stderr, direct.stderr)

    def test_validation_performs_no_product_level_writes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.valid_manifest()
            self.write_project(root, manifest)
            watched = [path for path in root.rglob("*") if path.is_file()]
            before = {path: digest(path) for path in watched}
            before_manifest = copy.deepcopy(manifest)

            self.assertEqual(
                [],
                VALIDATOR.validate_closeout_completeness(manifest, root),
            )
            result = self.run_cli(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            self.assertEqual(before_manifest, manifest)
            self.assertEqual(before, {path: digest(path) for path in watched})

    def test_verification_only_no_change_contract(self) -> None:
        record = {"work_package_type": "VERIFICATION_ONLY_NO_REUSABLE_PRODUCT_CHANGE", "implementation_state": "NOT_REQUIRED", "authorization_id": None, "repository_writer": None, "writer_authorization_reference": None, "reusable_product_paths": [], "reusable_product_commits": [], "product_commit": None}
        self.assertEqual(VALIDATOR.validate_verification_only_contract(record), [])


# BEGIN CTRL-02 VERIFICATION-ONLY CLOSEOUT TESTS

class VerificationOnlyCloseoutCompletenessTests(unittest.TestCase):
    def verification_only_manifest(self, *, applied: bool) -> dict:
        record = {
            "section": "FS-10",
            "id": "FS-10",
            "work_package_type": "VERIFICATION_ONLY_NO_REUSABLE_PRODUCT_CHANGE",
            "implementation": "NOT_REQUIRED",
            "implementation_state": "NOT_REQUIRED",
            "implementation_complete": False,
            "verification": "COMPLETE",
            "verification_state": "COMPLETE",
            "verification_complete": True,
            "administrator_acceptance": "ACCEPTED",
            "closeout": "APPLIED" if applied else "PROPOSED",
            "section_closeout": "APPLIED" if applied else "PROPOSED",
            "closeout_applied": applied,
            "reusable_product_paths": [],
            "reusable_product_path_count": 0,
            "reusable_product_commits": [],
            "reusable_product_commit_count": 0,
            "product_commit": None,
            "active_work_authorization": None,
            "active_control_work_authorization": None,
            "active_implementation_authorization": None,
            "active_migration_authorization": None,
            "active_implementation_section": None,
            "current_authorized_section": None,
            "authorization_id": None,
            "repository_writer": None,
            "writer_authorization_reference": None,
            "verification_evidence": {
                "result": "PASSED",
                "verified_checkpoint": "a" * 40,
                "recorded_transition": "TR-017-RECORD-VERIFICATION-ONLY-COMPLETE",
                "complete_repository_tests": {"status": "PASSED", "test_count": 155},
                "source_validator": "PASSED",
                "floppyctl_source_validation": "PASSED",
                "tracked_json": {"status": "PASSED", "file_count": 59},
                "accepted_no_change_findings": {
                    "work_package_type": "VERIFICATION_ONLY_NO_REUSABLE_PRODUCT_CHANGE",
                    "implementation_state": "NOT_REQUIRED",
                    "qualifying_real_migration_paths": 0,
                    "qualifying_real_source_format_fixtures": [],
                    "reusable_product_paths": [],
                    "reusable_product_path_count": 0,
                    "reusable_product_commits": [],
                    "reusable_product_commit_count": 0,
                    "product_commit": None,
                    "real_project_modification": "NOT_PERFORMED",
                    "active_authorization": None,
                    "repository_writer": None,
                    "writer_authorization_reference": None,
                },
            },
        }
        proposal = {
            "section": "FS-10",
            "transition": "TR-019-PROPOSE-VERIFICATION-ONLY-SECTION-CLOSEOUT",
            "status": "APPROVED_AND_APPLIED" if applied else "PROPOSED_NOT_APPLIED",
            "record": ".floppy/closeouts/FS-10-closeout.md",
            "application_status": "APPLIED" if applied else "NOT_APPLIED",
        }
        manifest = {
            "status": "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE" if applied else "LC-VERIFICATION-ONLY-SECTION-ACCEPTED-CLOSEOUT-PROPOSED",
            "active_work_authorization": None,
            "active_control_work_authorization": None,
            "active_implementation_authorization": None,
            "active_migration_authorization": None,
            "active_implementation_section": None,
            "current_authorized_section": None,
            "repository_writer": None,
            "writer_authorization_reference": None,
            "authority": {
                "active_work_authorization": None,
                "active_implementation_authorization": None,
                "active_migration_authorization": None,
                "active_implementation_section": None,
                "current_authorized_section": None,
                "authorization_id": None,
                "repository_writer": None,
                "writer_authorization_reference": None,
            },
            "fs_10_work_package": record,
            "closeout_proposal": proposal,
        }
        if applied:
            manifest["closeout_application"] = {
                "section": "FS-10",
                "transition": "TR-020-APPLY-VERIFICATION-ONLY-SECTION-CLOSEOUT",
                "status": "APPLIED",
                "record": ".floppy/closeouts/FS-10-closeout.md",
                "resulting_lifecycle_state": "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE",
                "fs_11_draft_path": ".floppy/templates/Floppy-E-FS-11.draft.md",
            }
            manifest["fs_11_work_package"] = {
                "section": "FS-11",
                "id": "FS-11",
                "accepted": False,
                "active": False,
                "implementation_authorized": False,
                "authorization_id": None,
                "repository_writer": None,
            }
        return manifest

    def write_verification_only_project(self, root: Path, *, applied: bool) -> dict:
        manifest = self.verification_only_manifest(applied=applied)
        closeout = root / ".floppy/closeouts/FS-10-closeout.md"
        closeout.parent.mkdir(parents=True, exist_ok=True)
        closeout.write_text("fixture: FS-10 closeout\n", encoding="utf-8")
        if applied:
            draft = root / ".floppy/templates/Floppy-E-FS-11.draft.md"
            draft.parent.mkdir(parents=True, exist_ok=True)
            draft.write_text("STATUS: DRAFT_NOT_AUTHORIZED\n", encoding="utf-8")
        return manifest

    def assert_contains(self, manifest: dict, root: Path, expected: str) -> None:
        self.assertIn(expected, VALIDATOR.validate_closeout_completeness(manifest, root))

    def test_verification_only_proposal_not_required_tr019_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.write_verification_only_project(root, applied=False)
            self.assertEqual([], VALIDATOR.validate_closeout_completeness(manifest, root))

    def test_verification_only_application_not_required_tr020_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.write_verification_only_project(root, applied=True)
            self.assertEqual([], VALIDATOR.validate_closeout_completeness(manifest, root))

    def test_verification_only_complete_or_ordinary_evidence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            baseline = self.write_verification_only_project(root, applied=True)
            cases = (
                ("implementation_state", "COMPLETE", "CLOSEOUT_VERIFICATION_ONLY_IMPLEMENTATION_INVALID: FS-10"),
                ("implementation_checkpoint", "b" * 40, "CLOSEOUT_VERIFICATION_ONLY_IMPLEMENTATION_EVIDENCE_FORBIDDEN: FS-10"),
                ("implementation_evidence", {"fabricated": True}, "CLOSEOUT_VERIFICATION_ONLY_IMPLEMENTATION_EVIDENCE_FORBIDDEN: FS-10"),
            )
            for field, value, expected in cases:
                with self.subTest(field=field):
                    manifest = copy.deepcopy(baseline)
                    manifest["fs_10_work_package"][field] = value
                    self.assert_contains(manifest, root, expected)

    def test_verification_only_implementation_complete_true_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.write_verification_only_project(root, applied=True)
            manifest["fs_10_work_package"]["implementation_complete"] = True
            self.assert_contains(manifest, root, "CLOSEOUT_VERIFICATION_ONLY_IMPLEMENTATION_COMPLETE_FORBIDDEN: FS-10")

    def test_verification_only_tr008_proposal_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.write_verification_only_project(root, applied=False)
            manifest["closeout_proposal"]["transition"] = "TR-008-PROPOSE-SECTION-CLOSEOUT"
            self.assert_contains(manifest, root, "CLOSEOUT_PROPOSAL_TRANSITION_INVALID: FS-10")

    def test_verification_only_tr009_application_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.write_verification_only_project(root, applied=True)
            manifest["closeout_application"]["transition"] = "TR-009-APPLY-SECTION-CLOSEOUT"
            self.assert_contains(manifest, root, "CLOSEOUT_APPLICATION_TRANSITION_INVALID: FS-10")

    def test_verification_only_product_scope_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            baseline = self.write_verification_only_project(root, applied=True)
            for field, value in (
                ("reusable_product_paths", ["tools/fabricated.py"]),
                ("reusable_product_commits", ["c" * 40]),
                ("product_commit", "d" * 40),
            ):
                with self.subTest(field=field):
                    manifest = copy.deepcopy(baseline)
                    manifest["fs_10_work_package"][field] = value
                    self.assert_contains(manifest, root, "CLOSEOUT_VERIFICATION_ONLY_PRODUCT_SCOPE_INVALID: FS-10")

    def test_verification_only_validation_performs_no_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = self.write_verification_only_project(root, applied=True)
            before_manifest = json.dumps(manifest, ensure_ascii=False, sort_keys=True)
            before_files = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in sorted(root.rglob("*")) if path.is_file()
            }
            self.assertEqual([], VALIDATOR.validate_closeout_completeness(manifest, root))
            after_manifest = json.dumps(manifest, ensure_ascii=False, sort_keys=True)
            after_files = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in sorted(root.rglob("*")) if path.is_file()
            }
            self.assertEqual(before_manifest, after_manifest)
            self.assertEqual(before_files, after_files)

# END CTRL-02 VERIFICATION-ONLY CLOSEOUT TESTS

if __name__ == "__main__":
    unittest.main()
