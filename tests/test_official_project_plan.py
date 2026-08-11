from __future__ import annotations

import copy
import importlib.util
import json
import unittest
import uuid
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools/validate_floppy.py"
SCHEMA_PATH = ROOT / "schemas/bce/2.0.0/bce-official-project-plan.schema.json"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_floppy_v2_05_opp", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load V2-05 validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


def substantive() -> dict:
    return {
        "project_identity": {
            "project_name": "Test Project", "project_summary": "Test summary", "project_type": "SOFTWARE",
            "canonical_repository": "owner/repo", "canonical_branch": "main", "existing_project": False, "existing_floppy_project": False,
        },
        "intended_observable_final_outcome": "A verified observable result",
        "accepted_scope": {"outcomes": ["result exists"], "capabilities": ["validate"], "boundaries": ["explicit authority"]},
        "accepted_exclusions": ["silent migration"],
        "major_constraints": [{"constraint_id": "C-1", "statement": "explicit authority", "source": "ADMINISTRATOR", "change_requires_plan_revision": True}],
        "verified_starting_state": {
            "summary": "verified start", "repository_checkpoint": {"repository": "owner/repo", "branch": "main", "commit": "1" * 40, "tree": "2" * 40},
            "evidence": [{"kind": "REPOSITORY_CHECKPOINT", "reference": "owner/repo@checkpoint", "sha256": None}],
        },
        "important_assumptions": [], "known_unknowns": [], "accepted_architectural_decisions": [],
        "section_roadmap": [{
            "section_id": "FS-01", "name": "First", "purpose": "Implement first result", "observable_outcome": "First result exists",
            "dependencies": [], "acceptance_evidence": ["observable result"], "status": "DRAFT_NOT_AUTHORIZED", "implementation_details_frozen": False,
        }],
        "deferred_work": [], "explicitly_rejected_work": [],
        "migration_deployment_considerations": {
            "migration_disposition": "NONE", "automatic_migration": False, "migration_authority": "SEPARATE_EXPLICIT_ADMINISTRATOR_AUTHORITY_REQUIRED",
            "deployment_disposition": "NONE", "deployment_notes": [], "deployment_or_release_grants_implementation_authority": False,
        },
        "project_level_risks": [],
        "authority_model": {
            "administrator_final_authority": True, "plan_acceptance_grants_implementation_authority": False,
            "plan_acceptance_grants_repository_writer": False, "plan_acceptance_grants_migration_authority": False,
            "plan_acceptance_grants_main_modification_authority": False, "plan_acceptance_grants_integration_authority": False,
            "plan_acceptance_grants_tag_authority": False, "plan_acceptance_grants_release_authority": False,
            "role_or_provider_capability_grants_authority": False, "automatic_authority_transfer": False,
            "implementation_authorization": "SEPARATE_EXPLICIT_ACTION_REQUIRED", "first_section_requires_separate_work_package_acceptance": True,
        },
        "first_proposed_work_section": {
            "section_id": "FS-01", "draft_path": ".floppy/templates/Floppy-E-FS-01.draft.md",
            "status": "DRAFT_NOT_AUTHORIZED", "work_package_acceptance": "NOT_ACCEPTED", "implementation": "NOT_STARTED", "verification": "NOT_STARTED",
            "implementation_authorization": None, "section_working_model": None, "repository_writer": None,
        },
    }


