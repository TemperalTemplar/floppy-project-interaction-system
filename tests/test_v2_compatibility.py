from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_floppy.py"
PROFILE_PATH = ROOT / "specs" / "v2-compatibility-profile.json"
SCHEMA_PATH = (
    ROOT / "schemas" / "bce" / "2.0.0" / "bce-compatibility-profile.schema.json"
)


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_floppy_v2_01", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load tools/validate_floppy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


def normalized_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class V2CompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def resolve(self, combination_id: str):
        combination = next(
            item
            for item in self.profile["compatibility_combinations"]
            if item["combination_id"] == combination_id
        )
        return VALIDATOR.resolve_v2_compatibility_profile(
            self.profile,
            dict(combination["selector"]),
        )

    def test_profile_schema_is_valid_and_profile_conforms(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        failures = list(Draft202012Validator(self.schema).iter_errors(self.profile))
        self.assertEqual(failures, [])

    def test_v1_1_0_profile_recognition(self) -> None:
        result = self.resolve("V1_BASE_1_0")
        self.assertEqual(result["status"], "RESOLVED")
        self.assertEqual(result["disposition"], "CONTINUE_V1")

    def test_v1_1_1_verification_only_profile_recognition(self) -> None:
        result = self.resolve("V1_VERIFICATION_ONLY_1_1")
        self.assertEqual(result["status"], "RESOLVED")
        self.assertEqual(result["combination_id"], "V1_VERIFICATION_ONLY_1_1")

    def test_v1_1_2_final_closure_profile_recognition(self) -> None:
        result = self.resolve("V1_FINAL_CLOSURE_1_2")
        self.assertEqual(result["status"], "RESOLVED")
        self.assertEqual(result["combination_id"], "V1_FINAL_CLOSURE_1_2")

    def test_1_2_does_not_numerically_supersede_1_1(self) -> None:
        result_11 = self.resolve("V1_VERIFICATION_ONLY_1_1")
        result_12 = self.resolve("V1_FINAL_CLOSURE_1_2")
        self.assertEqual(result_11["combination_id"], "V1_VERIFICATION_ONLY_1_1")
        self.assertEqual(result_12["combination_id"], "V1_FINAL_CLOSURE_1_2")
        self.assertFalse(self.profile["numeric_latest_schema_inference"])
        self.assertTrue(self.profile["v1_contracts"]["numeric_supersession_forbidden"])

    def test_supported_v1_continues_without_migration(self) -> None:
        for identifier in (
            "V1_BASE_1_0",
            "V1_VERIFICATION_ONLY_1_1",
            "V1_FINAL_CLOSURE_1_2",
        ):
            with self.subTest(identifier=identifier):
                result = self.resolve(identifier)
                self.assertEqual(result["disposition"], "CONTINUE_V1")
                self.assertFalse(result["automatic_migration"])
                self.assertTrue(result["historical_state_preserved"])

    def test_explicit_v2_adoption_profiles_are_registered(self) -> None:
        for identifier in (
            "V2_PROFILE_OVER_V1_1_0",
            "V2_PROFILE_OVER_V1_1_1",
            "V2_PROFILE_OVER_V1_1_2",
        ):
            with self.subTest(identifier=identifier):
                result = self.resolve(identifier)
                self.assertEqual(result["status"], "RESOLVED")
                self.assertEqual(result["disposition"], "V2_ADOPTION_OPTIONAL")
                self.assertFalse(result["automatic_migration"])

    def test_ambiguous_profile_stops_safely(self) -> None:
        result = VALIDATOR.resolve_v2_compatibility_profile(
            self.profile,
            {"source_lineage": "v1.0.0"},
        )
        self.assertEqual(result["status"], "STOP")
        self.assertEqual(result["reason"], "AMBIGUOUS_PROFILE")
        self.assertTrue(result["candidates"])

    def test_unsupported_and_unknown_future_profiles_stop_safely(self) -> None:
        observed = {
            "source_lineage": "v2.0.0",
            "lifecycle_schema": "1.0.0",
            "verification_only_extension": False,
            "final_closure_extension": False,
            "compatibility_profile": "9.9.9",
        }
        result = VALIDATOR.resolve_v2_compatibility_profile(self.profile, observed)
        self.assertEqual(result["status"], "STOP")
        self.assertEqual(result["reason"], "UNSUPPORTED_PROFILE")

        exact = dict(
            next(
                item
                for item in self.profile["compatibility_combinations"]
                if item["combination_id"] == "V1_BASE_1_0"
            )["selector"]
        )
        exact["unknown_records"] = ["future-record-family:3.0.0"]
        future = VALIDATOR.resolve_v2_compatibility_profile(self.profile, exact)
        self.assertEqual(future["status"], "STOP")
        self.assertEqual(future["reason"], "UNSUPPORTED_PROFILE")

    def test_context_loss_and_accepted_state_precedence_are_normative(self) -> None:
        self.assertEqual(
            self.profile["context_loss_rule"],
            "Context loss is not authority to reconstruct accepted work.",
        )
        self.assertEqual(
            self.profile["accepted_state_precedence"],
            [
                "COMMITTED_ACCEPTED_REPOSITORY_STATE",
                "HISTORICAL_ACCEPTED_RECORDS",
                "CURRENT_OPERATIONAL_STATE",
                "DRAFTS",
                "EXPLICIT_ADMINISTRATOR_EVIDENCE",
                "LIVE_REPOSITORY_EVIDENCE",
                "CONVERSATION_MEMORY",
            ],
        )

    def test_provider_capability_never_grants_authority(self) -> None:
        classes = self.profile["provider_capability_classes"]
        self.assertEqual(set(classes), {"CLASS_A", "CLASS_B", "CLASS_C"})
        for name, record in classes.items():
            with self.subTest(provider_class=name):
                self.assertFalse(record["grants_floppy_authority"])
                self.assertFalse(record["grants_repository_writer"])

    def test_future_v2_04_and_v2_05_boundaries_are_non_implementing(self) -> None:
        future = self.profile["future_record_families"]
        self.assertEqual(future["continuity_overseer"]["owner_work_package"], "V2-04")
        self.assertEqual(future["official_project_plan"]["owner_work_package"], "V2-05")
        for name, record in future.items():
            with self.subTest(family=name):
                self.assertFalse(record["implemented"])
                self.assertFalse(record["authority_by_existence"])
                self.assertFalse(record["repository_writer_by_role"])

    def test_frozen_v1_schema_digests_are_preserved(self) -> None:
        expected = {
            "schemas/bce/1.0.0/bce-lifecycle-state.schema.json":
                "2be2744ec1a4db407bb898320809cf9eae84e1bd0202b038abbbe158c0a566e1",
            "schemas/bce/1.0.0/bce-work-authorization.schema.json":
                "8bc4ea16955e4b220b10ac3a155d015c26a6cf05e257a25be0fe2d1c5c6466f1",
            "schemas/bce/1.0.0/bce-lifecycle-transition.schema.json":
                "6343c112e374d3e970e4ea377244589128def021ada425a995bc16f0b1e89562",
            "schemas/bce/1.1.0/bce-lifecycle-state.schema.json":
                "40d0263ebb3b3c3ec4ba3801a315a92ec245adedba94c7a9bbba4f63636df4f5",
            "schemas/bce/1.2.0/bce-lifecycle-state.schema.json":
                "94014bc4ba99100b0b7b4d38f76155ed1ec018726c715b83f26cfaf1e7c6c14a",
        }
        for relative, digest in expected.items():
            with self.subTest(relative=relative):
                self.assertEqual(normalized_sha256(ROOT / relative), digest)

    def test_v2_artifacts_are_registered_in_system_manifest(self) -> None:
        manifest = json.loads((ROOT / "system-manifest.json").read_text(encoding="utf-8"))
        registry = manifest["v2_compatibility_profile"]
        self.assertEqual(registry["owner"], "V2-01")
        self.assertEqual(registry["profile_version"], "2.0.0")
        self.assertFalse(registry["numeric_latest_schema_inference"])
        self.assertFalse(registry["automatic_migration"])
        for record in registry["artifacts"].values():
            self.assertTrue((ROOT / record["path"]).is_file())
            self.assertEqual(
                normalized_sha256(ROOT / record["path"]),
                record["sha256"],
            )


if __name__ == "__main__":
    unittest.main()
