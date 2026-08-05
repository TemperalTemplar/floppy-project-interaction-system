from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_floppy.py"
SCHEMA_FIXTURES = ROOT / "tests" / "fixtures" / "bce-schemas" / "1.0.0"
REGISTRY_PATH = (
    ROOT / "project-seed" / ".floppy" / "orchestrator-registry.json"
)
TRANSITION_TABLE_PATH = ROOT / "specs" / "lifecycle-transition-table.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_floppy_fs03",
        VALIDATOR_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load tools/validate_floppy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BceSemanticValidationTests(unittest.TestCase):
    def valid_bundle(self) -> dict:
        table = load_json(TRANSITION_TABLE_PATH)
        definition = copy.deepcopy(
            next(
                transition
                for transition in table["transitions"]
                if transition["id"]
                == "TR-003-AUTHORIZE-SECTION-IMPLEMENTATION"
            )
        )
        definition.update(
            {
                "declarative_only": True,
                "execution_capability": False,
                "applies_transition": False,
                "writes_lifecycle_state": False,
            }
        )

        state = load_json(
            SCHEMA_FIXTURES / "valid" / "lifecycle-state.json"
        )
        state.update(
            {
                "section": "FS-03",
                "authorization_id": "FS_03_IMPLEMENTATION",
                "base_checkpoint": "c" * 40,
                "active_implementation_sections": ["FS-03"],
                "evidence": [
                    "FS03_WORK_PACKAGE_ACCEPTED",
                    "FS03_IMPLEMENTATION_AUTHORIZED",
                ],
            }
        )

        authorization = load_json(
            SCHEMA_FIXTURES / "valid" / "work-authorization.json"
        )
        authorization.update(
            {
                "authorization_id": "FS_03_IMPLEMENTATION",
                "section": "FS-03",
                "base_checkpoint": "c" * 40,
                "branch": "feature/fs-03-semantic-validator",
                "worktree": r"D:\A\Floppy-FS-03",
                "exact_file_scope": [
                    "tests/test_bce_semantics.py",
                    "tools/validate_floppy.py",
                ],
                "commit_sequence": [
                    {
                        "id": "P1",
                        "message": (
                            "feat(fs-03): add BCE semantic validation"
                        ),
                        "path_class": "reusable_product",
                    }
                ],
            }
        )

        registry = load_json(REGISTRY_PATH)
        registry["orchestrators"][0]["status"] = "ACTIVE"
        registry["current_assignments"].update(
            {
                "current_orchestrator": "PROJECT_ORCHESTRATOR",
                "current_section_working_model": "FS_03_WORKING_MODEL",
                "repository_writer": "FS_03_WORKING_MODEL",
                "writer_authorization_reference": (
                    "FS_03_IMPLEMENTATION"
                ),
            }
        )

        return {
            "lifecycle_states": [state],
            "work_authorizations": [authorization],
            "lifecycle_transitions": [definition],
            "orchestrator_registry": registry,
            "authorization_bindings": [
                {
                    "authorization_id": "FS_03_IMPLEMENTATION",
                    "orchestrator_id": "PROJECT_ORCHESTRATOR",
                    "working_model_id": "FS_03_WORKING_MODEL",
                    "repository_writer_id": "FS_03_WORKING_MODEL",
                }
            ],
            "represented_transitions": [
                {
                    "id": "FS03_ACTIVATION",
                    "transition_id": definition["id"],
                    "from_state_id": definition["from_state_ids"][0],
                    "to_state_id": definition["to_state_id"],
                    "satisfied_preconditions": copy.deepcopy(
                        definition["preconditions"]
                    ),
                    "evidence_refs": copy.deepcopy(state["evidence"]),
                }
            ],
            "evidence": [
                {
                    "id": "FS03_WORK_PACKAGE_ACCEPTED",
                    "present": True,
                },
                {
                    "id": "FS03_IMPLEMENTATION_AUTHORIZED",
                    "present": True,
                },
            ],
            "commits": [
                {
                    "id": "P1",
                    "authorization_id": "FS_03_IMPLEMENTATION",
                    "paths": [
                        "tests/test_bce_semantics.py",
                        "tools/validate_floppy.py",
                    ],
                }
            ],
        }

    def assert_one(self, bundle: dict, diagnostic: str) -> None:
        self.assertEqual(
            [diagnostic],
            VALIDATOR.validate_bce_semantics(bundle, ROOT),
        )

    def test_valid_cross_record_set_passes(self) -> None:
        self.assertEqual(
            [],
            VALIDATOR.validate_bce_semantics(
                self.valid_bundle(),
                ROOT,
            ),
        )


    def test_lifecycle_dimensions_mismatch_fails_once(self) -> None:
        bundle = self.valid_bundle()
        bundle["lifecycle_states"][0]["dimensions"][
            "implementation"
        ] = "IN_PROGRESS"
        self.assert_one(
            bundle,
            "SEMANTIC_LIFECYCLE_DIMENSIONS_MISMATCH: "
            "LC-SECTION-AUTHORIZED-NOT-STARTED",
        )

    def test_active_authorization_id_mismatch_fails_once(self) -> None:
        bundle = self.valid_bundle()
        bundle["lifecycle_states"][0][
            "authorization_id"
        ] = "UNKNOWN_AUTHORIZATION"
        self.assert_one(
            bundle,
            "SEMANTIC_ACTIVE_AUTHORIZATION_MISSING",
        )

    def test_authorization_section_mismatch_fails_once(self) -> None:
        bundle = self.valid_bundle()
        bundle["work_authorizations"][0]["section"] = "FS-04"
        self.assert_one(
            bundle,
            "SEMANTIC_AUTHORIZATION_SECTION_MISMATCH",
        )

    def test_authorization_checkpoint_mismatch_fails_once(self) -> None:
        bundle = self.valid_bundle()
        bundle["work_authorizations"][0][
            "base_checkpoint"
        ] = "d" * 40
        self.assert_one(
            bundle,
            "SEMANTIC_AUTHORIZATION_CHECKPOINT_MISMATCH",
        )

    def test_writer_authorization_reference_mismatch_fails_once(
        self,
    ) -> None:
        bundle = self.valid_bundle()
        bundle["orchestrator_registry"]["current_assignments"][
            "writer_authorization_reference"
        ] = "OTHER_AUTHORIZATION"
        self.assert_one(
            bundle,
            "SEMANTIC_WRITER_AUTHORIZATION_MISMATCH",
        )

    def test_unknown_orchestrator_fails_once(self) -> None:
        bundle = self.valid_bundle()
        bundle["authorization_bindings"][0][
            "orchestrator_id"
        ] = "UNKNOWN_ORCHESTRATOR"
        self.assert_one(
            bundle,
            "SEMANTIC_UNKNOWN_ORCHESTRATOR: UNKNOWN_ORCHESTRATOR",
        )

    def test_unknown_working_model_fails_once(self) -> None:
        bundle = self.valid_bundle()
        bundle["authorization_bindings"][0][
            "working_model_id"
        ] = "UNKNOWN_WORKING_MODEL"
        self.assert_one(
            bundle,
            "SEMANTIC_UNKNOWN_WORKING_MODEL: UNKNOWN_WORKING_MODEL",
        )

    def test_unknown_repository_writer_fails_once(self) -> None:
        bundle = self.valid_bundle()
        bundle["authorization_bindings"][0][
            "repository_writer_id"
        ] = "UNKNOWN_WRITER"
        self.assert_one(
            bundle,
            "SEMANTIC_UNKNOWN_REPOSITORY_WRITER: UNKNOWN_WRITER",
        )

    def test_more_than_one_current_writer_fails_once(self) -> None:
        bundle = self.valid_bundle()
        bundle["orchestrator_registry"]["current_assignments"][
            "repository_writer"
        ] = ["FS_03_WORKING_MODEL", "SECOND_WRITER"]
        self.assert_one(
            bundle,
            "SEMANTIC_MULTIPLE_CURRENT_WRITERS: found 2",
        )

    def test_path_outside_exact_scope_fails_once(self) -> None:
        bundle = self.valid_bundle()
        bundle["commits"][0]["paths"] = ["README.md"]
        self.assert_one(
            bundle,
            "SEMANTIC_COMMIT_PATH_OUTSIDE_SCOPE: P1 README.md",
        )

    def test_duplicate_conflicting_identifier_fails_once(self) -> None:
        bundle = self.valid_bundle()
        conflicting = copy.deepcopy(bundle["work_authorizations"][0])
        conflicting["source_version"] = "conflicting-version"
        bundle["work_authorizations"].append(conflicting)
        self.assert_one(
            bundle,
            "SEMANTIC_CONFLICTING_IDENTIFIER: "
            "work_authorization FS_03_IMPLEMENTATION",
        )

    def test_illegal_transition_source_fails_once(self) -> None:
        bundle = self.valid_bundle()
        bundle["represented_transitions"][0][
            "from_state_id"
        ] = "LC-ONBOARDING-REQUIRED"
        self.assert_one(
            bundle,
            "SEMANTIC_ILLEGAL_TRANSITION_SOURCE: "
            "FS03_ACTIVATION LC-ONBOARDING-REQUIRED",
        )

    def test_illegal_transition_destination_fails_once(self) -> None:
        bundle = self.valid_bundle()
        bundle["represented_transitions"][0][
            "to_state_id"
        ] = "LC-SECTION-IMPLEMENTATION-IN-PROGRESS"
        self.assert_one(
            bundle,
            "SEMANTIC_ILLEGAL_TRANSITION_DESTINATION: "
            "FS03_ACTIVATION "
            "LC-SECTION-IMPLEMENTATION-IN-PROGRESS",
        )

    def test_missing_represented_precondition_fails_once(self) -> None:
        bundle = self.valid_bundle()
        bundle["represented_transitions"][0][
            "satisfied_preconditions"
        ].pop()
        self.assert_one(
            bundle,
            "SEMANTIC_TRANSITION_PRECONDITION_MISSING: "
            "FS03_ACTIVATION",
        )

    def test_missing_required_evidence_fails_once(self) -> None:
        bundle = self.valid_bundle()
        bundle["evidence"].pop()
        self.assert_one(
            bundle,
            "SEMANTIC_REQUIRED_EVIDENCE_MISSING: "
            "FS03_IMPLEMENTATION_AUTHORIZED",
        )

    def test_fs02_normative_records_pass_schema_validation(self) -> None:
        bundle = self.valid_bundle()
        diagnostics = VALIDATOR.validate_bce_semantics(bundle, ROOT)
        self.assertFalse(
            any(
                item.startswith("SEMANTIC_SCHEMA_INVALID")
                for item in diagnostics
            ),
            diagnostics,
        )

    def test_validation_does_not_mutate_records_or_files(self) -> None:
        bundle = self.valid_bundle()
        before_bundle = copy.deepcopy(bundle)
        watched = [
            VALIDATOR_PATH,
            TRANSITION_TABLE_PATH,
            REGISTRY_PATH,
            ROOT
            / "schemas"
            / "bce"
            / "1.0.0"
            / "bce-lifecycle-state.schema.json",
            ROOT
            / "schemas"
            / "bce"
            / "1.0.0"
            / "bce-work-authorization.schema.json",
            ROOT
            / "schemas"
            / "bce"
            / "1.0.0"
            / "bce-lifecycle-transition.schema.json",
        ]
        before_files = {path: file_digest(path) for path in watched}

        self.assertEqual(
            [],
            VALIDATOR.validate_bce_semantics(bundle, ROOT),
        )

        self.assertEqual(before_bundle, bundle)
        self.assertEqual(
            before_files,
            {path: file_digest(path) for path in watched},
        )

    def test_verification_only_contract_helper(self) -> None:
        valid = {"work_package_type": "VERIFICATION_ONLY_NO_REUSABLE_PRODUCT_CHANGE", "implementation_state": "NOT_REQUIRED", "authorization_id": None, "repository_writer": None, "writer_authorization_reference": None, "reusable_product_paths": [], "reusable_product_commits": [], "product_commit": None}
        self.assertEqual(VALIDATOR.validate_verification_only_contract(valid), [])
        invalid = copy.deepcopy(valid)
        invalid["product_commit"] = "0" * 40
        self.assertIn("VERIFICATION_ONLY_PRODUCT_COMMIT_MUST_BE_NULL", VALIDATOR.validate_verification_only_contract(invalid))


if __name__ == "__main__":
    unittest.main()
