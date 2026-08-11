from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
import uuid
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools/validate_floppy.py"
CONTINUITY_SCHEMA = (
    ROOT / "schemas/bce/2.0.0/bce-continuity-overseer.schema.json"
)
SUCCESSION_SCHEMA = (
    ROOT / "schemas/bce/2.0.0/bce-orchestrator-succession.schema.json"
)


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_floppy_v2_04", VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load V2-04 validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()
AUTHORITY_ISOLATION = {
    "grants_implementation_authority": False,
    "grants_repository_writer": False,
    "grants_migration_authority": False,
    "grants_integration_authority": False,
    "grants_acceptance_authority": False,
    "grants_release_authority": False,
}


def accepted_state(project_id: str) -> dict:
    protected = {"project_origin": {"name": "test"}}
    digest = VALIDATOR.canonical_v2_protected_state_sha256(protected)
    return {
        "project_id": project_id,
        "original": {
            "revision_id": "ORIGINAL",
            "protected_state": protected,
            "protected_state_sha256": digest,
        },
        "revisions": [],
        "current_accepted_revision": "ORIGINAL",
    }


def continuity_record(project_id: str, initial: str) -> dict:
    accepted = accepted_state(project_id)
    value = {
        "format": "floppy-continuity-overseer",
        "format_version": 1,
        "project_id": project_id,
        "continuity_overseer_id": f"CO-{project_id}",
        "reports_to": "ADMINISTRATOR",
        "accepted_state": {
            "record": ".floppy/accepted-state.json",
            "origin_revision_id": "ORIGINAL",
            "origin_protected_state_sha256": accepted["original"][
                "protected_state_sha256"
            ],
            "current_accepted_revision": "ORIGINAL",
            "current_protected_state_sha256": accepted["original"][
                "protected_state_sha256"
            ],
        },
        "initial_project_orchestrator_id": initial,
        "orchestrator_registry": ".floppy/orchestrator-registry.json",
        "shared_origin_sha256": "",
        "succession_history": [],
        "authority_isolation": dict(AUTHORITY_ISOLATION),
    }
    value["shared_origin_sha256"] = VALIDATOR.canonical_v2_continuity_sha256(
        VALIDATOR.v2_shared_origin_projection(value)
    )
    return value


def authority_state() -> dict:
    return {
        "lifecycle_state": "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE",
        "active_work_authorization": None,
        "active_implementation_authorization": None,
        "active_implementation_section": None,
        "current_section_working_model": None,
        "repository_writer": None,
        "writer_authorization_reference": None,
    }


def succession(project_id: str) -> dict:
    state = authority_state()
    successor = f"ORCH-{project_id}-00000002"
    return {
        "format": "floppy-orchestrator-succession",
        "format_version": 1,
        "succession_id": "ORCH-SUCC-000001",
        "sequence": 1,
        "project_id": project_id,
        "continuity_overseer_id": f"CO-{project_id}",
        "predecessor_orchestrator_id": f"ORCH-{project_id}-00000001",
        "successor_orchestrator_id": successor,
        "predecessor_availability": "AVAILABLE",
        "recovery_mode": "NORMAL",
        "repository_checkpoint": {
            "repository": "owner/project",
            "branch": "main",
            "checkpoint": "1" * 40,
        },
        "authority_state": state,
        "authority_state_sha256": VALIDATOR.canonical_v2_continuity_sha256(
            state
        ),
        "phase": "PREPARED",
        "readiness": {
            "predecessor_status": "ACTIVE",
            "successor_status": "HANDOFF_PENDING",
            "successor_readiness_verified": False,
        },
        "administrator_cutover": {
            "status": "PENDING",
            "decision": None,
        },
        "result": None,
        "completed_work": ["accepted work preserved"],
        "unresolved_work": ["next work preserved"],
        "next_legal_operation": "VERIFY_SUCCESSOR_READINESS",
        "prohibited_operations": ["automatic authority transfer"],
        "authority_isolation": dict(AUTHORITY_ISOLATION),
    }


