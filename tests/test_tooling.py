from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "tools" / "initialize_project.py"
VALIDATE = ROOT / "tools" / "validate_floppy.py"

def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_floppy_v2_progression",
        VALIDATE,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load tools/validate_floppy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


class ToolingTests(unittest.TestCase):
    def run_cmd(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_source_validates(self) -> None:
        result = self.run_cmd(str(VALIDATE), str(ROOT), "--mode", "source")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_v2_development_source_identity(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        manifest = json.loads(
            (ROOT / "system-manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(version, "2.0.0-dev")
        self.assertEqual(manifest["system_version"], "2.0.0-dev")
        self.assertEqual(manifest["status"], "development")
        self.assertEqual(
            manifest["v2_compatibility_profile"]["profile_version"],
            "2.0.0",
        )

    def test_initialize_and_validate_project(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / "sample-project"
            project.mkdir()
            result = self.run_cmd(
                str(INIT),
                "--target", str(project),
                "--project-name", "Sample Project",
                "--source-repository", "owner/floppy-source",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads((project / ".floppy/manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["project_name"], "Sample Project")
            self.assertEqual(manifest["system"]["source_repository"], "owner/floppy-source")
            self.assertEqual(manifest["system"]["version"], "2.0.0-dev")
            self.assertIn("2.0.0-dev", (project / ".floppy/START-HERE.md").read_text(encoding="utf-8"))
            validation = self.run_cmd(str(VALIDATE), str(project), "--mode", "project")
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)

    def test_refuses_existing_floppy_directory(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / "sample-project"
            (project / ".floppy").mkdir(parents=True)
            marker = project / ".floppy" / "marker.txt"
            marker.write_text("keep", encoding="utf-8")
            result = self.run_cmd(
                str(INIT),
                "--target", str(project),
                "--project-name", "Sample Project",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / "sample-project"
            project.mkdir()
            result = self.run_cmd(
                str(INIT),
                "--target", str(project),
                "--project-name", "Sample Project",
                "--dry-run",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((project / ".floppy").exists())


class V2DevelopmentProgressionTests(unittest.TestCase):
    IDS = ("V2-01", "V2-02", "V2-03", "V2-04", "V2-05")

    def validate(self, current: str, statuses: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan_path = root / ".floppy" / "roadmap" / "Floppy-V2-Project-Plan.json"
            plan_path.parent.mkdir(parents=True, exist_ok=True)
            plan_path.write_text(
                json.dumps(
                    {"work_packages": [{"id": identifier} for identifier in self.IDS]},
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            manifest = {
                "roadmap": {
                    "current_work_package": current,
                    "machine_readable": ".floppy/roadmap/Floppy-V2-Project-Plan.json",
                },
                "v2_work_packages": dict(statuses),
            }
            errors: list[str] = []
            VALIDATOR._validate_v2_development_work_package_progression(
                root,
                manifest,
                errors,
            )
            return errors

    def test_v2_current_r1_projection_validates(self) -> None:
        statuses = {
            "V2-01": "CLOSED",
            "V2-02": "PLANNED_NOT_AUTHORIZED",
            "V2-03": "PLANNED_NOT_AUTHORIZED",
            "V2-04": "PLANNED_NOT_AUTHORIZED",
            "V2-05": "PLANNED_NOT_AUTHORIZED",
        }
        self.assertEqual(self.validate("V2-02", statuses), [])

    def test_v2_simulated_w1_projection_validates(self) -> None:
        statuses = {
            "V2-01": "CLOSED",
            "V2-02": "ACCEPTED_PLANNING_BASELINE",
            "V2-03": "PLANNED_NOT_AUTHORIZED",
            "V2-04": "PLANNED_NOT_AUTHORIZED",
            "V2-05": "PLANNED_NOT_AUTHORIZED",
        }
        self.assertEqual(self.validate("V2-02", statuses), [])

    def test_v2_later_package_premature_advancement_is_rejected(self) -> None:
        statuses = {
            "V2-01": "CLOSED",
            "V2-02": "ACCEPTED_PLANNING_BASELINE",
            "V2-03": "ACCEPTED_PLANNING_BASELINE",
            "V2-04": "PLANNED_NOT_AUTHORIZED",
            "V2-05": "PLANNED_NOT_AUTHORIZED",
        }
        errors = self.validate("V2-02", statuses)
        self.assertTrue(
            any("later work package advanced prematurely" in item for item in errors),
            errors,
        )

    def test_v2_closed_previous_packages_are_preserved(self) -> None:
        statuses = {
            "V2-01": "CLOSED",
            "V2-02": "CLOSED",
            "V2-03": "PLANNED_NOT_AUTHORIZED",
            "V2-04": "PLANNED_NOT_AUTHORIZED",
            "V2-05": "PLANNED_NOT_AUTHORIZED",
        }
        self.assertEqual(self.validate("V2-03", statuses), [])

    def test_v2_skipped_package_progression_is_rejected(self) -> None:
        statuses = {
            "V2-01": "CLOSED",
            "V2-02": "ACCEPTED_PLANNING_BASELINE",
            "V2-03": "PLANNED_NOT_AUTHORIZED",
            "V2-04": "PLANNED_NOT_AUTHORIZED",
            "V2-05": "PLANNED_NOT_AUTHORIZED",
        }
        errors = self.validate("V2-03", statuses)
        self.assertTrue(
            any("previous work package must remain CLOSED" in item for item in errors),
            errors,
        )

    def test_v2_later_packages_remain_inactive_for_synthetic_v2_03(self) -> None:
        statuses = {
            "V2-01": "CLOSED",
            "V2-02": "CLOSED",
            "V2-03": "ACCEPTED_PLANNING_BASELINE",
            "V2-04": "IMPLEMENTATION_IN_PROGRESS",
            "V2-05": "PLANNED_NOT_AUTHORIZED",
        }
        errors = self.validate("V2-03", statuses)
        self.assertTrue(
            any("later work package advanced prematurely" in item for item in errors),
            errors,
        )

    def test_v2_current_package_requires_lawful_operational_status(self) -> None:
        statuses = {
            "V2-01": "CLOSED",
            "V2-02": "UNKNOWN_FUTURE_STATE",
            "V2-03": "PLANNED_NOT_AUTHORIZED",
            "V2-04": "PLANNED_NOT_AUTHORIZED",
            "V2-05": "PLANNED_NOT_AUTHORIZED",
        }
        errors = self.validate("V2-02", statuses)
        self.assertTrue(
            any("current work-package status is invalid" in item for item in errors),
            errors,
        )

if __name__ == "__main__":
    unittest.main()
