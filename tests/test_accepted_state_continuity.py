from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_floppy.py"
SCHEMA_PATH = ROOT / "schemas" / "bce" / "2.0.0" / "bce-accepted-state.schema.json"
SPEC_PATH = ROOT / "specs" / "accepted-state-continuity.md"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_floppy_v2_03", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load V2-03 validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


def protected(label: str) -> dict:
    return {
        "project_origin": {"kind": "test", "name": "α-project"},
        "original_intent": f"Preserve {label}",
        "accepted_scope": {"included": ["one", "two"]},
        "accepted_plan": {"path": ".floppy/roadmap/roadmap.json", "revision": label},
        "accepted_exclusions": ["silent reconstruction"],
        "major_constraints": ["no authority by existence"],
        "verified_starting_state": {"label": label},
    }


def acceptance(decision: str = "ACCEPT") -> dict:
    return {
        "status": "ACCEPTED",
        "authority": "TEST_ADMINISTRATOR",
        "accepted_at": "2026-08-10T12:00:00-05:00",
        "decision": decision,
    }


def revision(revision_id: str, state: dict, supersedes: str | None = None) -> dict:
    value = {
        "revision_id": revision_id,
        "accepted_checkpoint": "1" * 40,
        "administrator_acceptance": acceptance(),
        "protected_state": state,
        "protected_state_sha256": VALIDATOR.canonical_v2_protected_state_sha256(state),
    }
    if supersedes is not None:
        value["supersedes_revision_id"] = supersedes
    return value


def record() -> dict:
    original_state = protected("original")
    return {
        "format": "floppy-accepted-state",
        "format_version": 1,
        "project_id": str(uuid.uuid4()),
        "original": revision("ORIGINAL", original_state),
        "revisions": [],
        "current_accepted_revision": "ORIGINAL",
        "authority_isolation": {
            "grants_implementation_authority": False,
            "grants_repository_writer": False,
            "grants_migration_authority": False,
            "grants_integration_authority": False,
            "grants_release_authority": False,
        },
    }


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


