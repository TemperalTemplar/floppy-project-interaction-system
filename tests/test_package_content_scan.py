from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "tools" / "floppyctl.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("floppyctl_fs07", CLI_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load tools/floppyctl.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CLI = load_cli()


def write_tree(root: Path) -> None:
    (root / "content" / "nested").mkdir(parents=True)
    (root / "content" / "alpha.txt").write_text("alpha", encoding="utf-8")
    (root / "content" / "nested" / "beta.txt").write_text(
        "beta",
        encoding="utf-8",
    )


def tree_digest(root: Path) -> dict[str, str]:
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


class PackageContentScanTests(unittest.TestCase):
    def run_cli(
        self,
        repository: Path,
        scan_root: str,
        *,
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(CLI_PATH),
                "--root",
                str(repository),
                "scan",
                scan_root,
            ],
            cwd=cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )

    def payload(self, result: subprocess.CompletedProcess[str]) -> dict:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout)

    def test_empty_scan_input(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = self.run_cli(root, ".")
            self.assertEqual(
                self.payload(result),
                {"entries": [], "scan_root": "."},
            )

    def test_nested_content_and_types(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_tree(root)
            payload = self.payload(self.run_cli(root, "content"))
            self.assertEqual(
                payload,
                {
                    "entries": [
                        {"path": "content/alpha.txt", "type": "file"},
                        {"path": "content/nested", "type": "directory"},
                        {
                            "path": "content/nested/beta.txt",
                            "type": "file",
                        },
                    ],
                    "scan_root": "content",
                },
            )

    def test_deterministic_ordering(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_tree(root)
            (root / "content" / "zeta.txt").write_text("z", encoding="utf-8")
            entries = CLI.scan_package_content(root, root / "content")
            self.assertEqual(
                [entry["path"] for entry in entries],
                sorted(entry["path"] for entry in entries),
            )

    def test_filesystem_enumeration_order_independence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_tree(root)
            normal = CLI.scan_package_content(root, root / "content")

            def reverse_scandir(path: Path):
                return reversed(list(os.scandir(path)))

            reversed_result = CLI.scan_package_content(
                root,
                root / "content",
                scandir=reverse_scandir,
            )
            self.assertEqual(reversed_result, normal)

    def test_repeated_identical_execution(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_tree(root)
            first = self.run_cli(root, "content")
            second = self.run_cli(root, "content")
            self.assertEqual(first.returncode, 0)
            self.assertEqual(first.stdout, second.stdout)
            self.assertEqual(first.stderr, second.stderr)

    def test_timestamp_changes_do_not_change_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_tree(root)
            target = root / "content" / "alpha.txt"
            first = self.run_cli(root, "content")
            metadata = target.stat()
            os.utime(
                target,
                (metadata.st_atime + 120, metadata.st_mtime + 120),
            )
            second = self.run_cli(root, "content")
            self.assertEqual(first.returncode, 0)
            self.assertEqual(first.stdout, second.stdout)
            self.assertEqual(first.stderr, second.stderr)

    def test_absolute_checkout_location_independence(self) -> None:
        with tempfile.TemporaryDirectory() as first_td, tempfile.TemporaryDirectory() as second_td:
            first = Path(first_td)
            second = Path(second_td)
            write_tree(first)
            write_tree(second)
            first_payload = self.payload(self.run_cli(first, "content"))
            second_payload = self.payload(self.run_cli(second, "content"))
            self.assertEqual(first_payload, second_payload)

    def test_current_working_directory_independence(self) -> None:
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as cwd_td:
            root = Path(td)
            write_tree(root)
            normal = self.run_cli(root, "content", cwd=root)
            elsewhere = self.run_cli(root, "content", cwd=Path(cwd_td))
            self.assertEqual(normal.returncode, 0)
            self.assertEqual(normal.stdout, elsewhere.stdout)
            self.assertEqual(normal.stderr, elsewhere.stderr)

    def test_windows_and_repository_separators_match(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_tree(root)
            forward = self.run_cli(root, "content/nested")
            backward = self.run_cli(root, r"content\nested")
            self.assertEqual(forward.returncode, 0)
            self.assertEqual(forward.stdout, backward.stdout)
            self.assertEqual(forward.stderr, backward.stderr)

    def test_path_normalization(self) -> None:
        self.assertEqual(
            CLI._normalized_repository_path(r"alpha\beta\file.txt"),
            "alpha/beta/file.txt",
        )
        self.assertEqual(
            CLI._finalize_scan_entries(
                [
                    {"path": r"zeta\file.txt", "type": "file"},
                    {"path": "alpha", "type": "directory"},
                ]
            ),
            [
                {"path": "alpha", "type": "directory"},
                {"path": "zeta/file.txt", "type": "file"},
            ],
        )

    def test_escaping_scan_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            root.mkdir()
            outside = root.parent / "outside"
            outside.mkdir()
            relative = self.run_cli(root, "../outside")
            absolute = self.run_cli(root, str(outside))
            for result in (relative, absolute):
                self.assertEqual(result.returncode, 2)
                self.assertEqual(
                    result.stderr,
                    "ERROR: scan root escapes repository root\n",
                )

    def test_scan_root_must_be_directory(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "file.txt"
            target.write_text("data", encoding="utf-8")
            result = self.run_cli(root, "file.txt")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(
                result.stderr,
                "ERROR: scan root is not a directory: file.txt\n",
            )

    def test_symlink_is_rejected_without_following(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            outside = Path(td) / "outside"
            root.mkdir()
            outside.mkdir()
            (outside / "secret.txt").write_text("secret", encoding="utf-8")
            link = root / "linked"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable")
            result = self.run_cli(root, ".")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(
                result.stderr,
                "ERROR: unsafe scan link or reparse point: linked\n",
            )
            self.assertNotIn("secret.txt", result.stdout + result.stderr)

    def test_reparse_point_attribute_is_rejected(self) -> None:
        fake = mock.Mock()
        fake.st_file_attributes = stat.FILE_ATTRIBUTE_REPARSE_POINT
        self.assertTrue(CLI._is_reparse_stat(fake))

    def test_duplicate_logical_path_diagnostic_is_deterministic(self) -> None:
        entries = [
            {"path": "zeta", "type": "file"},
            {"path": "alpha", "type": "file"},
            {"path": "zeta", "type": "file"},
            {"path": "alpha", "type": "file"},
        ]
        with self.assertRaisesRegex(
            CLI.CliError,
            "^duplicate logical scan path: alpha$",
        ):
            CLI._finalize_scan_entries(entries)
        with self.assertRaisesRegex(
            CLI.CliError,
            "^duplicate logical scan path: alpha$",
        ):
            CLI._finalize_scan_entries(list(reversed(entries)))

    def test_case_collision_diagnostic_is_deterministic(self) -> None:
        entries = [
            {"path": "Other", "type": "file"},
            {"path": "other", "type": "file"},
            {"path": "Alpha", "type": "file"},
            {"path": "alpha", "type": "file"},
        ]
        with self.assertRaisesRegex(
            CLI.CliError,
            "^scan path case collision: Alpha, alpha$",
        ):
            CLI._finalize_scan_entries(entries)
        with self.assertRaisesRegex(
            CLI.CliError,
            "^scan path case collision: Alpha, alpha$",
        ):
            CLI._finalize_scan_entries(list(reversed(entries)))

    def test_scan_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_tree(root)
            before = tree_digest(root)
            first = self.run_cli(root, "content")
            second = self.run_cli(root, "content")
            after = tree_digest(root)
            self.assertEqual(first.returncode, 0)
            self.assertEqual(second.returncode, 0)
            self.assertEqual(before, after)

    def test_scan_argument_errors_are_concise(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            missing = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(CLI_PATH),
                    "--root",
                    str(root),
                    "scan",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            extra = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(CLI_PATH),
                    "--root",
                    str(root),
                    "scan",
                    ".",
                    "extra",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            for result in (missing, extra):
                self.assertEqual(result.returncode, 2)
                self.assertEqual(
                    result.stderr,
                    "ERROR: scan requires exactly one scan root\n",
                )


if __name__ == "__main__":
    unittest.main()
