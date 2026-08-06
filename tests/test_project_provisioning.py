from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
INITIALIZER_PATH = ROOT / "tools/initialize_project.py"
VALIDATOR_PATH = ROOT / "tools/validate_floppy.py"
STATE_SCHEMA_PATH = ROOT / "schemas/bce/1.0.0/bce-lifecycle-state.schema.json"


def load_initializer():
    spec = importlib.util.spec_from_file_location("initialize_project_fs11", INITIALIZER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load tools/initialize_project.py")
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


INIT = load_initializer()


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return result.stdout.strip()


class ProjectProvisioningTests(unittest.TestCase):
    def make_target(self, base: Path, name: str = "sample-project") -> Path:
        target = base / name
        target.mkdir()
        return target

    def provision(self, target: Path, **kwargs):
        return INIT.provision_project(
            target=target,
            project_name=kwargs.pop("project_name", "Sample Project"),
            source_repository=kwargs.pop("source_repository", "owner/floppy-source"),
            source_root=kwargs.pop("source_root", ROOT),
            **kwargs,
        )

    def test_dry_run_lists_lifecycle_state_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td))
            result = self.provision(target, dry_run=True)
            self.assertTrue(result.dry_run)
            self.assertIn("lifecycle-state.json", result.created_paths)
            self.assertFalse((target / ".floppy").exists())
            self.assertFalse((target / INIT.STAGE_NAME).exists())

    def test_provisions_canonical_initial_control_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td))
            result = self.provision(target)
            self.assertFalse(result.dry_run)
            floppy = target / ".floppy"
            manifest = json.loads((floppy / "manifest.json").read_text(encoding="utf-8"))
            state = json.loads((floppy / "lifecycle-state.json").read_text(encoding="utf-8"))
            registry = json.loads((floppy / "orchestrator-registry.json").read_text(encoding="utf-8"))
            self.assertEqual(state["state_id"], "LC-ONBOARDING-REQUIRED")
            self.assertEqual(state["active_implementation_sections"], [])
            self.assertEqual(state["dimensions"]["authority"], "NO_ACTIVE_WORK_AUTHORIZATION")
            self.assertFalse(manifest["control_state"]["implementation_authority"])
            self.assertIsNone(registry["current_assignments"]["repository_writer"])
            self.assertEqual(result.tree_sha256, tree_digest(floppy))

    def test_lifecycle_state_validates_against_normative_schema(self) -> None:
        schema = json.loads(STATE_SCHEMA_PATH.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td))
            self.provision(target)
            state = json.loads((target / ".floppy/lifecycle-state.json").read_text(encoding="utf-8"))
            Draft202012Validator(schema).validate(state)

    def test_manifest_registry_and_lifecycle_checkpoint_agree(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td))
            self.provision(target, project_repository="example/project")
            manifest = json.loads((target / ".floppy/manifest.json").read_text(encoding="utf-8"))
            registry = json.loads((target / ".floppy/orchestrator-registry.json").read_text(encoding="utf-8"))
            state = json.loads((target / ".floppy/lifecycle-state.json").read_text(encoding="utf-8"))
            control = manifest["control_state"]
            self.assertEqual(
                registry["project_checkpoint"],
                {key: control[key] for key in ("repository", "branch", "worktree", "checkpoint")},
            )
            self.assertEqual(state["base_checkpoint"], control["checkpoint"])

    def test_repeated_same_input_is_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td))
            first = self.provision(target)
            first_digest = tree_digest(target / ".floppy")
            shutil.rmtree(target / ".floppy")
            second = self.provision(target)
            self.assertEqual(first.created_paths, second.created_paths)
            self.assertEqual(first.tree_sha256, second.tree_sha256)
            self.assertEqual(first_digest, tree_digest(target / ".floppy"))

    def test_all_json_control_records_are_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td))
            self.provision(target)
            for relative in (
                ".floppy/manifest.json",
                ".floppy/lifecycle-state.json",
                ".floppy/orchestrator-registry.json",
            ):
                path = target / relative
                parsed = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(path.read_bytes(), INIT.canonical_json_bytes(parsed))

    def test_git_identity_is_captured(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td))
            git(target, "init")
            git(target, "config", "user.email", "fs11@example.invalid")
            git(target, "config", "user.name", "FS11 Tests")
            (target / "README.txt").write_text("fixture\n", encoding="utf-8")
            git(target, "add", "README.txt")
            git(target, "commit", "-m", "fixture")
            git(target, "remote", "add", "origin", "https://example.invalid/project.git")
            self.provision(target)
            control = json.loads((target / ".floppy/manifest.json").read_text(encoding="utf-8"))["control_state"]
            self.assertEqual(control["repository"], "https://example.invalid/project.git")
            self.assertEqual(control["checkpoint"], git(target, "rev-parse", "HEAD"))
            self.assertEqual(control["branch"], git(target, "symbolic-ref", "--short", "HEAD"))

    def test_non_git_directory_uses_explicit_local_identity(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td), "plain")
            self.provision(target)
            control = json.loads((target / ".floppy/manifest.json").read_text(encoding="utf-8"))["control_state"]
            self.assertEqual(control["repository"], "LOCAL::plain")
            self.assertIsNone(control["branch"])
            self.assertIsNone(control["checkpoint"])

    def test_project_repository_override_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td))
            self.provision(target, project_repository="TemperalTemplar/example")
            control = json.loads((target / ".floppy/manifest.json").read_text(encoding="utf-8"))["control_state"]
            self.assertEqual(control["repository"], "TemperalTemplar/example")

    def test_existing_destination_is_rejected_without_changes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td))
            existing = target / ".floppy"
            existing.mkdir()
            marker = existing / "marker.txt"
            marker.write_text("keep\n", encoding="utf-8")
            with self.assertRaises(INIT.ProvisioningError):
                self.provision(target)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep\n")

    def test_stale_stage_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td))
            (target / INIT.STAGE_NAME).mkdir()
            with self.assertRaises(INIT.ProvisioningError):
                self.provision(target)
            self.assertFalse((target / ".floppy").exists())

    def test_failure_before_install_removes_stage_and_output(self) -> None:
        def fail_hook(name, _context):
            if name == "staged-and-validated":
                raise RuntimeError("injected pre-install failure")

        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td))
            with self.assertRaises(RuntimeError):
                self.provision(target, hook=fail_hook)
            self.assertFalse((target / ".floppy").exists())
            self.assertFalse((target / INIT.STAGE_NAME).exists())

    def test_failure_after_atomic_install_rolls_back_destination(self) -> None:
        def fail_hook(name, _context):
            if name == "destination-replaced":
                raise RuntimeError("injected post-install failure")

        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td))
            with self.assertRaises(RuntimeError):
                self.provision(target, hook=fail_hook)
            self.assertFalse((target / ".floppy").exists())
            self.assertFalse((target / INIT.STAGE_NAME).exists())

    def test_blank_project_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td))
            with self.assertRaises(INIT.ProvisioningError):
                self.provision(target, project_name="   ")
            self.assertFalse((target / ".floppy").exists())

    def test_target_inside_source_repository_is_rejected(self) -> None:
        target = ROOT / ".fs11-provisioning-test-target"
        target.mkdir(exist_ok=False)
        try:
            with self.assertRaises(INIT.ProvisioningError):
                self.provision(target)
        finally:
            target.rmdir()

    def test_seed_symlink_is_rejected_where_supported(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = base / "source"
            shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            victim = source / "project-seed/.floppy/manifest.json"
            real = source / "manifest-real.json"
            real.write_bytes(victim.read_bytes())
            victim.unlink()
            try:
                victim.symlink_to(real)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            target = self.make_target(base, "target")
            with self.assertRaises(INIT.ProvisioningError):
                self.provision(target, source_root=source)
            self.assertFalse((target / ".floppy").exists())

    def test_provisioned_project_passes_project_validator(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td))
            self.provision(target)
            result = subprocess.run(
                [
                    os.fspath(Path(os.sys.executable)),
                    "-B",
                    os.fspath(VALIDATOR_PATH),
                    os.fspath(target),
                    "--mode",
                    "project",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_no_unresolved_template_tokens_remain(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = self.make_target(Path(td))
            self.provision(target)
            for path in (target / ".floppy").rglob("*"):
                if not path.is_file():
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                self.assertNotIn("{{PROJECT_NAME}}", text)
                self.assertNotIn("{{SOURCE_REPOSITORY}}", text)


if __name__ == "__main__":
    unittest.main()
