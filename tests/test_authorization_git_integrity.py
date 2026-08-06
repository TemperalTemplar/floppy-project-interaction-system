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
        ".floppy/manifest.json",
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


if __name__ == "__main__":
    unittest.main()
