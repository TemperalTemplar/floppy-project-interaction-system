from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "tools" / "initialize_project.py"
VALIDATE = ROOT / "tools" / "validate_floppy.py"


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
            self.assertEqual(manifest["system"]["version"], "0.4.2-dev")
            self.assertIn("0.4.2-dev", (project / ".floppy/START-HERE.md").read_text(encoding="utf-8"))
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


if __name__ == "__main__":
    unittest.main()