class AcceptedStateContinuityTests(unittest.TestCase):
    def test_schema_and_source_registration_exist(self) -> None:
        self.assertTrue(SCHEMA_PATH.is_file())
        self.assertTrue(SPEC_PATH.is_file())
        system = json.loads((ROOT / "system-manifest.json").read_text(encoding="utf-8"))
        registry = system["accepted_state_continuity"]
        self.assertEqual(registry["owner"], "V2-03")
        self.assertEqual(registry["runtime_record"], ".floppy/accepted-state.json")
        self.assertFalse(registry["automatic_migration"])
        self.assertFalse(registry["automatic_backfill"])
        self.assertEqual(
            registry["validated_boot_package_paths_added"],
            [
                "schemas/bce/2.0.0/bce-accepted-state.schema.json",
                "specs/accepted-state-continuity.md",
            ],
        )
        self.assertFalse((ROOT / "project-seed/.floppy/accepted-state.json").exists())

    def test_hash_serialization_is_exact_and_unicode_direct(self) -> None:
        state_a = {"z": "λ", "a": {"b": 2, "a": 1}}
        state_b = {"a": {"a": 1, "b": 2}, "z": "λ"}
        expected_bytes = json.dumps(
            state_a,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        expected = hashlib.sha256(expected_bytes).hexdigest()
        self.assertEqual(VALIDATOR.canonical_v2_protected_state_sha256(state_a), expected)
        self.assertEqual(
            VALIDATOR.canonical_v2_protected_state_sha256(state_a),
            VALIDATOR.canonical_v2_protected_state_sha256(state_b),
        )
        self.assertIn("λ".encode("utf-8"), expected_bytes)
        self.assertNotIn(b"\\u03bb", expected_bytes.lower())

    def test_project_id_is_lowercase_canonical_uuid4(self) -> None:
        value = record()
        self.assertEqual(VALIDATOR.validate_v2_accepted_state_record(value), [])
        parsed = uuid.UUID(value["project_id"])
        self.assertEqual(parsed.version, 4)
        self.assertEqual(str(parsed), value["project_id"])
        broken = copy.deepcopy(value)
        broken["project_id"] = value["project_id"].upper()
        errors = VALIDATOR.validate_v2_accepted_state_record(broken)
        self.assertIn("ACCEPTED_STATE_PROJECT_ID_INVALID", errors)

    def test_roles_are_derived_without_rewriting_history(self) -> None:
        value = record()
        first = revision("R1", protected("r1"), "ORIGINAL")
        value["revisions"].append(first)
        value["current_accepted_revision"] = "R1"
        roles = VALIDATOR.resolve_v2_accepted_state_roles(value)
        self.assertEqual(roles["original_revision"], "ORIGINAL")
        self.assertEqual(roles["current_accepted_revision"], "R1")
        self.assertEqual(roles["superseded_but_historical"], ["ORIGINAL"])
        self.assertEqual(VALIDATOR.validate_v2_accepted_state_record(value), [])

    def test_lawful_append_preserves_prior_revision_objects(self) -> None:
        before = record()
        r1 = revision("R1", protected("r1"), "ORIGINAL")
        before["revisions"] = [r1]
        before["current_accepted_revision"] = "R1"
        after = copy.deepcopy(before)
        r2 = revision("R2", protected("r2"), "R1")
        after["revisions"].append(r2)
        after["current_accepted_revision"] = "R2"
        self.assertEqual(
            VALIDATOR.validate_v2_accepted_state_record(after, previous_record=before),
            [],
        )
        self.assertEqual(after["revisions"][0], before["revisions"][0])

    def test_history_rewrite_is_distinct(self) -> None:
        before = record()
        after = copy.deepcopy(before)
        after["original"]["protected_state"]["original_intent"] = "rewritten"
        after["original"]["protected_state_sha256"] = VALIDATOR.canonical_v2_protected_state_sha256(
            after["original"]["protected_state"]
        )
        errors = VALIDATOR.validate_v2_accepted_state_record(after, previous_record=before)
        self.assertIn("ACCEPTED_STATE_HISTORY_REWRITE", errors)

    def test_silent_drift_is_distinct(self) -> None:
        value = record()
        value["original"]["protected_state_sha256"] = "0" * 64
        errors = VALIDATOR.validate_v2_accepted_state_record(value)
        self.assertIn("ACCEPTED_STATE_SILENT_DRIFT", errors)

    def test_authority_isolation_is_enforced(self) -> None:
        value = record()
        value["authority_isolation"]["grants_repository_writer"] = True
        errors = VALIDATOR.validate_v2_accepted_state_record(value)
        self.assertIn("ACCEPTED_STATE_AUTHORITY_ISOLATION_VIOLATION", errors)

    def test_legacy_absence_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".floppy").mkdir()
            errors: list[str] = []
            VALIDATOR.validate_v2_accepted_state_continuity_project(root, {}, errors)
            self.assertEqual(errors, [])
            self.assertFalse((root / ".floppy/accepted-state.json").exists())

    def test_active_missing_record_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".floppy").mkdir()
            manifest = {
                "accepted_state_continuity": {
                    "status": "ACTIVE",
                    "contract_version": "2.0.0",
                    "record": ".floppy/accepted-state.json",
                    "schema": "schemas/bce/2.0.0/bce-accepted-state.schema.json",
                }
            }
            errors: list[str] = []
            VALIDATOR.validate_v2_accepted_state_continuity_project(root, manifest, errors)
            self.assertIn("ACCEPTED_STATE_REQUIRED_RECORD_MISSING", errors)

    def test_unregistered_record_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".floppy").mkdir()
            (root / ".floppy/accepted-state.json").write_text(
                json.dumps(record(), ensure_ascii=False), encoding="utf-8"
            )
            errors: list[str] = []
            VALIDATOR.validate_v2_accepted_state_continuity_project(root, {}, errors)
            self.assertIn("ACCEPTED_STATE_UNREGISTERED_RECORD", errors)

    def test_committed_activation_removal_is_repository_backed_drift(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".floppy").mkdir()
            active = {
                "status": "ACTIVE",
                "contract_version": "2.0.0",
                "record": ".floppy/accepted-state.json",
                "schema": "schemas/bce/2.0.0/bce-accepted-state.schema.json",
            }
            manifest_path = root / ".floppy/manifest.json"
            record_path = root / ".floppy/accepted-state.json"
            manifest_path.write_text(
                json.dumps({"accepted_state_continuity": active}, ensure_ascii=False),
                encoding="utf-8",
            )
            record_path.write_text(json.dumps(record(), ensure_ascii=False), encoding="utf-8")
            git(root, "init")
            git(root, "config", "user.name", "V2-03 Test")
            git(root, "config", "user.email", "v2-03@example.invalid")
            git(root, "add", ".")
            git(root, "commit", "-m", "activate accepted state")
            manifest_path.write_text("{}", encoding="utf-8")
            record_path.unlink()
            errors: list[str] = []
            VALIDATOR.validate_v2_accepted_state_continuity_project(root, {}, errors)
            self.assertIn("ACCEPTED_STATE_SILENT_DRIFT", errors)




# V2_05_ACCEPTED_STATE_OPP_LINK_TEST
class V205AcceptedStateOppLinkTests(unittest.TestCase):
    def test_normative_spec_records_opp_link_without_schema_rewrite(self) -> None:
        text = SPEC_PATH.read_text(encoding="utf-8")
        self.assertIn("V2_05_OFFICIAL_PROJECT_PLAN_LINKAGE_BEGIN", text)
        self.assertIn("OFFICIAL_PROJECT_PLAN_UNREVIEWED_SUBSTANTIVE_CHANGE", text)
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["owner"], "V2-03")

if __name__ == "__main__":
    unittest.main()
