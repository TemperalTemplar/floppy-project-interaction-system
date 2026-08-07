from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TABLE_PATH = ROOT / "specs" / "lifecycle-transition-table.json"

DRAFT_SCHEMAS = {
    ROOT / "schemas" / "drafts" / "bce-lifecycle-state.schema.json":
        "urn:floppy-project-interaction-system:draft:bce-lifecycle-state:fs-01",
    ROOT / "schemas" / "drafts" / "bce-work-authorization.schema.json":
        "urn:floppy-project-interaction-system:draft:bce-work-authorization:fs-01",
    ROOT / "schemas" / "drafts" / "bce-lifecycle-transition.schema.json":
        "urn:floppy-project-interaction-system:draft:bce-lifecycle-transition:fs-01",
}

REQUIRED_DIMENSIONS = {
    "roadmap",
    "work_package",
    "authority",
    "implementation",
    "verification",
    "acceptance",
    "closeout",
    "migration",
    "final_closure",
}

REQUIRED_TRANSITION_FIELDS = {
    "id",
    "title",
    "from_state_ids",
    "to_state_id",
    "changed_dimensions",
    "preconditions",
    "required_human_authority",
    "required_inputs",
    "required_outputs",
    "stop_conditions",
    "forbidden_side_effects",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_refs(value: Any) -> list[str]:
    refs: list[str] = []

    if isinstance(value, dict):
        for key, child in value.items():
            if key == "$ref":
                refs.append(child)
            refs.extend(collect_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.extend(collect_refs(child))

    return refs


class LifecycleSpecificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.table = load_json(TABLE_PATH)

    def test_transition_table_is_declarative_only(self) -> None:
        self.assertTrue(self.table["declarative_only"])
        self.assertFalse(self.table["execution_capability"])
        self.assertFalse(self.table["applies_transitions"])
        self.assertFalse(self.table["writes_lifecycle_state"])
        self.assertFalse(self.table["production_schema_enforcement"])

    def test_all_orthogonal_dimensions_are_declared(self) -> None:
        self.assertEqual(set(self.table["dimensions"]), REQUIRED_DIMENSIONS)
        self.assertEqual(self.table["one_active_implementation_section_maximum"], 1)

    def test_state_identifiers_are_unique(self) -> None:
        state_ids = [state["id"] for state in self.table["states"]]
        self.assertEqual(len(state_ids), 20)
        self.assertEqual(len(state_ids), len(set(state_ids)))

        for state in self.table["states"]:
            self.assertEqual(set(state["dimensions"]), REQUIRED_DIMENSIONS)

    def test_transition_identifiers_and_references_are_valid(self) -> None:
        state_ids = {state["id"] for state in self.table["states"]}
        transition_ids = [transition["id"] for transition in self.table["transitions"]]

        self.assertEqual(len(transition_ids), 20)
        self.assertEqual(len(transition_ids), len(set(transition_ids)))

        for transition in self.table["transitions"]:
            self.assertTrue(REQUIRED_TRANSITION_FIELDS.issubset(transition))
            self.assertTrue(transition["from_state_ids"])
            self.assertTrue(transition["changed_dimensions"])
            self.assertTrue(transition["preconditions"])
            self.assertTrue(transition["required_inputs"])
            self.assertTrue(transition["required_outputs"])
            self.assertTrue(transition["stop_conditions"])
            self.assertTrue(transition["forbidden_side_effects"])
            self.assertIn(transition["to_state_id"], state_ids)

            for state_id in transition["from_state_ids"]:
                self.assertIn(state_id, state_ids)

            authority = transition["required_human_authority"]
            self.assertTrue(authority["actor"])
            self.assertTrue(authority["decision"])

    def test_post_provisioning_acceptance_dimensions_equal_actual_union(self) -> None:
        states = {state["id"]: state for state in self.table["states"]}
        expected = {
            "TR-002-ACCEPT-WORK-PACKAGE": {"work_package", "closeout"},
            "TR-016-ACCEPT-VERIFICATION-ONLY-WORK-PACKAGE": {
                "work_package",
                "implementation",
                "verification",
                "closeout",
            },
        }
        transitions = {
            transition["id"]: transition
            for transition in self.table["transitions"]
        }
        for transition_id, expected_dimensions in expected.items():
            with self.subTest(transition=transition_id):
                transition = transitions[transition_id]
                target = states[transition["to_state_id"]]
                actual: set[str] = set()
                for source_id in transition["from_state_ids"]:
                    source = states[source_id]
                    actual.update(
                        dimension
                        for dimension in REQUIRED_DIMENSIONS
                        if source["dimensions"][dimension]
                        != target["dimensions"][dimension]
                    )
                    if source.get("active_implementation_section") != target.get(
                        "active_implementation_section"
                    ):
                        actual.add("active_implementation_section")
                self.assertEqual(set(transition["changed_dimensions"]), actual)
                self.assertEqual(actual, expected_dimensions)

    def test_global_invariants_are_present(self) -> None:
        invariant_ids = {
            invariant["id"] for invariant in self.table["global_invariants"]
        }
        self.assertEqual(
            invariant_ids,
            {"INV-001", "INV-002", "INV-003", "INV-004", "INV-005", "INV-010"},
        )

    def test_prohibited_implications_are_unique_and_complete(self) -> None:
        implications = self.table["prohibited_implications"]
        implication_ids = [item["id"] for item in implications]

        self.assertEqual(len(implications), 12)
        self.assertEqual(len(implication_ids), len(set(implication_ids)))

        statements = "\n".join(item["statement"] for item in implications)
        required_fragments = (
            "Roadmap acceptance does not imply section authorization.",
            "Work-package acceptance does not imply section authorization.",
            "Draft creation does not imply section activation.",
            "Implementation completion does not imply administrator acceptance.",
            "Verification completion does not imply administrator acceptance.",
            "Section acceptance does not imply section closeout.",
            "Section closeout does not imply next-section authorization.",
            "A migration plan does not imply migration authorization.",
            "Migration application does not imply migration verification.",
            "A final-closure proposal does not imply final closure.",
        )

        for fragment in required_fragments:
            self.assertIn(fragment, statements)

    def test_draft_schema_candidates_are_non_normative(self) -> None:
        for path, expected_id in DRAFT_SCHEMAS.items():
            with self.subTest(path=path):
                schema = load_json(path)
                self.assertEqual(
                    schema["$schema"],
                    "https://json-schema.org/draft/2020-12/schema",
                )
                self.assertEqual(schema["$id"], expected_id)
                self.assertEqual(schema["status"], "draft_non_normative")
                self.assertEqual(schema["normative_section"], "FS-02")
                self.assertEqual(schema["current_section"], "FS-01")
                self.assertFalse(schema["production_enforcement"])

                definitions = schema.get("$defs", {})
                self.assertTrue(definitions)

                refs = collect_refs(schema)
                self.assertTrue(refs)

                for ref in refs:
                    self.assertTrue(ref.startswith("#/$defs/"), ref)
                    self.assertIn(ref.removeprefix("#/$defs/"), definitions)


if __name__ == "__main__":
    unittest.main()
