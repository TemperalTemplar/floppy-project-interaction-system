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


if __name__ == "__main__":
    unittest.main()
