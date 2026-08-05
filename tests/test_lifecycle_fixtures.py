from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TABLE_PATH = ROOT / "specs" / "lifecycle-transition-table.json"
VALID_DIR = ROOT / "tests" / "fixtures" / "lifecycle" / "valid"
INVALID_DIR = ROOT / "tests" / "fixtures" / "lifecycle" / "invalid"

EXPECTED_VALID_FILES = {
    "01-onboarding-required.json",
    "02-roadmap-accepted-no-active-work.json",
    "03-work-package-accepted-no-active-work.json",
    "04-section-authorized-not-started.json",
    "05-section-implementation-in-progress.json",
    "06-implementation-complete-verification-pending.json",
    "07-verification-complete-acceptance-pending.json",
    "08-section-accepted-closeout-proposed.json",
    "09-section-closed-next-section-inactive.json",
    "10-migration-planned-not-authorized.json",
    "11-migration-applied-verification-complete.json",
    "12-project-finally-closed.json",
    "13-exact-section-implementation-authorization.json",
    "14-section-authorization-transition.json",
    "15-verification-only-work-package-accepted-pending.json",
    "16-verification-only-complete-acceptance-pending.json",
    "17-verification-only-section-accepted-closeout-not-proposed.json",
    "18-verification-only-section-accepted-closeout-proposed.json",
    "19-verification-only-closeout-applied.json",
}

EXPECTED_INVALID_FILES = {
    "01-roadmap-acceptance-implies-section-authorization.json",
    "02-work-package-acceptance-implies-section-authorization.json",
    "03-draft-created-implies-section-active.json",
    "04-implementation-complete-implies-acceptance.json",
    "05-section-accepted-implies-closed-without-closeout.json",
    "06-section-closed-implies-next-section-authorization.json",
    "07-stale-base-checkpoint-allows-write.json",
    "08-project-closed-allows-active-authorization.json",
    "09-proposed-closeout-marked-applied.json",
    "10-multiple-active-sections.json",
    "11-authorization-missing-exact-file-scope.json",
    "12-transition-missing-forbidden-side-effects.json",
    "13-not-required-with-standard-work-package.json",
    "14-verification-only-with-active-authorization.json",
    "15-verification-only-with-active-section.json",
    "16-verification-only-with-product-scope.json",
    "17-verification-only-with-product-commit.json",
}