def accepted(provider_class: str = "CLASS_A") -> dict:
    value = substantive()
    digest = VALIDATOR.canonical_v2_opp_substantive_sha256(value)
    project_id = str(uuid.uuid4())
    return {
        "format": "floppy-official-project-plan", "format_version": "1.0.0", "contract_version": "2.0.0",
        "plan_id": f"OPP-{project_id}", "plan_revision_id": "ORIGINAL", "project_id": project_id, "accepted_state_revision_id": "ORIGINAL", **value,
        "roadmap_binding": {"machine_path": ".floppy/roadmap/roadmap.json", "human_path": ".floppy/roadmap/roadmap.md", "machine_sha256": "3" * 64, "human_sha256": "4" * 64, "section_roadmap_sha256": VALIDATOR.canonical_v2_opp_substantive_sha256(value["section_roadmap"])},
        "project_origin_binding": {"origin_contract": "V2_ACCEPTED_PROJECT_ORIGIN", "project_id": project_id, "accepted_state_path": ".floppy/accepted-state.json", "accepted_state_revision_id": "ORIGINAL", "continuity_overseer_id": f"CO-{project_id}", "initial_project_orchestrator_id": f"ORCH-{project_id}-00000001", "shared_origin_linkage": "DERIVED_AFTER_ACCEPTED_STATE_ESTABLISHMENT"},
        "source_provenance": {"floppy_source_identity": "2.0.0", "compatibility_profile": "2.0.0", "onboarding_entrypoint": "onboarding/Floppy_1E.md", "review_candidate_substantive_sha256": digest, "provider_capability_class": provider_class, "generation_repository_checkpoint": "5" * 40},
        "acceptance": {"status": "ACCEPTED", "authority": "TEST_ADMINISTRATOR", "accepted_at": "2026-08-11T12:00:00-05:00", "decision": f"ACCEPT CANDIDATE {digest}", "review_candidate_substantive_sha256": digest},
        "revision": {"revision_id": "ORIGINAL", "revision_kind": "ORIGINAL", "supersedes_revision_id": None, "review_candidate_substantive_sha256": digest, "substantive_projection_sha256": digest, "mechanical_completion_verified": True, "canonical_machine_path": ".floppy/project-plan/history/ORIGINAL.json", "canonical_human_path": ".floppy/project-plan/history/ORIGINAL.md", "active_machine_alias": ".floppy/project-plan/official-project-plan.json", "active_human_alias": ".floppy/project-plan/official-project-plan.md", "active_alias_semantics": "MUTABLE_POINTER_COPY_TO_CURRENT_ACCEPTED_REVISION"},
    }


class OfficialProjectPlanTests(unittest.TestCase):
    def test_schema_and_review_candidate_contracts_are_distinct(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        self.assertEqual(len(schema["required"]), 28)
        candidate = {"candidate_format": "floppy-official-project-plan-review-candidate", "candidate_format_version": "1.0.0", "substantive_plan": substantive()}
        resolver = RefResolver.from_schema(schema)
        self.assertFalse(list(Draft202012Validator(schema["$defs"]["review_candidate"], resolver=resolver).iter_errors(candidate)))
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(candidate)))
        self.assertNotIn("project_id", candidate)

    def test_candidate_digest_is_external_and_deterministic(self) -> None:
        value = substantive()
        candidate = {"candidate_format": "floppy-official-project-plan-review-candidate", "candidate_format_version": "1.0.0", "substantive_plan": value}
        self.assertEqual(VALIDATOR.validate_v2_official_project_plan_candidate(candidate), [])
        self.assertNotIn("candidate_substantive_sha256", candidate)
        self.assertEqual(VALIDATOR.canonical_v2_opp_substantive_sha256(value), VALIDATOR.canonical_v2_opp_substantive_sha256(dict(reversed(list(value.items())))))

    def test_accepted_record_exact_contract_and_no_digest_cycle(self) -> None:
        plan = accepted()
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertFalse(list(Draft202012Validator(schema).iter_errors(plan)))
        self.assertEqual(VALIDATOR.validate_v2_official_project_plan_record(plan), [])
        self.assertNotIn("protected_state_sha256", plan["project_origin_binding"])
        self.assertNotIn("shared_origin_sha256", plan["project_origin_binding"])
        self.assertEqual(plan["first_proposed_work_section"]["status"], "DRAFT_NOT_AUTHORIZED")
        self.assertIsNone(plan["first_proposed_work_section"]["implementation_authorization"])

    def test_unreviewed_substantive_change_is_failure(self) -> None:
        plan = accepted()
        plan["intended_observable_final_outcome"] = "unreviewed change"
        self.assertIn("OFFICIAL_PROJECT_PLAN_UNREVIEWED_SUBSTANTIVE_CHANGE", VALIDATOR.validate_v2_official_project_plan_record(plan))

    def test_provider_classes_normalize_to_same_semantics(self) -> None:
        base = accepted("CLASS_A")
        tuples = []
        for provider in ("CLASS_A", "CLASS_B", "CLASS_C"):
            plan = copy.deepcopy(base)
            plan["source_provenance"]["provider_capability_class"] = provider
            tuples.append(VALIDATOR.v2_opp_provider_semantic_tuple(plan, accepted_state_revision="ORIGINAL", shared_origin_sha256="6" * 64, roadmap_sha256="7" * 64))
        self.assertEqual(tuples[0], tuples[1])
        self.assertEqual(tuples[1], tuples[2])


if __name__ == "__main__":
    unittest.main()
