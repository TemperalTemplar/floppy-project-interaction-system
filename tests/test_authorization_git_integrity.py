from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_floppy.py"
CLI_PATH = ROOT / "tools" / "floppyctl.py"
BRANCH = "feature/fs-06-authorization-git-integrity"
AUTHORIZATION = "FS_06_IMPLEMENTATION"
WRITER = "FS_06_WORKING_MODEL"
SCOPE = [
    "tools/validate_floppy.py",
    "tests/test_authorization_git_integrity.py",
]


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_floppy_fs06",
        VALIDATOR_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load tools/validate_floppy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={root.as_posix()}",
            "-C",
            str(root),
            *args,
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def require_git(root: Path, *args: str) -> str:
    result = run_git(root, *args)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout.strip()


def digest_tree(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            result[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return result


class AuthorizationGitIntegrityTests(unittest.TestCase):
    def manifest(self, branch: str = BRANCH) -> dict:
        active = {
            "authorization_id": AUTHORIZATION,
            "repository_writer": WRITER,
            "writer_authorization_reference": AUTHORIZATION,
            "branch": branch,
            "exact_file_scope": list(SCOPE),
        }
        return {
            "active_work_authorization": active,
            "continuation_point": {
                "active_work_authorization": AUTHORIZATION,
                "repository_writer": WRITER,
                "writer_authorization_reference": AUTHORIZATION,
            },
            "fs_06_work_package": {
                "branch": branch,
                "exact_file_scope": list(SCOPE),
            },
        }

    def make_repo(
        self,
        *,
        branch: str = BRANCH,
        product_paths: list[str] | None = None,
    ) -> tuple[tempfile.TemporaryDirectory[str], Path, str]:
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        require_git(root, "init")
        require_git(root, "config", "user.name", "FS-06 Test")
        require_git(root, "config", "user.email", "fs06@example.invalid")
        require_git(root, "checkout", "-b", branch)

        for relative in [*SCOPE, "baseline.txt"]:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"baseline: {relative}\n", encoding="utf-8")
        require_git(root, "add", "--", ".")
        require_git(root, "commit", "-m", "baseline")

        selected = list(SCOPE if product_paths is None else product_paths)
        for relative in selected:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write("product change\n")
        require_git(root, "add", "--", ".")
        require_git(root, "commit", "-m", "product")
        head = require_git(root, "rev-parse", "HEAD")
        return td, root, head

    def environment(self, head: str) -> dict[str, str]:
        return {
            "FLOPPY_AUTHORIZATION_REFERENCE": AUTHORIZATION,
            "FLOPPY_REPOSITORY_WRITER": WRITER,
            "FLOPPY_EXPECTED_HEAD": head,
            "FLOPPY_SCOPE_COMMIT": head,
        }

    def validate(
        self,
        root: Path,
        manifest: dict,
        environment: dict[str, str],
    ) -> list[str]:
        return VALIDATOR.validate_authorization_git_integrity(
            root,
            manifest,
            environment,
        )

    def test_exact_authorization_and_git_state_pass_together(self) -> None:
        td, root, head = self.make_repo()
        with td:
            self.assertEqual(
                [],
                self.validate(root, self.manifest(), self.environment(head)),
            )

    def test_branch_mismatch_fails_exact_condition(self) -> None:
        td, root, head = self.make_repo()
        with td:
            errors = self.validate(
                root,
                self.manifest("feature/wrong"),
                self.environment(head),
            )
            self.assertIn(
                f"GIT_INTEGRITY_BRANCH_MISMATCH: "
                f"expected feature/wrong found {BRANCH}",
                errors,
            )

    def test_detached_head_fails_when_branch_required(self) -> None:
        td, root, head = self.make_repo()
        with td:
            require_git(root, "checkout", "--detach", head)
            errors = self.validate(
                root,
                self.manifest(),
                self.environment(head),
            )
            self.assertIn(
                f"GIT_INTEGRITY_DETACHED_HEAD: expected branch {BRANCH}",
                errors,
            )

    def test_head_mismatch_fails_exact_condition(self) -> None:
        td, root, head = self.make_repo()
        with td:
            environment = self.environment(head)
            environment["FLOPPY_EXPECTED_HEAD"] = "0" * 40
            errors = self.validate(root, self.manifest(), environment)
            self.assertIn(
                f"GIT_INTEGRITY_HEAD_MISMATCH: expected {'0' * 40} "
                f"found {head}",
                errors,
            )

    def test_dirty_tracked_staged_and_untracked_fail_concisely(self) -> None:
        for case in ("tracked", "staged", "untracked"):
            with self.subTest(case=case):
                td, root, head = self.make_repo()
                with td:
                    if case == "tracked":
                        (root / "baseline.txt").write_text(
                            "dirty\n",
                            encoding="utf-8",
                        )
                        expected = "GIT_INTEGRITY_TRACKED_CHANGES"
                    elif case == "staged":
                        (root / "baseline.txt").write_text(
                            "staged\n",
                            encoding="utf-8",
                        )
                        require_git(root, "add", "--", "baseline.txt")
                        expected = "GIT_INTEGRITY_STAGED_CHANGES"
                    else:
                        (root / "untracked.txt").write_text(
                            "untracked\n",
                            encoding="utf-8",
                        )
                        expected = "GIT_INTEGRITY_UNTRACKED_PATHS"
                    errors = self.validate(
                        root,
                        self.manifest(),
                        self.environment(head),
                    )
                    self.assertTrue(
                        any(item.startswith(expected) for item in errors),
                        errors,
                    )

    def test_missing_and_mismatched_authorization_reference_fail(self) -> None:
        td, root, head = self.make_repo()
        with td:
            missing = self.environment(head)
            missing.pop("FLOPPY_AUTHORIZATION_REFERENCE")
            self.assertIn(
                "GIT_INTEGRITY_AUTHORIZATION_REFERENCE_MISSING",
                self.validate(root, self.manifest(), missing),
            )
            mismatch = self.environment(head)
            mismatch["FLOPPY_AUTHORIZATION_REFERENCE"] = "STALE"
            self.assertIn(
                "GIT_INTEGRITY_AUTHORIZATION_REFERENCE_MISMATCH: "
                f"expected {AUTHORIZATION} found STALE",
                self.validate(root, self.manifest(), mismatch),
            )

    def test_missing_and_mismatched_registered_writer_fail(self) -> None:
        td, root, head = self.make_repo()
        with td:
            missing = self.environment(head)
            missing.pop("FLOPPY_REPOSITORY_WRITER")
            self.assertIn(
                "GIT_INTEGRITY_EXECUTING_WRITER_MISSING",
                self.validate(root, self.manifest(), missing),
            )
            mismatch = self.environment(head)
            mismatch["FLOPPY_REPOSITORY_WRITER"] = "OTHER_MODEL"
            self.assertIn(
                "GIT_INTEGRITY_EXECUTING_WRITER_MISMATCH: "
                f"expected {WRITER} found OTHER_MODEL",
                self.validate(root, self.manifest(), mismatch),
            )

    def test_unauthorized_and_missing_paths_fail_concisely(self) -> None:
        td, root, head = self.make_repo(
            product_paths=[*SCOPE, "unauthorized.txt"]
        )
        with td:
            errors = self.validate(
                root,
                self.manifest(),
                self.environment(head),
            )
            self.assertIn(
                "GIT_INTEGRITY_UNAUTHORIZED_PATHS: unauthorized.txt",
                errors,
            )

        td, root, head = self.make_repo(product_paths=[SCOPE[0]])
        with td:
            errors = self.validate(
                root,
                self.manifest(),
                self.environment(head),
            )
            self.assertIn(
                f"GIT_INTEGRITY_REQUIRED_PATHS_MISSING: {SCOPE[1]}",
                errors,
            )

    def test_exact_authorized_path_set_passes(self) -> None:
        td, root, head = self.make_repo(product_paths=list(reversed(SCOPE)))
        with td:
            self.assertEqual(
                [],
                self.validate(root, self.manifest(), self.environment(head)),
            )

    def test_git_integrity_validation_performs_no_mutation(self) -> None:
        td, root, head = self.make_repo()
        with td:
            before = {
                "head": require_git(root, "rev-parse", "HEAD"),
                "branch": require_git(root, "branch", "--show-current"),
                "status": require_git(
                    root,
                    "status",
                    "--porcelain=v1",
                    "--untracked-files=all",
                ),
                "refs": require_git(root, "show-ref"),
                "files": digest_tree(root),
            }
            self.assertEqual(
                [],
                self.validate(root, self.manifest(), self.environment(head)),
            )
            after = {
                "head": require_git(root, "rev-parse", "HEAD"),
                "branch": require_git(root, "branch", "--show-current"),
                "status": require_git(
                    root,
                    "status",
                    "--porcelain=v1",
                    "--untracked-files=all",
                ),
                "refs": require_git(root, "show-ref"),
                "files": digest_tree(root),
            }
            self.assertEqual(before, after)

    def test_cli_preserves_validator_result_diagnostics_and_exit_status(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "source"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(
                    ".git",
                    "__pycache__",
                    "*.pyc",
                ),
            )
            require_git(root, "init")
            require_git(root, "config", "user.name", "FS-06 Test")
            require_git(root, "config", "user.email", "fs06@example.invalid")
            require_git(root, "checkout", "-b", BRANCH)

            manifest_path = root / ".floppy/manifest.json"
            manifest = json.loads(
                manifest_path.read_text(encoding="utf-8")
            )
            synthetic = self.manifest()
            manifest["active_work_authorization"] = synthetic[
                "active_work_authorization"
            ]
            continuation = manifest.get("continuation_point")
            if not isinstance(continuation, dict):
                continuation = {}
                manifest["continuation_point"] = continuation
            continuation.update(synthetic["continuation_point"])
            manifest["fs_06_work_package"] = synthetic[
                "fs_06_work_package"
            ]
            # This fixture overlays an FS-06 authorization onto a copy of the
            # current source tree. The current tree may itself be at any later
            # control operation (for example closeout proposal/application).
            # Remove that unrelated operation marker so Git-integrity
            # classification is derived from the synthetic active
            # authorization and its parent, not from current project history.
            manifest.pop("git_integrity_operation", None)
            manifest_path.write_text(
                json.dumps(manifest, indent=4, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            require_git(root, "add", "--", ".")
            require_git(root, "commit", "-m", "active control baseline")
            for relative in SCOPE:
                with (root / relative).open("a", encoding="utf-8") as handle:
                    handle.write("\n# CLI preservation fixture\n")
            require_git(root, "add", "--", *SCOPE)
            require_git(root, "commit", "-m", "product")
            head = require_git(root, "rev-parse", "HEAD")

            env = os.environ.copy()
            env.update(self.environment(head))
            env["FLOPPY_REPOSITORY_WRITER"] = "OTHER_MODEL"
            env["PYTHONDONTWRITEBYTECODE"] = "1"

            direct = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(root / "tools/validate_floppy.py"),
                    str(root),
                    "--mode",
                    "source",
                ],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            wrapped = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(root / "tools/floppyctl.py"),
                    "--root",
                    str(root),
                    "validate",
                    "--mode",
                    "source",
                ],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(direct.returncode, 0)
            self.assertEqual(wrapped.returncode, direct.returncode)
            self.assertEqual(wrapped.stdout, direct.stdout)
            self.assertEqual(wrapped.stderr, direct.stderr)
            self.assertIn(
                "GIT_INTEGRITY_EXECUTING_WRITER_MISMATCH",
                direct.stdout,
            )


class WorkPackageAcceptanceGitIntegrityTests(unittest.TestCase):
    SECTION = "FS-12"
    BRANCH = "feature/fs-12-acceptance-integrity-fixture"
    CONTROL_PATHS = [
        ".floppy/floppies/Floppy-E-Current-Section.md",
        ".floppy/lifecycle-state.json",
        ".floppy/manifest.json",
        ".floppy/roadmap/roadmap.json",
        ".floppy/roadmap/roadmap.md",
        ".floppy/templates/Floppy-E-FS-12.draft.md",
    ]

    def write_json(self, path: Path, value: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, indent=4, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def parent_manifest(self) -> dict:
        return {
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
                "last_applied_transition": "TR-009-APPLY-SECTION-CLOSEOUT",
                "active_implementation_section": None,
                "repository_writer": None,
                "writer_authorization_reference": None,
            },
            "fs_12_work_package": {
                "id": self.SECTION,
                "section": self.SECTION,
                "path": ".floppy/templates/Floppy-E-FS-12.draft.md",
                "accepted": False,
                "active": False,
                "implementation_authorized": False,
                "branch": self.BRANCH,
            },
        }

    def candidate_manifest(self, *, verification_only: bool = False) -> dict:
        manifest = self.parent_manifest()
        transition = (
            "TR-016-ACCEPT-VERIFICATION-ONLY-WORK-PACKAGE"
            if verification_only
            else "TR-002-ACCEPT-WORK-PACKAGE"
        )
        post_state = (
            "LC-VERIFICATION-ONLY-WORK-PACKAGE-ACCEPTED-PENDING"
            if verification_only
            else "LC-WORK-PACKAGE-ACCEPTED-NO-ACTIVE-WORK"
        )
        manifest["status"] = post_state
        manifest["authority"]["last_applied_transition"] = transition
        manifest["fs_12_work_package"]["accepted"] = True
        manifest["git_integrity_operation"] = {
            "operation": "WORK_PACKAGE_ACCEPTANCE_CONTROL",
            "section": self.SECTION,
            "implementation_scope_exercised": False,
            "exact_control_paths": list(self.CONTROL_PATHS),
            "transition_sequence": [
                {
                    "id": transition,
                    "pre_state": "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE",
                    "post_state": post_state,
                    "actor": "administrator",
                    "decision": "explicit_work_package_acceptance",
                    "inputs": ["reviewed work package"],
                    "outputs": ["accepted planning baseline"],
                    "validation_evidence": ["exact path proof"],
                }
            ],
        }
        return manifest

    def make_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        require_git(root, "init")
        require_git(root, "config", "user.name", "FS-12 Test")
        require_git(root, "config", "user.email", "fs12@example.invalid")
        require_git(root, "checkout", "-b", self.BRANCH)
        all_paths = set(self.CONTROL_PATHS) | {
            ".floppy/orchestrator-registry.json",
        }
        for relative in sorted(all_paths):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if relative.endswith(".json"):
                self.write_json(path, {"baseline": relative})
            else:
                path.write_text(f"baseline: {relative}\n", encoding="utf-8")
        self.write_json(root / ".floppy/manifest.json", self.parent_manifest())
        require_git(root, "add", "--", ".")
        require_git(root, "commit", "-m", "closed section baseline")
        return td, root

    def commit_acceptance(
        self,
        root: Path,
        *,
        verification_only: bool = False,
        paths: list[str] | None = None,
    ) -> tuple[str, dict]:
        manifest = self.candidate_manifest(verification_only=verification_only)
        selected = list(self.CONTROL_PATHS if paths is None else paths)
        for relative in selected:
            path = root / relative
            if relative == ".floppy/manifest.json":
                self.write_json(path, manifest)
            else:
                with path.open("a", encoding="utf-8") as handle:
                    handle.write("work-package acceptance change\n")
        require_git(root, "add", "--", *selected)
        require_git(root, "commit", "-m", "accept work package")
        return require_git(root, "rev-parse", "HEAD"), manifest

    def environment(self, head: str) -> dict[str, str]:
        return {
            "FLOPPY_EXPECTED_HEAD": head,
            "FLOPPY_SCOPE_COMMIT": head,
            "FLOPPY_CONTROL_OPERATION": "WORK_PACKAGE_ACCEPTANCE_CONTROL",
            "FLOPPY_CONTROL_BRANCH": self.BRANCH,
        }

    def validate(self, root: Path, manifest: dict, head: str) -> list[str]:
        return VALIDATOR.validate_authorization_git_integrity(
            root, manifest, self.environment(head)
        )

    def test_standard_work_package_acceptance_exact_canonical_scope_passes(self) -> None:
        td, root = self.make_repo()
        with td:
            head, manifest = self.commit_acceptance(root)
            self.assertEqual([], self.validate(root, manifest, head))

    def test_verification_only_acceptance_exact_canonical_scope_passes(self) -> None:
        td, root = self.make_repo()
        with td:
            head, manifest = self.commit_acceptance(root, verification_only=True)
            self.assertEqual([], self.validate(root, manifest, head))

    def test_acceptance_missing_canonical_lifecycle_state_fails(self) -> None:
        td, root = self.make_repo()
        with td:
            paths = [
                item
                for item in self.CONTROL_PATHS
                if item != ".floppy/lifecycle-state.json"
            ]
            head, manifest = self.commit_acceptance(root, paths=paths)
            self.assertIn(
                "GIT_INTEGRITY_REQUIRED_PATHS_MISSING: "
                ".floppy/lifecycle-state.json",
                self.validate(root, manifest, head),
            )

    def test_acceptance_cannot_fall_back_when_canonical_registry_missing(self) -> None:
        td, root = self.make_repo()
        with td:
            require_git(root, "rm", "--", ".floppy/orchestrator-registry.json")
            require_git(root, "commit", "-m", "remove canonical registry")
            head, manifest = self.commit_acceptance(root)
            self.assertIn(
                "GIT_INTEGRITY_CANONICAL_CONTROL_RECORDS_REQUIRED",
                self.validate(root, manifest, head),
            )

    def test_acceptance_extra_legacy_projection_fails(self) -> None:
        td, root = self.make_repo()
        with td:
            extra = ".floppy/floppies/Floppy-D-Project-Map.md"
            path = root / extra
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("legacy projection change\n", encoding="utf-8")
            head, manifest = self.commit_acceptance(
                root, paths=[*self.CONTROL_PATHS, extra]
            )
            self.assertIn(
                f"GIT_INTEGRITY_UNAUTHORIZED_PATHS: {extra}",
                self.validate(root, manifest, head),
            )


class ActivationAndImplementationGitIntegrityTests(unittest.TestCase):
    SECTION = "FS-11"
    AUTHORIZATION = "FS_11_PROV_01_IMPLEMENTATION"
    WRITER = "FS_11_PROV_01_WORKING_MODEL"
    BRANCH = "feature/fs-11-git-integrity-fixture"
    PRODUCT_SCOPE = [
        "README.md",
        "docs/User-Guide.md",
        "project-seed/.floppy/lifecycle-state.json",
        "project-seed/.floppy/manifest.json",
        "project-seed/.floppy/orchestrator-registry.json",
        "schemas/floppy-fields.md",
        "system-manifest.json",
        "tools/floppyctl.py",
        "tools/initialize_project.py",
        "tools/validate_floppy.py",
        "tests/test_floppyctl.py",
        "tests/test_orchestrator_registry.py",
        "tests/test_project_provisioning.py",
        "tests/test_validated_boot_package.py",
    ]
    CONTROL_PATHS = [
        ".floppy/floppies/Floppy-E-Current-Section.md",
        ".floppy/lifecycle-state.json",
        ".floppy/manifest.json",
        ".floppy/orchestrator-registry.json",
        ".floppy/roadmap/roadmap.json",
        ".floppy/roadmap/roadmap.md",
        ".floppy/templates/Floppy-E-FS-11.draft.md",
    ]

    def parent_manifest(self) -> dict:
        return {
            "status": "LC-WORK-PACKAGE-ACCEPTED-NO-ACTIVE-WORK",
            "active_work_authorization": None,
            "continuation_point": {
                "active_work_authorization": None,
                "repository_writer": None,
                "writer_authorization_reference": None,
            },
            "authority": {
                "last_applied_transition": "TR-002-ACCEPT-WORK-PACKAGE",
                "active_implementation_section": None,
                "repository_writer": None,
                "writer_authorization_reference": None,
            },
            "fs_11_work_package": {
                "id": self.SECTION,
                "section": self.SECTION,
                "path": ".floppy/templates/Floppy-E-FS-11.draft.md",
                "accepted": True,
                "active": False,
                "implementation_authorized": False,
            },
        }

    def active_authorization(self) -> dict:
        return {
            "authorization_id": self.AUTHORIZATION,
            "authorization_kind": "section_implementation",
            "section": self.SECTION,
            "base_checkpoint": "1" * 40,
            "branch": self.BRANCH,
            "worktree": r"D:\A\Floppy-CTRL-02",
            "repository_writer": self.WRITER,
            "writer_authorization_reference": self.AUTHORIZATION,
            "exact_file_scope": list(self.PRODUCT_SCOPE),
        }

    def activation_manifest(self) -> dict:
        manifest = self.parent_manifest()
        manifest["status"] = "LC-SECTION-IMPLEMENTATION-IN-PROGRESS"
        manifest["active_work_authorization"] = self.active_authorization()
        manifest["continuation_point"].update({
            "active_work_authorization": self.AUTHORIZATION,
            "repository_writer": self.WRITER,
            "writer_authorization_reference": self.AUTHORIZATION,
            "active_implementation_section": self.SECTION,
        })
        manifest["authority"].update({
            "last_applied_transition": "TR-004-START-SECTION-IMPLEMENTATION",
            "active_implementation_section": self.SECTION,
            "repository_writer": self.WRITER,
            "writer_authorization_reference": self.AUTHORIZATION,
            "authorization_id": self.AUTHORIZATION,
        })
        manifest["fs_11_work_package"].update({
            "active": True,
            "implementation_authorized": True,
            "authorization_id": self.AUTHORIZATION,
            "repository_writer": self.WRITER,
            "writer_authorization_reference": self.AUTHORIZATION,
        })
        manifest["authorization_activation"] = {
            "authorization_id": self.AUTHORIZATION,
            "operation": "ACTIVATION_CONTROL_COMMIT",
            "implementation_scope_exercised": False,
            "exact_control_paths": list(self.CONTROL_PATHS),
            "transition_sequence": [
                {
                    "id": "TR-003-AUTHORIZE-SECTION-IMPLEMENTATION",
                    "pre_state": "LC-WORK-PACKAGE-ACCEPTED-NO-ACTIVE-WORK",
                    "post_state": "LC-SECTION-AUTHORIZED-NOT-STARTED",
                },
                {
                    "id": "TR-004-START-SECTION-IMPLEMENTATION",
                    "pre_state": "LC-SECTION-AUTHORIZED-NOT-STARTED",
                    "post_state": "LC-SECTION-IMPLEMENTATION-IN-PROGRESS",
                },
            ],
        }
        return manifest

    def write_json(self, path: Path, value: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, indent=4, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def make_parent_repo(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        require_git(root, "init")
        require_git(root, "config", "user.name", "FS-11 Test")
        require_git(root, "config", "user.email", "fs11@example.invalid")
        require_git(root, "checkout", "-b", self.BRANCH)
        all_paths = set(self.PRODUCT_SCOPE) | set(self.CONTROL_PATHS) | {
            ".floppy/README.md",
        }
        for relative in sorted(all_paths):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if relative.endswith(".json"):
                self.write_json(path, {"baseline": relative})
            else:
                path.write_text(f"baseline: {relative}\n", encoding="utf-8")
        self.write_json(root / ".floppy/manifest.json", self.parent_manifest())
        require_git(root, "add", "--", ".")
        require_git(root, "commit", "-m", "accepted work package")
        return td, root

    def commit_activation(
        self,
        root: Path,
        *,
        manifest: dict | None = None,
        paths: list[str] | None = None,
    ) -> tuple[str, dict]:
        candidate = self.activation_manifest() if manifest is None else manifest
        selected = list(self.CONTROL_PATHS if paths is None else paths)
        for relative in selected:
            path = root / relative
            if relative == ".floppy/manifest.json":
                self.write_json(path, candidate)
            else:
                with path.open("a", encoding="utf-8") as handle:
                    handle.write("activation control change\n")
        require_git(root, "add", "--", *selected)
        require_git(root, "commit", "-m", "activation")
        return require_git(root, "rev-parse", "HEAD"), candidate

    def commit_implementation(
        self,
        root: Path,
        *,
        product_paths: list[str] | None = None,
        manifest_mutator=None,
    ) -> tuple[str, dict]:
        candidate = json.loads(
            (root / ".floppy/manifest.json").read_text(encoding="utf-8")
        )
        if manifest_mutator is not None:
            manifest_mutator(candidate)
            self.write_json(root / ".floppy/manifest.json", candidate)
        selected = list(self.PRODUCT_SCOPE if product_paths is None else product_paths)
        for relative in selected:
            path = root / relative
            with path.open("a", encoding="utf-8") as handle:
                handle.write("implementation change\n")
        require_git(root, "add", "--", ".")
        require_git(root, "commit", "-m", "implementation")
        return require_git(root, "rev-parse", "HEAD"), candidate

    def environment(self, head: str, writer: str | None = None) -> dict[str, str]:
        return {
            "FLOPPY_AUTHORIZATION_REFERENCE": self.AUTHORIZATION,
            "FLOPPY_REPOSITORY_WRITER": self.WRITER if writer is None else writer,
            "FLOPPY_EXPECTED_HEAD": head,
            "FLOPPY_SCOPE_COMMIT": head,
        }

    def validate(self, root: Path, manifest: dict, head: str, writer=None):
        return VALIDATOR.validate_authorization_git_integrity(
            root,
            manifest,
            self.environment(head, writer),
        )

    def test_activation_control_commit_with_future_fourteen_path_scope_passes(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            head, manifest = self.commit_activation(root)
            self.assertEqual([], self.validate(root, manifest, head))

    def test_activation_does_not_require_future_implementation_paths(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            head, manifest = self.commit_activation(root)
            errors = self.validate(root, manifest, head)
            self.assertFalse(
                any(item.startswith("GIT_INTEGRITY_REQUIRED_PATHS_MISSING") for item in errors),
                errors,
            )

    def test_activation_changing_implementation_path_fails(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            paths = [*self.CONTROL_PATHS, self.PRODUCT_SCOPE[0]]
            head, manifest = self.commit_activation(root, paths=paths)
            errors = self.validate(root, manifest, head)
            self.assertTrue(
                any(item.startswith("GIT_INTEGRITY_ACTIVATION_CHANGED_IMPLEMENTATION_PATHS") for item in errors),
                errors,
            )

    def test_activation_extra_administrative_path_fails(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            head, manifest = self.commit_activation(
                root,
                paths=[*self.CONTROL_PATHS, ".floppy/README.md"],
            )
            self.assertIn(
                "GIT_INTEGRITY_UNAUTHORIZED_PATHS: .floppy/README.md",
                self.validate(root, manifest, head),
            )

    def test_activation_missing_required_control_path_fails(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            omitted = self.CONTROL_PATHS[-1]
            head, manifest = self.commit_activation(
                root,
                paths=self.CONTROL_PATHS[:-1],
            )
            self.assertIn(
                f"GIT_INTEGRITY_REQUIRED_PATHS_MISSING: {omitted}",
                self.validate(root, manifest, head),
            )

    def test_activation_without_explicit_transition_evidence_fails(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            manifest = self.activation_manifest()
            manifest.pop("authorization_activation")
            head, manifest = self.commit_activation(root, manifest=manifest)
            self.assertIn(
                "GIT_INTEGRITY_ACTIVATION_EVIDENCE_INVALID",
                self.validate(root, manifest, head),
            )

    def test_activation_writer_mismatch_fails(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            head, manifest = self.commit_activation(root)
            self.assertIn(
                "GIT_INTEGRITY_EXECUTING_WRITER_MISMATCH: "
                f"expected {self.WRITER} found OTHER_WRITER",
                self.validate(root, manifest, head, "OTHER_WRITER"),
            )

    def test_activation_writer_reference_mismatch_fails(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            manifest = self.activation_manifest()
            manifest["active_work_authorization"][
                "writer_authorization_reference"
            ] = "OTHER_AUTHORIZATION"
            head, manifest = self.commit_activation(root, manifest=manifest)
            errors = self.validate(root, manifest, head)
            self.assertTrue(
                any("AUTHORIZATION_REFERENCE" in item for item in errors),
                errors,
            )

    def test_implementation_exact_active_scope_passes(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            self.commit_activation(root)
            head, manifest = self.commit_implementation(root)
            self.assertEqual([], self.validate(root, manifest, head))

    def test_implementation_missing_required_path_fails(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            self.commit_activation(root)
            missing = self.PRODUCT_SCOPE[-1]
            head, manifest = self.commit_implementation(
                root,
                product_paths=self.PRODUCT_SCOPE[:-1],
            )
            self.assertIn(
                f"GIT_INTEGRITY_REQUIRED_PATHS_MISSING: {missing}",
                self.validate(root, manifest, head),
            )

    def test_implementation_unauthorized_path_fails(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            self.commit_activation(root)
            head, manifest = self.commit_implementation(
                root,
                product_paths=[*self.PRODUCT_SCOPE, "unauthorized.txt"],
            )
            self.assertIn(
                "GIT_INTEGRITY_UNAUTHORIZED_PATHS: unauthorized.txt",
                self.validate(root, manifest, head),
            )

    def test_implementation_root_control_path_fails(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            self.commit_activation(root)
            head, manifest = self.commit_implementation(
                root,
                product_paths=[*self.PRODUCT_SCOPE, ".floppy/README.md"],
            )
            self.assertIn(
                "GIT_INTEGRITY_UNAUTHORIZED_PATHS: .floppy/README.md",
                self.validate(root, manifest, head),
            )

    def test_implementation_authorization_scope_mutation_fails(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            self.commit_activation(root)

            def mutate(manifest):
                manifest["active_work_authorization"]["exact_file_scope"] = (
                    self.PRODUCT_SCOPE[:-1]
                )

            head, manifest = self.commit_implementation(
                root,
                product_paths=self.PRODUCT_SCOPE[:-1],
                manifest_mutator=mutate,
            )
            errors = self.validate(root, manifest, head)
            self.assertTrue(
                any(item.startswith("GIT_INTEGRITY_AUTHORIZATION_MUTATED") for item in errors),
                errors,
            )

    def test_implementation_different_writer_fails(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            self.commit_activation(root)
            head, manifest = self.commit_implementation(root)
            self.assertIn(
                "GIT_INTEGRITY_EXECUTING_WRITER_MISMATCH: "
                f"expected {self.WRITER} found OTHER_WRITER",
                self.validate(root, manifest, head, "OTHER_WRITER"),
            )

    def test_combined_activation_and_implementation_fails(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            head, manifest = self.commit_activation(
                root,
                paths=[*self.CONTROL_PATHS, *self.PRODUCT_SCOPE],
            )
            errors = self.validate(root, manifest, head)
            self.assertTrue(
                any(item.startswith("GIT_INTEGRITY_ACTIVATION_CHANGED_IMPLEMENTATION_PATHS") for item in errors),
                errors,
            )

    def test_implementation_parent_must_preserve_same_authorization(self) -> None:
        td, root = self.make_parent_repo()
        with td:
            self.commit_activation(root)

            def mutate(manifest):
                manifest["active_work_authorization"]["authorization_id"] = (
                    "OTHER_AUTHORIZATION"
                )

            head, manifest = self.commit_implementation(
                root,
                manifest_mutator=mutate,
            )
            errors = self.validate(root, manifest, head)
            self.assertTrue(
                any(item.startswith("GIT_INTEGRITY_AUTHORIZATION_MUTATED") for item in errors),
                errors,
            )


class RemainingControlCommitGitIntegrityTests(unittest.TestCase):
    SECTION = "FS-11"
    NEXT_SECTION = "FS-12"
    BRANCH = "feature/fs-11-remaining-control-fixture"
    PROV_AUTH = "FS_11_PROV_01_IMPLEMENTATION"
    PROV_WRITER = "FS_11_PROV_01_WORKING_MODEL"
    INT_AUTH = "FS_11_INT_01_SELF_HOSTED_RECONCILIATION"
    INT_WRITER = "FS_11_INT_01_WORKING_MODEL"
    HANDOFF_PATHS = [
        ".floppy/floppies/Floppy-E-Current-Section.md",
        ".floppy/manifest.json",
        ".floppy/roadmap/roadmap.json",
        ".floppy/roadmap/roadmap.md",
        ".floppy/lifecycle-state.json",
        ".floppy/orchestrator-registry.json",
        ".floppy/templates/Floppy-E-FS-11.draft.md",
    ]
    RECONCILIATION_PATHS = [
        ".floppy/START-HERE.md",
        ".floppy/README.md",
        ".floppy/floppies/Floppy-B-Development-Issues.md",
        ".floppy/floppies/Floppy-D-Project-Map.md",
        ".floppy/floppies/Floppy-E-Current-Section.md",
        ".floppy/manifest.json",
        ".floppy/roadmap/roadmap.json",
        ".floppy/roadmap/roadmap.md",
        ".floppy/lifecycle-state.json",
        ".floppy/orchestrator-registry.json",
    ]
    PROPOSAL_PATHS = [
        ".floppy/closeouts/FS-11-closeout.md",
        ".floppy/floppies/Floppy-E-Current-Section.md",
        ".floppy/manifest.json",
        ".floppy/roadmap/roadmap.json",
        ".floppy/roadmap/roadmap.md",
        ".floppy/lifecycle-state.json",
        ".floppy/templates/Floppy-E-FS-11.draft.md",
    ]
    APPLICATION_PATHS = [
        ".floppy/START-HERE.md",
        ".floppy/README.md",
        ".floppy/closeouts/FS-11-closeout.md",
        ".floppy/floppies/Floppy-D-Project-Map.md",
        ".floppy/floppies/Floppy-E-Current-Section.md",
        ".floppy/manifest.json",
        ".floppy/roadmap/roadmap.json",
        ".floppy/roadmap/roadmap.md",
        ".floppy/lifecycle-state.json",
        ".floppy/orchestrator-registry.json",
        ".floppy/templates/Floppy-E-FS-11.draft.md",
        ".floppy/templates/Floppy-E-FS-12.draft.md",
    ]

    def active(self, authorization: str, writer: str, scope: list[str]) -> dict:
        return {
            "authorization_id": authorization,
            "authorization_kind": "section_implementation",
            "section": self.SECTION,
            "base_checkpoint": "1" * 40,
            "branch": self.BRANCH,
            "worktree": r"D:\A\Floppy-CTRL-02",
            "repository_writer": writer,
            "writer_authorization_reference": authorization,
            "exact_file_scope": list(scope),
        }

    def manifest_with_authority(
        self,
        *,
        status: str,
        authorization: str,
        writer: str,
        scope: list[str],
    ) -> dict:
        return {
            "status": status,
            "active_work_authorization": self.active(
                authorization,
                writer,
                scope,
            ),
            "repository_writer": writer,
            "writer_authorization_reference": authorization,
            "continuation_point": {
                "active_work_authorization": authorization,
                "repository_writer": writer,
                "writer_authorization_reference": authorization,
                "active_implementation_section": self.SECTION,
            },
            "authority": {
                "authority_state": "EXACT_SECTION_IMPLEMENTATION_AUTHORIZATION",
                "active_work_authorization": authorization,
                "active_implementation_authorization": authorization,
                "active_implementation_section": self.SECTION,
                "current_authorized_section": self.SECTION,
                "authorization_id": authorization,
                "repository_writer": writer,
                "writer_authorization_reference": authorization,
            },
            "fs_11_work_package": {
                "id": self.SECTION,
                "section": self.SECTION,
                "path": ".floppy/templates/Floppy-E-FS-11.draft.md",
                "branch": self.BRANCH,
                "accepted": True,
                "active": True,
                "implementation_authorized": True,
                "authorization_id": authorization,
                "repository_writer": writer,
                "writer_authorization_reference": authorization,
            },
        }

    def transition(
        self,
        identifier: str,
        pre_state: str,
        post_state: str,
    ) -> dict:
        return {
            "id": identifier,
            "pre_state": pre_state,
            "post_state": post_state,
            "actor": "fixture actor",
            "decision": "fixture decision",
            "inputs": ["fixture input"],
            "outputs": ["fixture output"],
            "validation_evidence": ["fixture validation"],
        }

    def operation(
        self,
        name: str,
        paths: list[str],
        transitions: list[dict],
        *,
        exercised: bool = False,
    ) -> dict:
        return {
            "operation": name,
            "section": self.SECTION,
            "implementation_scope_exercised": exercised,
            "exact_control_paths": list(paths),
            "transition_sequence": transitions,
        }

    def write_json(self, path: Path, value: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, indent=4, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def make_repo(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        require_git(root, "init")
        require_git(root, "config", "user.name", "Remaining Control Test")
        require_git(root, "config", "user.email", "remaining@example.invalid")
        require_git(root, "checkout", "-b", self.BRANCH)
        all_paths = (
            set(self.HANDOFF_PATHS)
            | set(self.RECONCILIATION_PATHS)
            | set(self.PROPOSAL_PATHS)
            | set(self.APPLICATION_PATHS)
        )
        all_paths.discard(".floppy/lifecycle-state.json")
        all_paths.discard(".floppy/orchestrator-registry.json")
        for relative in sorted(all_paths):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if relative.endswith(".json"):
                self.write_json(path, {"baseline": relative})
            else:
                path.write_text(f"baseline: {relative}\n", encoding="utf-8")
        parent = self.manifest_with_authority(
            status="LC-SECTION-IMPLEMENTATION-IN-PROGRESS",
            authorization=self.PROV_AUTH,
            writer=self.PROV_WRITER,
            scope=["README.md"],
        )
        self.write_json(root / ".floppy/manifest.json", parent)
        require_git(root, "add", "--", ".")
        require_git(root, "commit", "-m", "PROV-01 parent")
        return td, root

    def apply_commit(
        self,
        root: Path,
        manifest: dict,
        paths: list[str],
        subject: str,
    ) -> str:
        for relative in paths:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if relative == ".floppy/manifest.json":
                self.write_json(path, manifest)
            elif relative == ".floppy/roadmap/roadmap.json":
                self.write_json(
                    path,
                    {
                        "changed": relative,
                        "subject": subject,
                        "sections": [
                            {"id": self.SECTION},
                            {"id": self.NEXT_SECTION},
                        ],
                    },
                )
            elif relative in {
                ".floppy/lifecycle-state.json",
                ".floppy/orchestrator-registry.json",
            }:
                self.write_json(path, {"changed": relative, "subject": subject})
            else:
                with path.open("a", encoding="utf-8") as handle:
                    handle.write(f"{subject}\n")
        require_git(root, "add", "--", *paths)
        require_git(root, "commit", "-m", subject)
        return require_git(root, "rev-parse", "HEAD")

    def environment(
        self,
        head: str,
        authorization: str | None,
        writer: str | None,
    ) -> dict[str, str]:
        value = {
            "FLOPPY_EXPECTED_HEAD": head,
            "FLOPPY_SCOPE_COMMIT": head,
        }
        if authorization is not None:
            value["FLOPPY_AUTHORIZATION_REFERENCE"] = authorization
        if writer is not None:
            value["FLOPPY_REPOSITORY_WRITER"] = writer
        return value

    def validate(
        self,
        root: Path,
        manifest: dict,
        head: str,
        authorization: str | None,
        writer: str | None,
    ) -> list[str]:
        return VALIDATOR.validate_authorization_git_integrity(
            root,
            manifest,
            self.environment(head, authorization, writer),
        )

    def handoff_manifest(self) -> dict:
        candidate = self.manifest_with_authority(
            status="LC-SECTION-IMPLEMENTATION-IN-PROGRESS",
            authorization=self.INT_AUTH,
            writer=self.INT_WRITER,
            scope=self.RECONCILIATION_PATHS,
        )
        candidate["git_integrity_operation"] = self.operation(
            "STATE_PRESERVING_AUTHORITY_HANDOFF",
            self.HANDOFF_PATHS,
            [],
        )
        return candidate

    def commit_handoff(self, root: Path, paths: list[str] | None = None):
        manifest = self.handoff_manifest()
        selected = self.HANDOFF_PATHS if paths is None else paths
        head = self.apply_commit(root, manifest, selected, "authority handoff")
        return head, manifest

    def test_state_preserving_authority_handoff_passes(self) -> None:
        td, root = self.make_repo()
        with td:
            head, manifest = self.commit_handoff(root)
            self.assertEqual(
                [],
                self.validate(root, manifest, head, self.INT_AUTH, self.INT_WRITER),
            )

    def test_handoff_cannot_include_reconciliation_bytes(self) -> None:
        td, root = self.make_repo()
        with td:
            extra = ".floppy/README.md"
            head, manifest = self.commit_handoff(
                root,
                [*self.HANDOFF_PATHS, extra],
            )
            self.assertIn(
                f"GIT_INTEGRITY_UNAUTHORIZED_PATHS: {extra}",
                self.validate(root, manifest, head, self.INT_AUTH, self.INT_WRITER),
            )

    def test_handoff_requires_distinct_writer_and_authorization(self) -> None:
        td, root = self.make_repo()
        with td:
            manifest = self.handoff_manifest()
            manifest["active_work_authorization"]["authorization_id"] = self.PROV_AUTH
            manifest["active_work_authorization"]["writer_authorization_reference"] = self.PROV_AUTH
            manifest["writer_authorization_reference"] = self.PROV_AUTH
            manifest["continuation_point"]["active_work_authorization"] = self.PROV_AUTH
            manifest["continuation_point"]["writer_authorization_reference"] = self.PROV_AUTH
            manifest["authority"]["active_work_authorization"] = self.PROV_AUTH
            manifest["authority"]["active_implementation_authorization"] = self.PROV_AUTH
            manifest["authority"]["authorization_id"] = self.PROV_AUTH
            manifest["authority"]["writer_authorization_reference"] = self.PROV_AUTH
            manifest["fs_11_work_package"]["authorization_id"] = self.PROV_AUTH
            manifest["fs_11_work_package"]["writer_authorization_reference"] = self.PROV_AUTH
            head = self.apply_commit(root, manifest, self.HANDOFF_PATHS, "bad handoff")
            self.assertIn(
                "GIT_INTEGRITY_HANDOFF_AUTHORIZATION_NOT_REPLACED",
                self.validate(root, manifest, head, self.PROV_AUTH, self.INT_WRITER),
            )

    def test_root_control_implementation_exact_scope_passes(self) -> None:
        td, root = self.make_repo()
        with td:
            self.commit_handoff(root)
            manifest = self.handoff_manifest()
            manifest["git_integrity_operation"] = self.operation(
                "ROOT_CONTROL_IMPLEMENTATION",
                self.RECONCILIATION_PATHS,
                [],
                exercised=True,
            )
            head = self.apply_commit(
                root,
                manifest,
                self.RECONCILIATION_PATHS,
                "reconciliation",
            )
            self.assertEqual(
                [],
                self.validate(root, manifest, head, self.INT_AUTH, self.INT_WRITER),
            )

    def completion_manifest(self) -> dict:
        manifest = self.handoff_manifest()
        manifest["status"] = "LC-VERIFICATION-COMPLETE-ACCEPTANCE-PENDING"
        manifest["git_integrity_operation"] = self.operation(
            "COMPLETION_VERIFICATION_CONTROL",
            self.HANDOFF_PATHS,
            [
                self.transition(
                    "TR-005-RECORD-IMPLEMENTATION-COMPLETE",
                    "LC-SECTION-IMPLEMENTATION-IN-PROGRESS",
                    "LC-IMPLEMENTATION-COMPLETE-VERIFICATION-PENDING",
                ),
                self.transition(
                    "TR-006-RECORD-VERIFICATION-COMPLETE",
                    "LC-IMPLEMENTATION-COMPLETE-VERIFICATION-PENDING",
                    "LC-VERIFICATION-COMPLETE-ACCEPTANCE-PENDING",
                ),
            ],
        )
        return manifest

    def test_completion_verification_control_passes_and_retains_authority(self) -> None:
        td, root = self.make_repo()
        with td:
            self.commit_handoff(root)
            manifest = self.completion_manifest()
            head = self.apply_commit(root, manifest, self.HANDOFF_PATHS, "complete")
            self.assertEqual(
                [],
                self.validate(root, manifest, head, self.INT_AUTH, self.INT_WRITER),
            )

    def test_completion_requires_ordered_extended_transition_evidence(self) -> None:
        td, root = self.make_repo()
        with td:
            self.commit_handoff(root)
            manifest = self.completion_manifest()
            manifest["git_integrity_operation"]["transition_sequence"].reverse()
            head = self.apply_commit(root, manifest, self.HANDOFF_PATHS, "bad complete")
            errors = self.validate(root, manifest, head, self.INT_AUTH, self.INT_WRITER)
            self.assertTrue(
                any(item.startswith("GIT_INTEGRITY_TRANSITION_SEQUENCE_INVALID") for item in errors),
                errors,
            )

    def acceptance_manifest(self) -> dict:
        manifest = self.completion_manifest()
        manifest["status"] = "LC-SECTION-ACCEPTED-CLOSEOUT-NOT-PROPOSED"
        manifest["active_work_authorization"] = None
        manifest["repository_writer"] = None
        manifest["writer_authorization_reference"] = None
        manifest["continuation_point"].update({
            "active_work_authorization": None,
            "repository_writer": None,
            "writer_authorization_reference": None,
            "active_implementation_section": None,
        })
        manifest["authority"].update({
            "authority_state": "NO_ACTIVE_WORK_AUTHORIZATION",
            "active_work_authorization": None,
            "active_implementation_authorization": None,
            "active_implementation_section": None,
            "current_authorized_section": None,
            "authorization_id": None,
            "repository_writer": None,
            "writer_authorization_reference": None,
        })
        manifest["fs_11_work_package"].update({
            "active": False,
            "implementation_authorized": False,
            "authorization_id": None,
            "repository_writer": None,
            "writer_authorization_reference": None,
        })
        manifest["git_integrity_operation"] = self.operation(
            "ADMINISTRATOR_ACCEPTANCE_CONTROL",
            self.HANDOFF_PATHS,
            [
                self.transition(
                    "TR-007-ACCEPT-SECTION",
                    "LC-VERIFICATION-COMPLETE-ACCEPTANCE-PENDING",
                    "LC-SECTION-ACCEPTED-CLOSEOUT-NOT-PROPOSED",
                )
            ],
        )
        return manifest

    def test_administrator_acceptance_passes_and_clears_authority(self) -> None:
        td, root = self.make_repo()
        with td:
            self.commit_handoff(root)
            completion = self.completion_manifest()
            self.apply_commit(root, completion, self.HANDOFF_PATHS, "complete")
            manifest = self.acceptance_manifest()
            head = self.apply_commit(root, manifest, self.HANDOFF_PATHS, "accept")
            self.assertEqual(
                [],
                self.validate(root, manifest, head, self.INT_AUTH, self.INT_WRITER),
            )

    def test_administrator_acceptance_rejects_incomplete_clearance(self) -> None:
        td, root = self.make_repo()
        with td:
            self.commit_handoff(root)
            completion = self.completion_manifest()
            self.apply_commit(root, completion, self.HANDOFF_PATHS, "complete")
            manifest = self.acceptance_manifest()
            manifest["authority"]["repository_writer"] = self.INT_WRITER
            head = self.apply_commit(root, manifest, self.HANDOFF_PATHS, "bad accept")
            self.assertIn(
                "GIT_INTEGRITY_AUTHORITY_CLEARANCE_INCOMPLETE",
                self.validate(root, manifest, head, self.INT_AUTH, self.INT_WRITER),
            )

    def proposal_manifest(self) -> dict:
        manifest = self.acceptance_manifest()
        manifest["status"] = "LC-SECTION-ACCEPTED-CLOSEOUT-PROPOSED"
        manifest["closeout_proposal"] = {
            "section": self.SECTION,
            "transition": "TR-008-PROPOSE-SECTION-CLOSEOUT",
            "record": ".floppy/closeouts/FS-11-closeout.md",
        }
        manifest["git_integrity_operation"] = self.operation(
            "CLOSEOUT_PROPOSAL_CONTROL",
            self.PROPOSAL_PATHS,
            [
                self.transition(
                    "TR-008-PROPOSE-SECTION-CLOSEOUT",
                    "LC-SECTION-ACCEPTED-CLOSEOUT-NOT-PROPOSED",
                    "LC-SECTION-ACCEPTED-CLOSEOUT-PROPOSED",
                )
            ],
        )
        return manifest

    def test_closeout_proposal_exact_scope_passes_without_active_writer(self) -> None:
        td, root = self.make_repo()
        with td:
            self.commit_handoff(root)
            completion = self.completion_manifest()
            self.apply_commit(root, completion, self.HANDOFF_PATHS, "complete")
            acceptance = self.acceptance_manifest()
            self.apply_commit(root, acceptance, self.HANDOFF_PATHS, "accept")
            manifest = self.proposal_manifest()
            head = self.apply_commit(root, manifest, self.PROPOSAL_PATHS, "proposal")
            self.assertEqual([], self.validate(root, manifest, head, None, None))

    def application_manifest(self) -> dict:
        manifest = self.proposal_manifest()
        manifest["status"] = "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE"
        manifest["closeout_application"] = {
            "section": self.SECTION,
            "transition": "TR-009-APPLY-SECTION-CLOSEOUT",
            "record": ".floppy/closeouts/FS-11-closeout.md",
            "fs_12_draft_path": ".floppy/templates/Floppy-E-FS-12.draft.md",
        }
        manifest["fs_12_work_package"] = {
            "id": self.NEXT_SECTION,
            "section": self.NEXT_SECTION,
            "path": ".floppy/templates/Floppy-E-FS-12.draft.md",
            "branch": self.BRANCH,
            "accepted": False,
            "active": False,
            "implementation_authorized": False,
            "authorization_id": None,
            "repository_writer": None,
        }
        manifest["git_integrity_operation"] = self.operation(
            "CLOSEOUT_APPLICATION_CONTROL",
            self.APPLICATION_PATHS,
            [
                self.transition(
                    "TR-009-APPLY-SECTION-CLOSEOUT",
                    "LC-SECTION-ACCEPTED-CLOSEOUT-PROPOSED",
                    "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE",
                )
            ],
        )
        return manifest

    def test_closeout_application_exact_scope_passes_without_active_writer(self) -> None:
        td, root = self.make_repo()
        with td:
            self.commit_handoff(root)
            completion = self.completion_manifest()
            self.apply_commit(root, completion, self.HANDOFF_PATHS, "complete")
            acceptance = self.acceptance_manifest()
            self.apply_commit(root, acceptance, self.HANDOFF_PATHS, "accept")
            proposal = self.proposal_manifest()
            self.apply_commit(root, proposal, self.PROPOSAL_PATHS, "proposal")
            manifest = self.application_manifest()
            head = self.apply_commit(root, manifest, self.APPLICATION_PATHS, "application")
            self.assertEqual([], self.validate(root, manifest, head, None, None))

    def _terminal_scope_manifest(self, section: str) -> dict:
        return {
            f"fs_{section[3:]}_work_package": {
                "id": section,
                "section": section,
                "path": f".floppy/templates/Floppy-E-{section}.draft.md",
            },
            "closeout_proposal": {
                "section": section,
                "record": f".floppy/closeouts/{section}-closeout.md",
            },
        }

    def _write_terminal_scope_roadmap(
        self,
        root: Path,
        section_ids: list[str],
    ) -> None:
        self.write_json(
            root / ".floppy/roadmap/roadmap.json",
            {"sections": [{"id": item} for item in section_ids]},
        )

    def test_non_final_closeout_application_still_requires_next_draft(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_terminal_scope_roadmap(
                root,
                ["FS-11", "FS-12", "FS-13"],
            )
            section = "FS-12"
            manifest = self._terminal_scope_manifest(section)
            actual = VALIDATOR._git_integrity_control_paths(
                "CLOSEOUT_APPLICATION_CONTROL",
                manifest,
                manifest,
                section,
                root,
            )
            self.assertIsNotNone(actual)
            assert actual is not None
            self.assertIn(
                ".floppy/templates/Floppy-E-FS-13.draft.md",
                actual,
            )
            self.assertNotIn(
                ".floppy/templates/Floppy-E-FS-14.draft.md",
                actual,
            )

    def test_final_roadmap_section_closeout_omits_nonexistent_next_draft(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_terminal_scope_roadmap(
                root,
                ["FS-11", "FS-12", "FS-13"],
            )
            section = "FS-13"
            manifest = self._terminal_scope_manifest(section)
            actual = VALIDATOR._git_integrity_control_paths(
                "CLOSEOUT_APPLICATION_CONTROL",
                manifest,
                manifest,
                section,
                root,
            )
            expected = {
                ".floppy/START-HERE.md",
                ".floppy/README.md",
                ".floppy/closeouts/FS-13-closeout.md",
                ".floppy/floppies/Floppy-D-Project-Map.md",
                ".floppy/floppies/Floppy-E-Current-Section.md",
                ".floppy/lifecycle-state.json",
                ".floppy/manifest.json",
                ".floppy/orchestrator-registry.json",
                ".floppy/roadmap/roadmap.json",
                ".floppy/roadmap/roadmap.md",
                ".floppy/templates/Floppy-E-FS-13.draft.md",
            }
            self.assertEqual(expected, actual)
            self.assertNotIn(
                ".floppy/templates/Floppy-E-FS-14.draft.md",
                actual,
            )

    def test_closeout_control_rejects_extra_path(self) -> None:
        td, root = self.make_repo()
        with td:
            self.commit_handoff(root)
            completion = self.completion_manifest()
            self.apply_commit(root, completion, self.HANDOFF_PATHS, "complete")
            acceptance = self.acceptance_manifest()
            self.apply_commit(root, acceptance, self.HANDOFF_PATHS, "accept")
            manifest = self.proposal_manifest()
            extra = ".floppy/floppies/Floppy-B-Development-Issues.md"
            head = self.apply_commit(
                root,
                manifest,
                [*self.PROPOSAL_PATHS, extra],
                "bad proposal",
            )
            self.assertIn(
                f"GIT_INTEGRITY_UNAUTHORIZED_PATHS: {extra}",
                self.validate(root, manifest, head, None, None),
            )


    def bounded_environment(self, head: str, scope: list[str]) -> dict[str, str]:
        env = self.environment(head, self.PROV_AUTH, self.PROV_WRITER)
        env["FLOPPY_CONTROL_OPERATION"] = "BOUNDED_VALIDATOR_CORRECTION"
        env["FLOPPY_CONTROL_SCOPE"] = json.dumps(scope)
        env["FLOPPY_CONTROL_BRANCH"] = self.BRANCH
        return env

    def test_bounded_validator_correction_exact_scope_passes(self) -> None:
        td, root = self.make_repo()
        with td:
            scope = [
                "tools/validate_floppy.py",
                "tests/test_authorization_git_integrity.py",
                "system-manifest.json",
            ]
            for relative in scope:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"baseline: {relative}\n", encoding="utf-8")
            require_git(root, "add", "--", *scope)
            require_git(root, "commit", "-m", "correction baseline")
            for relative in scope:
                with (root / relative).open("a", encoding="utf-8") as handle:
                    handle.write("bounded correction\n")
            require_git(root, "add", "--", *scope)
            require_git(root, "commit", "-m", "bounded correction")
            head = require_git(root, "rev-parse", "HEAD")
            manifest = json.loads(
                (root / ".floppy/manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                [],
                VALIDATOR.validate_authorization_git_integrity(
                    root,
                    manifest,
                    self.bounded_environment(head, scope),
                ),
            )


    def test_bounded_validator_correction_exact_pre_fs12_pc2_scope_passes(self) -> None:
        td, root = self.make_repo()
        with td:
            scope = [
                "specs/lifecycle-transition-table.json",
                "tools/validate_floppy.py",
                "tests/test_lifecycle_specification.py",
                "tests/test_authorization_git_integrity.py",
                "system-manifest.json",
            ]
            for relative in scope:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"baseline: {relative}\n", encoding="utf-8")
            require_git(root, "add", "--", *scope)
            require_git(root, "commit", "-m", "pre-fs12 correction baseline")
            for relative in scope:
                with (root / relative).open("a", encoding="utf-8") as handle:
                    handle.write("pre-fs12 bounded correction\n")
            require_git(root, "add", "--", *scope)
            require_git(root, "commit", "-m", "pre-fs12 bounded correction")
            head = require_git(root, "rev-parse", "HEAD")
            manifest = json.loads(
                (root / ".floppy/manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                [],
                VALIDATOR.validate_authorization_git_integrity(
                    root,
                    manifest,
                    self.bounded_environment(head, scope),
                ),
            )

    def test_bounded_validator_correction_transition_table_requires_exact_pre_fs12_scope(self) -> None:
        td, root = self.make_repo()
        with td:
            scope = [
                "specs/lifecycle-transition-table.json",
                "tools/validate_floppy.py",
                "tests/test_lifecycle_specification.py",
                "system-manifest.json",
            ]
            for relative in scope:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"bounded: {relative}\n", encoding="utf-8")
            require_git(root, "add", "--", *scope)
            require_git(root, "commit", "-m", "incomplete pre-fs12 correction")
            head = require_git(root, "rev-parse", "HEAD")
            manifest = json.loads(
                (root / ".floppy/manifest.json").read_text(encoding="utf-8")
            )
            self.assertIn(
                "GIT_INTEGRITY_BOUNDED_CORRECTION_SCOPE_FORBIDDEN",
                VALIDATOR.validate_authorization_git_integrity(
                    root,
                    manifest,
                    self.bounded_environment(head, scope),
                ),
            )

    def test_bounded_validator_correction_passes_without_active_authority(self) -> None:
        td, root = self.make_repo()
        with td:
            self.commit_handoff(root)
            completion = self.completion_manifest()
            self.apply_commit(root, completion, self.HANDOFF_PATHS, "complete")
            acceptance = self.acceptance_manifest()
            self.apply_commit(root, acceptance, self.HANDOFF_PATHS, "accept")
            scope = [
                "tools/validate_floppy.py",
                "tests/test_authorization_git_integrity.py",
                "system-manifest.json",
            ]
            for relative in scope:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"baseline: {{relative}}\n", encoding="utf-8")
            require_git(root, "add", "--", *scope)
            require_git(root, "commit", "-m", "no-authority correction baseline")
            for relative in scope:
                with (root / relative).open("a", encoding="utf-8") as handle:
                    handle.write("bounded no-authority correction\n")
            require_git(root, "add", "--", *scope)
            require_git(root, "commit", "-m", "bounded no-authority correction")
            head = require_git(root, "rev-parse", "HEAD")
            manifest = json.loads(
                (root / ".floppy/manifest.json").read_text(encoding="utf-8")
            )
            environment = {
                "FLOPPY_EXPECTED_HEAD": head,
                "FLOPPY_SCOPE_COMMIT": head,
                "FLOPPY_CONTROL_OPERATION": "BOUNDED_VALIDATOR_CORRECTION",
                "FLOPPY_CONTROL_SCOPE": json.dumps(scope),
                "FLOPPY_CONTROL_BRANCH": self.BRANCH,
            }
            self.assertEqual(
                [],
                VALIDATOR.validate_authorization_git_integrity(
                    root,
                    manifest,
                    environment,
                ),
            )

    def test_closeout_proposal_uses_explicit_control_branch_without_recorded_branch(self) -> None:
        td, root = self.make_repo()
        with td:
            self.commit_handoff(root)
            completion = self.completion_manifest()
            self.apply_commit(root, completion, self.HANDOFF_PATHS, "complete")
            acceptance = self.acceptance_manifest()
            self.apply_commit(root, acceptance, self.HANDOFF_PATHS, "accept")
            proposal = self.proposal_manifest()
            proposal["fs_11_work_package"].pop("branch", None)
            head = self.apply_commit(
                root,
                proposal,
                self.PROPOSAL_PATHS,
                "proposal without recorded branch",
            )
            environment = self.environment(head, None, None)
            environment["FLOPPY_CONTROL_BRANCH"] = self.BRANCH
            self.assertEqual(
                [],
                VALIDATOR.validate_authorization_git_integrity(
                    root,
                    proposal,
                    environment,
                ),
            )

    def test_bounded_validator_correction_rejects_non_test_product_path(self) -> None:
        td, root = self.make_repo()
        with td:
            scope = [
                "tools/validate_floppy.py",
                "README.md",
                "system-manifest.json",
            ]
            for relative in scope:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("a", encoding="utf-8") as handle:
                    handle.write("bounded correction\n")
            require_git(root, "add", "--", *scope)
            require_git(root, "commit", "-m", "bad bounded correction")
            head = require_git(root, "rev-parse", "HEAD")
            manifest = json.loads(
                (root / ".floppy/manifest.json").read_text(encoding="utf-8")
            )
            self.assertIn(
                "GIT_INTEGRITY_BOUNDED_CORRECTION_SCOPE_FORBIDDEN",
                VALIDATOR.validate_authorization_git_integrity(
                    root,
                    manifest,
                    self.bounded_environment(head, scope),
                ),
            )

    def test_bounded_validator_correction_cannot_change_manifest(self) -> None:
        td, root = self.make_repo()
        with td:
            scope = [
                "tools/validate_floppy.py",
                "tests/test_authorization_git_integrity.py",
                "system-manifest.json",
                ".floppy/manifest.json",
            ]
            for relative in scope[:-1]:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"bounded: {relative}\n", encoding="utf-8")
            manifest = json.loads(
                (root / ".floppy/manifest.json").read_text(encoding="utf-8")
            )
            manifest["unexpected"] = True
            self.write_json(root / ".floppy/manifest.json", manifest)
            require_git(root, "add", "--", *scope)
            require_git(root, "commit", "-m", "manifest mutation")
            head = require_git(root, "rev-parse", "HEAD")
            errors = VALIDATOR.validate_authorization_git_integrity(
                root,
                manifest,
                self.bounded_environment(head, scope),
            )
            self.assertIn(
                "GIT_INTEGRITY_BOUNDED_CORRECTION_SCOPE_FORBIDDEN",
                errors,
            )
            self.assertIn(
                "GIT_INTEGRITY_BOUNDED_CORRECTION_MANIFEST_CHANGED",
                errors,
            )


if __name__ == "__main__":
    unittest.main()
