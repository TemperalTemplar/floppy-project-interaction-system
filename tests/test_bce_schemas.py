from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from importlib.metadata import version
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_floppy.py"
FIXTURES = ROOT / "tests" / "fixtures" / "bce-schemas" / "1.0.0"

CASES = {
    "lifecycle_state": {
        "schema": ROOT
        / "schemas"
        / "bce"
        / "1.0.0"
        / "bce-lifecycle-state.schema.json",
        "id": (
            "urn:floppy-project-interaction-system:"
            "schema:bce-lifecycle-state:1.0.0"
        ),
        "valid": FIXTURES / "valid" / "lifecycle-state.json",
        "invalid": FIXTURES / "invalid" / "lifecycle-state.json",
    },
    "work_authorization": {
        "schema": ROOT
        / "schemas"
        / "bce"
        / "1.0.0"
        / "bce-work-authorization.schema.json",
        "id": (
            "urn:floppy-project-interaction-system:"
            "schema:bce-work-authorization:1.0.0"
        ),
        "valid": FIXTURES / "valid" / "work-authorization.json",
        "invalid": FIXTURES / "invalid" / "work-authorization.json",
    },
    "lifecycle_transition": {
        "schema": ROOT
        / "schemas"
        / "bce"
        / "1.0.0"
        / "bce-lifecycle-transition.schema.json",
        "id": (
            "urn:floppy-project-interaction-system:"
            "schema:bce-lifecycle-transition:1.0.0"
        ),
        "valid": FIXTURES / "valid" / "lifecycle-transition.json",
        "invalid": FIXTURES / "invalid" / "lifecycle-transition.json",
    },
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_validator_module():
    spec = importlib.util.spec_from_file_location(
        "floppy_validator",
        VALIDATOR_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load tools/validate_floppy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BceSchemaTests(unittest.TestCase):
    def test_jsonschema_draft_2020_12_support_is_available(self) -> None:
        self.assertTrue(version("jsonschema"))
        self.assertEqual(
            Draft202012Validator.META_SCHEMA["$id"],
            "https://json-schema.org/draft/2020-12/schema",
        )

    def test_normative_schemas_are_registered_with_exact_digests(self) -> None:
        manifest = load_json(ROOT / "system-manifest.json")
        registry = manifest["normative_bce_schemas"]

        self.assertEqual(registry["section"], "FS-02")
        self.assertEqual(registry["status"], "reusable_product")
        self.assertEqual(registry["schema_version"], "1.0.0")
        self.assertEqual(registry["json_schema_draft"], "2020-12")
        self.assertFalse(registry["ordinary_operation_required"])
        self.assertFalse(registry["production_enforcement"])
        self.assertEqual(
            registry["validation_scope"],
            "development_and_verification_only",
        )
        self.assertEqual(registry["validator"], "tools/validate_floppy.py")
        self.assertEqual(set(registry["artifacts"]), set(CASES))

        validator = load_validator_module()
        for key, case in CASES.items():
            record = registry["artifacts"][key]
            self.assertEqual(
                record["path"],
                case["schema"].relative_to(ROOT).as_posix(),
            )
            self.assertEqual(record["$id"], case["id"])
            self.assertEqual(
                record["sha256"],
                validator.sha256(case["schema"]),
            )

    def test_each_schema_accepts_valid_and_rejects_invalid_fixture(self) -> None:
        for key, case in CASES.items():
            schema = load_json(case["schema"])
            Draft202012Validator.check_schema(schema)

            with self.subTest(schema=key, fixture="valid"):
                self.assertEqual(
                    schema["$schema"],
                    "https://json-schema.org/draft/2020-12/schema",
                )
                self.assertEqual(schema["$id"], case["id"])
                Draft202012Validator(schema).validate(
                    load_json(case["valid"])
                )

            with self.subTest(schema=key, fixture="invalid"):
                with self.assertRaises(ValidationError):
                    Draft202012Validator(schema).validate(
                        load_json(case["invalid"])
                    )

    def test_existing_validator_accepts_normative_registry_and_schemas(
        self,
    ) -> None:
        validator = load_validator_module()
        errors: list[str] = []
        validator.validate_normative_bce_schemas(
            ROOT,
            load_json(ROOT / "system-manifest.json"),
            errors,
        )
        self.assertEqual(errors, [])

    def test_existing_validator_rejects_bad_registered_digest(self) -> None:
        validator = load_validator_module()
        manifest = load_json(ROOT / "system-manifest.json")
        manifest["normative_bce_schemas"]["artifacts"][
            "lifecycle_state"
        ]["sha256"] = "0" * 64

        errors: list[str] = []
        validator.validate_normative_bce_schemas(
            ROOT,
            manifest,
            errors,
        )
        self.assertTrue(
            any("digest does not match" in error for error in errors),
            errors,
        )

    def test_validator_import_does_not_import_jsonschema(self) -> None:
        code = (
            "import importlib.util, pathlib, sys; "
            "path = pathlib.Path(sys.argv[1]); "
            "spec = importlib.util.spec_from_file_location('validator', path); "
            "module = importlib.util.module_from_spec(spec); "
            "spec.loader.exec_module(module); "
            "raise SystemExit(1 if 'jsonschema' in sys.modules else 0)"
        )
        result = subprocess.run(
            [sys.executable, "-I", "-c", code, str(VALIDATOR_PATH)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            result.stdout + result.stderr,
        )

    def test_ctrl02_lifecycle_state_extension(self) -> None:
        schema_path = ROOT / "schemas" / "bce" / "1.1.0" / "bce-lifecycle-state.schema.json"
        fixture_root = ROOT / "tests" / "fixtures" / "bce-schemas" / "1.1.0"
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(load_json(fixture_root / "valid" / "lifecycle-state.json"))
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(load_json(fixture_root / "invalid" / "lifecycle-state.json"))
        legacy = load_json(CASES["lifecycle_state"]["schema"])
        with self.assertRaises(ValidationError):
            Draft202012Validator(legacy).validate(load_json(fixture_root / "valid" / "lifecycle-state.json"))

    def test_ctrl02_registry_digest(self) -> None:
        manifest = load_json(ROOT / "system-manifest.json")
        registry = manifest["verification_only_lifecycle_extension"]
        record = registry["artifacts"]["lifecycle_state"]
        path = ROOT / record["path"]
        self.assertEqual(record["sha256"], load_validator_module().sha256(path))


if __name__ == "__main__":
    unittest.main()