class ContinuityOverseerTests(unittest.TestCase):
    def test_schemas_are_draft_2020_12_and_valid(self) -> None:
        for path in (CONTINUITY_SCHEMA, SUCCESSION_SCHEMA):
            value = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(
                value["$schema"],
                "https://json-schema.org/draft/2020-12/schema",
            )
            Draft202012Validator.check_schema(value)

    def test_identity_and_shared_origin_are_deterministic(self) -> None:
        project_id = str(uuid.uuid4())
        initial = f"ORCH-{project_id}-00000001"
        accepted = accepted_state(project_id)
        value = continuity_record(project_id, initial)
        self.assertEqual(
            VALIDATOR.validate_v2_continuity_overseer_record(
                value, accepted_state=accepted
            ),
            [],
        )
        self.assertEqual(value["continuity_overseer_id"], f"CO-{project_id}")
        self.assertNotIn("current_orchestrator", value)

    def test_shared_origin_drift_fails(self) -> None:
        project_id = str(uuid.uuid4())
        initial = f"ORCH-{project_id}-00000001"
        value = continuity_record(project_id, initial)
        value["shared_origin_sha256"] = "0" * 64
        errors = VALIDATOR.validate_v2_continuity_overseer_record(value)
        self.assertIn("CONTINUITY_OVERSEER_SHARED_ORIGIN_MISMATCH", errors)

    def test_succession_history_is_append_only(self) -> None:
        project_id = str(uuid.uuid4())
        initial = f"ORCH-{project_id}-00000001"
        before = continuity_record(project_id, initial)
        before["succession_history"] = ["ORCH-SUCC-000001"]
        after = copy.deepcopy(before)
        after["succession_history"].append("ORCH-SUCC-000002")
        self.assertEqual(
            VALIDATOR.validate_v2_continuity_overseer_record(
                after, previous_record=before
            ),
            [],
        )
        rewritten = copy.deepcopy(after)
        rewritten["succession_history"] = ["ORCH-SUCC-000002"]
        self.assertIn(
            "CONTINUITY_OVERSEER_SILENT_DRIFT",
            VALIDATOR.validate_v2_continuity_overseer_record(
                rewritten, previous_record=before
            ),
        )

    def test_prepared_succession_preserves_authority(self) -> None:
        project_id = str(uuid.uuid4())
        value = succession(project_id)
        self.assertEqual(
            VALIDATOR.validate_v2_orchestrator_succession_record(
                value, current_authority_state=authority_state()
            ),
            [],
        )

    def test_stale_succession_stops(self) -> None:
        project_id = str(uuid.uuid4())
        value = succession(project_id)
        changed = authority_state()
        changed["repository_writer"] = "DIFFERENT_WRITER"
        errors = VALIDATOR.validate_v2_orchestrator_succession_record(
            value,
            current_authority_state=changed,
        )
        self.assertIn("STALE_SUCCESSION_HANDOFF", errors)

    def test_recovery_mode_requires_unavailable_predecessor(self) -> None:
        project_id = str(uuid.uuid4())
        value = succession(project_id)
        value["predecessor_availability"] = "UNAVAILABLE"
        value["recovery_mode"] = "REPOSITORY_BACKED"
        self.assertEqual(
            VALIDATOR.validate_v2_orchestrator_succession_record(value),
            [],
        )

    def test_applied_cutover_has_one_successor_current(self) -> None:
        project_id = str(uuid.uuid4())
        value = succession(project_id)
        value["phase"] = "APPLIED"
        value["readiness"] = {
            "predecessor_status": "RETIRED",
            "successor_status": "ACTIVE",
            "successor_readiness_verified": True,
        }
        value["administrator_cutover"] = {
            "status": "ACCEPTED",
            "decision": "ACCEPT SUCCESSION",
        }
        value["result"] = {
            "predecessor_status": "RETIRED",
            "successor_status": "ACTIVE",
            "current_orchestrator": value["successor_orchestrator_id"],
        }
        self.assertEqual(
            VALIDATOR.validate_v2_orchestrator_succession_record(value),
            [],
        )

    def test_scope_drift_boundary_requires_administrator_revision(self) -> None:
        self.assertEqual(
            VALIDATOR.resolve_v2_scope_change(
                material_goal_or_fundamental_scope_conflict=False,
                accepted_project_revision_present=False,
            ),
            "ORDINARY_IMPLEMENTATION_ADAPTATION",
        )
        self.assertEqual(
            VALIDATOR.resolve_v2_scope_change(
                material_goal_or_fundamental_scope_conflict=True,
                accepted_project_revision_present=False,
            ),
            "SCOPE_DRIFT_REVIEW_REQUIRED",
        )
        self.assertEqual(
            VALIDATOR.resolve_v2_scope_change(
                material_goal_or_fundamental_scope_conflict=True,
                accepted_project_revision_present=True,
            ),
            "ACCEPTED_PROJECT_REVISION",
        )

    def test_legacy_absence_does_not_create_runtime_record(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".floppy").mkdir()
            errors: list[str] = []
            VALIDATOR.validate_v2_continuity_overseer_project(root, {}, errors)
            self.assertEqual(errors, [])
            self.assertFalse(
                (root / ".floppy/continuity-overseer.json").exists()
            )




# V2_05_OPP_CONTINUITY_TEST
class V205OppContinuityTests(unittest.TestCase):
    def test_opp_does_not_change_continuity_authority_isolation(self) -> None:
        manifest = json.loads((ROOT / "system-manifest.json").read_text(encoding="utf-8"))
        self.assertIn("official_project_plan", manifest)
        self.assertEqual(manifest["official_project_plan"]["owner"], "V2-05")
        self.assertEqual(manifest["continuity_overseer"]["authority_isolation"], AUTHORITY_ISOLATION)

if __name__ == "__main__":
    unittest.main()
