#!/usr/bin/env python3
"""Focused FS-09 tests for the accepted single-transition lifecycle writer."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "floppyctl.py"
SPEC = importlib.util.spec_from_file_location("fs09_floppyctl_under_test", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
FLOPPYCTL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FLOPPYCTL)

TRANSITION = "TR-004-START-SECTION-IMPLEMENTATION"
AUTHORIZATION = "FIXTURE_SECTION_IMPLEMENTATION"
WRITER = "FIXTURE_WORKING_MODEL"
REPOSITORY = "example/disposable-fixture"
SOURCE_VERSION = "0.4.1-dev"
TARGET = ".floppy/lifecycle-state.json"

SOURCE_DIMENSIONS = {
    "roadmap": "ACCEPTED",
    "work_package": "ACCEPTED_PLANNING_BASELINE",
    "authority": "EXACT_SECTION_IMPLEMENTATION_AUTHORIZATION",
    "implementation": "NOT_STARTED",
    "verification": "NOT_STARTED",
    "acceptance": "PENDING",
    "closeout": "NOT_PROPOSED",
    "migration": "NONE",
    "final_closure": "OPEN",
}


def canonical(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def run_git(root: Path, *arguments: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={root}", "-C", str(root), *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    return result.stdout.strip()


class Fixture:
    def __init__(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "fixture"
        self.root.mkdir()
        run_git(self.root, "init", "-b", "main")
        run_git(self.root, "config", "user.name", "FS09 Fixture")
        run_git(self.root, "config", "user.email", "fs09@example.invalid")
        (self.root / "VERSION").write_text(SOURCE_VERSION + "\n", encoding="utf-8", newline="\n")
        (self.root / "base.txt").write_text("base\n", encoding="utf-8", newline="\n")
        run_git(self.root, "add", "--", "VERSION", "base.txt")
        run_git(self.root, "commit", "-m", "fixture base")
        self.base = run_git(self.root, "rev-parse", "HEAD")
        self._write_records()
        run_git(self.root, "add", "--all")
        run_git(self.root, "commit", "-m", "fixture authorized state")
        self.refresh()

    def refresh(self) -> None:
        self.branch = run_git(self.root, "branch", "--show-current")
        self.head = run_git(self.root, "rev-parse", "HEAD")

    def _authorization(self) -> dict[str, Any]:
        return {
            "authorization_id": AUTHORIZATION,
            "authorization_kind": "section_implementation",
            "section": "FS-42",
            "human_authority": {
                "actor": "ADMINISTRATOR",
                "decision": "Authorize disposable TR-004 fixture testing.",
                "issued_explicitly": True,
            },
            "repository": REPOSITORY,
            "base_checkpoint": self.base,
            "source_version": SOURCE_VERSION,
            "branch": "main",
            "worktree": str(self.root.resolve()),
            "exact_file_scope": [TARGET],
            "required_validation": ["focused FS-09 tests"],
            "commit_sequence": [
                {
                    "id": "P1",
                    "message": "fixture-only",
                    "path_class": "reusable_product",
                }
            ],
            "push_boundary": {
                "permitted": False,
                "branch": None,
                "force_push": False,
            },
            "forbidden_side_effects": ["real_project_write"],
            "administrator_acceptance": "PENDING",
            "section_closeout": "NOT AUTHORIZED",
            "integration": "NOT AUTHORIZED",
            "later_section_authority": "NOT AUTHORIZED",
        }

    def _write_records(self) -> None:
        floppy = self.root / ".floppy"
        floppy.mkdir()
        manifest = {
            "format_version": 1,
            "project_name": "Disposable FS-09 Fixture",
            "repository": REPOSITORY,
            "source_version": SOURCE_VERSION,
            "system": {
                "source_repository": REPOSITORY,
                "source_version": SOURCE_VERSION,
            },
            "active_work_authorization": self._authorization(),
        }
        registry = {
            "format_version": 1,
            "artifact": "project-orchestrator-registry",
            "current_assignments": {
                "current_orchestrator": "PROJECT_ORCHESTRATOR",
                "current_section_working_model": WRITER,
                "repository_writer": WRITER,
                "writer_authorization_reference": AUTHORIZATION,
            },
        }
        state = {
            "state_id": "LC-SECTION-AUTHORIZED-NOT-STARTED",
            "section": "FS-42",
            "authorization_id": AUTHORIZATION,
            "base_checkpoint": self.base,
            "dimensions": SOURCE_DIMENSIONS,
            "active_implementation_sections": ["FS-42"],
            "evidence": [f"AUTHORIZATION:{AUTHORIZATION}"],
        }
        (floppy / "manifest.json").write_bytes(canonical(manifest))
        (floppy / "orchestrator-registry.json").write_bytes(canonical(registry))
        (floppy / "lifecycle-state.json").write_bytes(canonical(state))
        (floppy / "unrelated.txt").write_text("unchanged\n", encoding="utf-8", newline="\n")

    @property
    def target(self) -> Path:
        return self.root / TARGET

    @property
    def manifest(self) -> Path:
        return self.root / ".floppy/manifest.json"

    @property
    def registry(self) -> Path:
        return self.root / ".floppy/orchestrator-registry.json"

    def json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def commit_json_change(self, path: Path, value: dict[str, Any], message: str = "fixture mutation") -> None:
        path.write_bytes(canonical(value))
        run_git(self.root, "add", "--", str(path.relative_to(self.root)))
        run_git(self.root, "commit", "-m", message)
        self.refresh()

    def plan(self) -> dict[str, Any]:
        return FLOPPYCTL._fs09_operation(
            self.root,
            mode="dry-run",
            transition=TRANSITION,
            authorization_reference=AUTHORIZATION,
            repository_writer=WRITER,
            expected_branch=self.branch,
            expected_head=self.head,
        )

    def apply(self, plan: dict[str, Any]) -> dict[str, Any]:
        return FLOPPYCTL._fs09_operation(
            self.root,
            mode="apply",
            transition=TRANSITION,
            authorization_reference=AUTHORIZATION,
            repository_writer=WRITER,
            expected_branch=self.branch,
            expected_head=self.head,
            plan_sha256=plan["plan_sha256"],
        )

    def close(self) -> None:
        FLOPPYCTL._FS09_TEST_HOOK = None
        self.temp.cleanup()


class FS09ControlledLifecycleWritesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = Fixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def assert_rejected(self, function: Any, fragment: str | None = None) -> str:
        with self.assertRaises(FLOPPYCTL.CliError) as caught:
            function()
        message = str(caught.exception)
        if fragment:
            self.assertIn(fragment, message)
        return message

    def test_contract_is_accepted_normative_and_traceable(self) -> None:
        contract_path = ROOT / "specs/lifecycle-write-contract.json"
        raw = contract_path.read_bytes()
        contract = json.loads(raw)
        self.assertEqual(raw, canonical(contract))
        self.assertEqual(contract["status"], "ACCEPTED_NORMATIVE")
        self.assertEqual(
            contract["accepted_design_proposal_sha256"],
            "6a221e89ac49dd1478906a8c80a26c99e0d9f5037384b3bca9dc225ffdb83b41",
        )
        self.assertEqual(
            [item["transition_id"] for item in contract["supported_transitions"]],
            [TRANSITION],
        )

    def test_dry_run_is_deterministic_and_writes_nothing(self) -> None:
        target_before = self.fixture.target.read_bytes()
        stat_before = self.fixture.target.stat()
        status_before = run_git(self.fixture.root, "status", "--porcelain=v1", "--untracked-files=all")
        first = self.fixture.plan()
        second = self.fixture.plan()
        self.assertEqual(first, second)
        self.assertEqual(first["operation_mode"], "DRY_RUN")
        self.assertFalse(first["applied"])
        self.assertEqual(first["exact_target_path"], TARGET)
        self.assertEqual(first["operation"], "REPLACE")
        self.assertEqual(self.fixture.target.read_bytes(), target_before)
        stat_after = self.fixture.target.stat()
        self.assertEqual(stat_before.st_mtime_ns, stat_after.st_mtime_ns)
        self.assertEqual(stat_before.st_size, stat_after.st_size)
        self.assertEqual(
            run_git(self.fixture.root, "status", "--porcelain=v1", "--untracked-files=all"),
            status_before,
        )
        self.assertFalse(any(".fs09-" in child.name for child in self.fixture.target.parent.iterdir()))

    def test_apply_replaces_exact_state_only(self) -> None:
        unrelated = (self.fixture.root / ".floppy/unrelated.txt").read_bytes()
        manifest = self.fixture.manifest.read_bytes()
        registry = self.fixture.registry.read_bytes()
        plan = self.fixture.plan()
        result = self.fixture.apply(plan)
        self.assertTrue(result["applied"])
        state = json.loads(self.fixture.target.read_text(encoding="utf-8"))
        self.assertEqual(state["state_id"], "LC-SECTION-IMPLEMENTATION-IN-PROGRESS")
        self.assertEqual(state["dimensions"]["implementation"], "IN_PROGRESS")
        self.assertEqual((self.fixture.root / ".floppy/unrelated.txt").read_bytes(), unrelated)
        self.assertEqual(self.fixture.manifest.read_bytes(), manifest)
        self.assertEqual(self.fixture.registry.read_bytes(), registry)
        self.assertEqual(run_git(self.fixture.root, "diff", "--cached", "--name-only"), "")
        self.assertEqual(run_git(self.fixture.root, "diff", "--name-only"), TARGET)

    def test_only_tr004_is_supported(self) -> None:
        self.assert_rejected(
            lambda: FLOPPYCTL._fs09_operation(
                self.fixture.root,
                mode="dry-run",
                transition="TR-005-RECORD-IMPLEMENTATION-COMPLETE",
                authorization_reference=AUTHORIZATION,
                repository_writer=WRITER,
                expected_branch=self.fixture.branch,
                expected_head=self.fixture.head,
            ),
            "unsupported lifecycle transition",
        )

    def test_caller_supplied_write_interfaces_are_rejected(self) -> None:
        prohibited = (
            "--path", "--json-pointer", "--patch", "--replacement-document",
            "--replacement-bytes",
        )
        common = [
            "--root", str(self.fixture.root), "lifecycle-write",
            "--mode", "dry-run", "--transition", TRANSITION,
            "--authorization-reference", AUTHORIZATION,
            "--repository-writer", WRITER,
            "--expected-branch", self.fixture.branch,
            "--expected-head", self.fixture.head,
        ]
        for option in prohibited:
            with self.subTest(option=option):
                with self.assertRaises(SystemExit):
                    FLOPPYCTL._fs09_parse_cli([*common, option, "x"])

    def test_missing_target_is_rejected_without_creation(self) -> None:
        self.fixture.target.unlink()
        run_git(self.fixture.root, "add", "-u")
        run_git(self.fixture.root, "commit", "-m", "remove target")
        self.fixture.refresh()
        self.assert_rejected(self.fixture.plan, "file creation is not supported")
        self.assertFalse(self.fixture.target.exists())

    def test_noncanonical_source_is_rejected(self) -> None:
        state = json.loads(self.fixture.target.read_text(encoding="utf-8"))
        self.fixture.target.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8", newline="\n")
        run_git(self.fixture.root, "add", "--", TARGET)
        run_git(self.fixture.root, "commit", "-m", "noncanonical state")
        self.fixture.refresh()
        self.assert_rejected(self.fixture.plan, "serialization is not deterministic")

    def test_malformed_source_state_is_rejected(self) -> None:
        state = self.fixture.json(self.fixture.target)
        state["state_id"] = "NOT-A-LIFECYCLE-STATE"
        self.fixture.commit_json_change(self.fixture.target, state)
        self.assert_rejected(self.fixture.plan)

    def test_missing_authorization_is_rejected(self) -> None:
        manifest = self.fixture.json(self.fixture.manifest)
        manifest["active_work_authorization"] = None
        self.fixture.commit_json_change(self.fixture.manifest, manifest)
        self.assert_rejected(self.fixture.plan, "authorization is missing")

    def test_inactive_or_unissued_authorization_is_rejected(self) -> None:
        manifest = self.fixture.json(self.fixture.manifest)
        manifest["active_work_authorization"]["human_authority"]["issued_explicitly"] = False
        self.fixture.commit_json_change(self.fixture.manifest, manifest)
        self.assert_rejected(self.fixture.plan)

    def test_mismatched_authorization_reference_is_rejected(self) -> None:
        self.assert_rejected(
            lambda: FLOPPYCTL._fs09_operation(
                self.fixture.root,
                mode="dry-run",
                transition=TRANSITION,
                authorization_reference="WRONG",
                repository_writer=WRITER,
                expected_branch=self.fixture.branch,
                expected_head=self.fixture.head,
            ),
            "authorization reference",
        )

    def test_wrong_authorization_kind_is_rejected(self) -> None:
        manifest = self.fixture.json(self.fixture.manifest)
        manifest["active_work_authorization"]["authorization_kind"] = "migration"
        self.fixture.commit_json_change(self.fixture.manifest, manifest)
        self.assert_rejected(self.fixture.plan, "wrong kind")

    def test_wrong_project_or_source_version_is_rejected(self) -> None:
        for field, value in (("repository", "wrong/project"), ("source_version", "9.9.9")):
            fixture = Fixture()
            try:
                manifest = fixture.json(fixture.manifest)
                manifest["active_work_authorization"][field] = value
                fixture.commit_json_change(fixture.manifest, manifest)
                self.assert_rejected(fixture.plan)
            finally:
                fixture.close()

    def test_wrong_branch_and_detached_head_are_rejected(self) -> None:
        self.assert_rejected(
            lambda: FLOPPYCTL._fs09_operation(
                self.fixture.root,
                mode="dry-run",
                transition=TRANSITION,
                authorization_reference=AUTHORIZATION,
                repository_writer=WRITER,
                expected_branch="wrong-branch",
                expected_head=self.fixture.head,
            ),
            "wrong branch",
        )
        run_git(self.fixture.root, "checkout", "--detach", self.fixture.head)
        self.fixture.branch = "main"
        self.assert_rejected(self.fixture.plan, "detached HEAD")

    def test_wrong_head_is_rejected(self) -> None:
        self.assert_rejected(
            lambda: FLOPPYCTL._fs09_operation(
                self.fixture.root,
                mode="dry-run",
                transition=TRANSITION,
                authorization_reference=AUTHORIZATION,
                repository_writer=WRITER,
                expected_branch=self.fixture.branch,
                expected_head="0" * 40,
            ),
            "wrong HEAD",
        )

    def test_dirty_staged_tracked_and_untracked_states_are_rejected(self) -> None:
        cases = ("staged", "tracked", "untracked")
        for case in cases:
            fixture = Fixture()
            try:
                if case == "staged":
                    (fixture.root / "base.txt").write_text("changed\n", encoding="utf-8")
                    run_git(fixture.root, "add", "--", "base.txt")
                elif case == "tracked":
                    (fixture.root / "base.txt").write_text("changed\n", encoding="utf-8")
                else:
                    (fixture.root / "new.txt").write_text("new\n", encoding="utf-8")
                self.assert_rejected(fixture.plan, "must be clean")
            finally:
                fixture.close()

    def test_stale_authorization_base_is_rejected(self) -> None:
        manifest = self.fixture.json(self.fixture.manifest)
        manifest["active_work_authorization"]["base_checkpoint"] = "1" * 40
        state = self.fixture.json(self.fixture.target)
        state["base_checkpoint"] = "1" * 40
        self.fixture.manifest.write_bytes(canonical(manifest))
        self.fixture.target.write_bytes(canonical(state))
        run_git(self.fixture.root, "add", "--", ".floppy/manifest.json", TARGET)
        run_git(self.fixture.root, "commit", "-m", "stale base")
        self.fixture.refresh()
        self.assert_rejected(self.fixture.plan, "stale")

    def test_exact_file_scope_may_not_omit_but_may_not_widen_target(self) -> None:
        manifest = self.fixture.json(self.fixture.manifest)
        manifest["active_work_authorization"]["exact_file_scope"] = ["other.txt"]
        self.fixture.commit_json_change(self.fixture.manifest, manifest)
        self.assert_rejected(self.fixture.plan, "omits")
        fixture = Fixture()
        try:
            manifest = fixture.json(fixture.manifest)
            manifest["active_work_authorization"]["exact_file_scope"] = [
                TARGET, "other.txt", ".floppy/manifest.json"
            ]
            fixture.commit_json_change(fixture.manifest, manifest)
            plan = fixture.plan()
            self.assertEqual(plan["exact_target_path"], TARGET)
        finally:
            fixture.close()

    def test_missing_wrong_or_stale_writer_binding_is_rejected(self) -> None:
        for key, value in (
            ("repository_writer", None),
            ("repository_writer", "WRONG"),
            ("current_section_working_model", "WRONG"),
            ("writer_authorization_reference", "STALE"),
        ):
            fixture = Fixture()
            try:
                registry = fixture.json(fixture.registry)
                registry["current_assignments"][key] = value
                fixture.commit_json_change(fixture.registry, registry)
                self.assert_rejected(fixture.plan)
            finally:
                fixture.close()

    def test_plan_is_stale_after_target_mutation(self) -> None:
        plan = self.fixture.plan()
        state = self.fixture.json(self.fixture.target)
        state["evidence"].append("CHANGED")
        self.fixture.target.write_bytes(canonical(state))
        self.assert_rejected(lambda: self.fixture.apply(plan), "must be clean")

    def test_apply_requires_exact_plan_digest(self) -> None:
        self.fixture.plan()
        self.assert_rejected(
            lambda: FLOPPYCTL._fs09_operation(
                self.fixture.root,
                mode="apply",
                transition=TRANSITION,
                authorization_reference=AUTHORIZATION,
                repository_writer=WRITER,
                expected_branch=self.fixture.branch,
                expected_head=self.fixture.head,
                plan_sha256="0" * 64,
            ),
            "exact current dry-run plan",
        )

    def test_temporary_file_collision_is_rejected_and_original_preserved(self) -> None:
        original = self.fixture.target.read_bytes()
        plan = self.fixture.plan()
        collision = self.fixture.target.with_name(".lifecycle-state.json.fs09-stage")
        collision.write_text("collision", encoding="utf-8")
        run_git(self.fixture.root, "add", "--", str(collision.relative_to(self.fixture.root)))
        run_git(self.fixture.root, "commit", "-m", "tracked collision")
        self.fixture.refresh()
        fresh_plan = self.fixture.plan()
        self.assert_rejected(lambda: self.fixture.apply(fresh_plan), "collision")
        self.assertEqual(self.fixture.target.read_bytes(), original)

    def test_target_mutation_immediately_before_replace_is_rejected(self) -> None:
        original = self.fixture.target.read_bytes()
        plan = self.fixture.plan()
        def hook(name: str, context: dict[str, Any]) -> None:
            if name == "after_validation":
                context["target"].write_bytes(b"changed\n")
        FLOPPYCTL._FS09_TEST_HOOK = hook
        self.assert_rejected(lambda: self.fixture.apply(plan), "changed after planning")
        self.assertEqual(self.fixture.target.read_bytes(), b"changed\n")

    def test_failures_before_during_and_after_staging_leave_original(self) -> None:
        for point in ("before_stage", "during_stage_write", "after_stage", "before_replace", "replacement"):
            fixture = Fixture()
            try:
                original = fixture.target.read_bytes()
                plan = fixture.plan()
                def hook(name: str, context: dict[str, Any], point: str = point) -> None:
                    if name == point:
                        raise FLOPPYCTL.CliError(f"injected {point}")
                FLOPPYCTL._FS09_TEST_HOOK = hook
                self.assert_rejected(lambda: fixture.apply(plan))
                self.assertEqual(fixture.target.read_bytes(), original)
                self.assertFalse(any(".fs09-" in item.name for item in fixture.target.parent.iterdir()))
            finally:
                fixture.close()

    def test_final_verification_failure_restores_original(self) -> None:
        original = self.fixture.target.read_bytes()
        plan = self.fixture.plan()
        def hook(name: str, context: dict[str, Any]) -> None:
            if name == "before_final_verify":
                context["target"].write_bytes(b"corrupt\n")
        FLOPPYCTL._FS09_TEST_HOOK = hook
        message = self.assert_rejected(lambda: self.fixture.apply(plan), "original bytes restored")
        self.assertIn("restored", message)
        self.assertEqual(self.fixture.target.read_bytes(), original)
        self.assertFalse(any(".fs09-" in item.name for item in self.fixture.target.parent.iterdir()))

    def test_restoration_failure_is_high_severity_and_never_success(self) -> None:
        plan = self.fixture.plan()
        def hook(name: str, context: dict[str, Any]) -> None:
            if name == "before_final_verify":
                context["target"].write_bytes(b"corrupt\n")
            if name == "before_restore_replace":
                raise FLOPPYCTL.CliError("injected restoration failure")
        FLOPPYCTL._FS09_TEST_HOOK = hook
        self.assert_rejected(lambda: self.fixture.apply(plan), "HIGH-SEVERITY")

    def test_mode_is_preserved(self) -> None:
        original_mode = stat.S_IMODE(self.fixture.target.stat().st_mode)
        self.fixture.apply(self.fixture.plan())
        self.assertEqual(stat.S_IMODE(self.fixture.target.stat().st_mode), original_mode)

    def test_symlink_target_escape_is_rejected_where_supported(self) -> None:
        real = self.fixture.target.with_name("real-state.json")
        self.fixture.target.replace(real)
        try:
            self.fixture.target.symlink_to(real.name)
        except (OSError, NotImplementedError):
            self.skipTest("symbolic links are unavailable")
        run_git(self.fixture.root, "add", "--all")
        run_git(self.fixture.root, "commit", "-m", "symlink target")
        self.fixture.refresh()
        self.assert_rejected(self.fixture.plan, "symbolic link")


def run_required_smokes() -> dict[str, str]:
    results: dict[str, str] = {}
    fixture = Fixture()
    try:
        first = fixture.plan()
        second = fixture.plan()
        if first != second:
            raise AssertionError("dry-run results differ")
        results["deterministic_dry_run"] = "PASSED"
        fixture.apply(first)
        results["controlled_fixture_apply"] = "PASSED"
        results["temporary_file_cleanup"] = (
            "PASSED"
            if not any(".fs09-" in item.name for item in fixture.target.parent.iterdir())
            else "FAILED"
        )
    finally:
        fixture.close()

    fixture = Fixture()
    try:
        plan = fixture.plan()
        fixture.target.write_bytes(b"stale\n")
        try:
            fixture.apply(plan)
        except FLOPPYCTL.CliError:
            results["stale_state_rejection"] = "PASSED"
        else:
            results["stale_state_rejection"] = "FAILED"
    finally:
        fixture.close()

    fixture = Fixture()
    try:
        try:
            FLOPPYCTL._fs09_operation(
                fixture.root,
                mode="dry-run",
                transition=TRANSITION,
                authorization_reference=AUTHORIZATION,
                repository_writer="WRONG",
                expected_branch=fixture.branch,
                expected_head=fixture.head,
            )
        except FLOPPYCTL.CliError:
            results["unauthorized_writer_rejection"] = "PASSED"
        else:
            results["unauthorized_writer_rejection"] = "FAILED"
    finally:
        fixture.close()

    for point, key in (
        ("replacement", "atomic_replacement_failure"),
        ("before_final_verify", "restoration"),
    ):
        fixture = Fixture()
        try:
            original = fixture.target.read_bytes()
            plan = fixture.plan()
            def hook(name: str, context: dict[str, Any], point: str = point) -> None:
                if name == point:
                    if point == "before_final_verify":
                        context["target"].write_bytes(b"corrupt\n")
                    else:
                        raise FLOPPYCTL.CliError("injected replacement failure")
            FLOPPYCTL._FS09_TEST_HOOK = hook
            try:
                fixture.apply(plan)
            except FLOPPYCTL.CliError:
                if point == "before_final_verify" and fixture.target.read_bytes() != original:
                    results[key] = "FAILED"
                else:
                    results[key] = "PASSED"
            else:
                results[key] = "FAILED"
        finally:
            fixture.close()

    fixture = Fixture()
    try:
        plan = fixture.plan()
        def failure_hook(name: str, context: dict[str, Any]) -> None:
            if name == "before_final_verify":
                context["target"].write_bytes(b"corrupt\n")
            if name == "before_restore_replace":
                raise FLOPPYCTL.CliError("injected restoration failure")
        FLOPPYCTL._FS09_TEST_HOOK = failure_hook
        try:
            fixture.apply(plan)
        except FLOPPYCTL.CliError as exc:
            results["restoration_failure_diagnostic"] = (
                "PASSED" if "HIGH-SEVERITY" in str(exc) else "FAILED"
            )
        else:
            results["restoration_failure_diagnostic"] = "FAILED"
    finally:
        fixture.close()

    if any(value != "PASSED" for value in results.values()):
        raise AssertionError(results)
    return results


if __name__ == "__main__":
    unittest.main()