ASSERTION_ERRORS = {
    "roadmap_acceptance_authorizes_section":
        "roadmap_acceptance_must_not_authorize_section",
    "work_package_acceptance_authorizes_section":
        "work_package_acceptance_must_not_authorize_section",
    "draft_creation_activates_section":
        "draft_creation_must_not_activate_section",
    "implementation_completion_accepts_section":
        "implementation_completion_must_not_imply_acceptance",
    "section_acceptance_closes_section":
        "section_acceptance_must_not_imply_closeout",
    "section_closeout_authorizes_next_section":
        "section_closeout_must_not_authorize_next_section",
    "stale_base_checkpoint_permits_write":
        "stale_base_checkpoint_must_stop_write",
    "final_closure_permits_active_authority":
        "finally_closed_project_must_not_have_active_authority",
    "proposed_closeout_is_applied":
        "proposed_closeout_must_not_be_marked_applied",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class FixtureSemantics:
    def __init__(self, table: dict[str, Any]) -> None:
        self.states = {state["id"]: state for state in table["states"]}
        self.transitions = {
            transition["id"]: transition for transition in table["transitions"]
        }

    def validate(self, fixture: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        state = fixture.get("state", {})
        state_id = state.get("state_id")

        if state_id not in self.states:
            errors.append("unknown_lifecycle_state")
            return errors

        expected_dimensions = self.states[state_id]["dimensions"]
        if state.get("dimensions") != expected_dimensions:
            errors.append("state_dimensions_do_not_match_state_identifier")

        active_sections = state.get("active_implementation_sections", [])
        if len(active_sections) > 1:
            errors.append("multiple_active_implementation_sections")

        authority_value = state.get("dimensions", {}).get("authority")
        authorization = fixture.get("authorization")

        if active_sections:
            if authority_value != "EXACT_SECTION_IMPLEMENTATION_AUTHORIZATION":
                errors.append("active_section_requires_exact_authority")
            if authorization is None:
                errors.append("active_section_requires_authorization_record")
            if state.get("section") not in active_sections:
                errors.append("active_section_must_match_state_section")

        if authority_value == "EXACT_SECTION_IMPLEMENTATION_AUTHORIZATION":
            if authorization is None:
                errors.append("exact_authority_requires_authorization_record")
            else:
                if authorization.get("kind") != "section_implementation":
                    errors.append("authorization_kind_must_be_section_implementation")
                if authorization.get("section") != state.get("section"):
                    errors.append("authorization_section_mismatch")
                if authorization.get("authorization_id") != state.get(
                    "authorization_id"
                ):
                    errors.append("authorization_identifier_mismatch")
                exact_scope = authorization.get("exact_file_scope")
                if not isinstance(exact_scope, list) or not exact_scope:
                    errors.append("authorization_requires_exact_file_scope")
                if authorization.get("base_checkpoint") != fixture.get(
                    "current_checkpoint"
                ):
                    errors.append("stale_base_checkpoint_must_stop_write")
        elif authorization is not None:
            errors.append("authorization_record_without_active_authority")

        if (
            state.get("dimensions", {}).get("final_closure") == "FINALLY_CLOSED"
            and (active_sections or authorization is not None)
        ):
            errors.append("finally_closed_project_must_not_have_active_authority")

        assertions = fixture.get("assertions", {})
        for assertion_name, error_code in ASSERTION_ERRORS.items():
            if assertions.get(assertion_name) is True:
                errors.append(error_code)

        if fixture.get("next_section_authorized") is True:
            errors.append("section_closeout_must_not_authorize_next_section")

        if fixture.get("work_package_type") == "VERIFICATION_ONLY_NO_REUSABLE_PRODUCT_CHANGE" and state_id.startswith("LC-VERIFICATION-ONLY-"):
            if state.get("dimensions", {}).get("implementation") != "NOT_REQUIRED": errors.append("verification_only_contract_invalid")
            if fixture.get("reusable_product_paths") not in ([], None): errors.append("verification_only_contract_invalid")
            if fixture.get("reusable_product_commits") not in ([], None): errors.append("verification_only_contract_invalid")
        elif state.get("dimensions", {}).get("implementation") == "NOT_REQUIRED":
            errors.append("verification_only_contract_invalid")

        if (
            fixture.get("draft_artifact_status") == "draft_non_normative"
            and assertions.get("draft_creation_activates_section") is True
        ):
            errors.append("draft_creation_must_not_activate_section")

        transition_record = fixture.get("transition_record")
        if transition_record is not None:
            transition_id = transition_record.get("id")
            transition = self.transitions.get(transition_id)

            if transition is None:
                errors.append("unknown_transition_identifier")
            else:
                if transition_record.get("from_state_id") not in transition[
                    "from_state_ids"
                ]:
                    errors.append("transition_from_state_mismatch")
                if transition_record.get("to_state_id") != transition["to_state_id"]:
                    errors.append("transition_to_state_mismatch")
                if transition_record.get("changed_dimensions") != transition[
                    "changed_dimensions"
                ]:
                    errors.append("transition_changed_dimensions_mismatch")
                if not transition_record.get("forbidden_side_effects"):
                    errors.append("transition_requires_forbidden_side_effects")

        return sorted(set(errors))


class LifecycleFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.table = load_json(TABLE_PATH)
        cls.semantics = FixtureSemantics(cls.table)

    def test_exact_fixture_inventory(self) -> None:
        valid_names = {path.name for path in VALID_DIR.glob("*.json")}
        invalid_names = {path.name for path in INVALID_DIR.glob("*.json")}

        self.assertEqual(valid_names, EXPECTED_VALID_FILES)
        self.assertEqual(invalid_names, EXPECTED_INVALID_FILES)

    def test_every_fixture_parses_as_json(self) -> None:
        paths = sorted(VALID_DIR.glob("*.json")) + sorted(
            INVALID_DIR.glob("*.json")
        )
        self.assertEqual(len(paths), 36)

        for path in paths:
            with self.subTest(path=path):
                fixture = load_json(path)
                self.assertTrue(fixture["fixture_id"])
                self.assertIn("expected_valid", fixture)

    def test_valid_fixtures_have_no_semantic_errors(self) -> None:
        for path in sorted(VALID_DIR.glob("*.json")):
            with self.subTest(path=path):
                fixture = load_json(path)
                self.assertTrue(fixture["expected_valid"])
                self.assertEqual(self.semantics.validate(fixture), [])

    def test_invalid_fixtures_fail_for_expected_reason(self) -> None:
        for path in sorted(INVALID_DIR.glob("*.json")):
            with self.subTest(path=path):
                fixture = load_json(path)
                self.assertFalse(fixture["expected_valid"])
                expected_error = fixture["expected_error"]
                errors = self.semantics.validate(fixture)
                self.assertIn(expected_error, errors, errors)


if __name__ == "__main__":
    unittest.main()
