from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "tools/floppyctl.py"


def load_cli():
    spec = importlib.util.spec_from_file_location("floppyctl_v2_05_release", CLI_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load floppyctl")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CLI = load_cli()


class V2ReleaseSourceFinalizationTests(unittest.TestCase):
    def test_source_identity_is_finalized_without_later_release_claims(self) -> None:
        manifest = json.loads((ROOT / "system-manifest.json").read_text(encoding="utf-8"))
        profile = json.loads((ROOT / "specs/v2-compatibility-profile.json").read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "schemas/bce/2.0.0/bce-compatibility-profile.schema.json").read_text(encoding="utf-8"))
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), "2.0.0")
        self.assertEqual(manifest["system_version"], "2.0.0")
        self.assertEqual(manifest["status"], "stable-release")
        self.assertEqual(profile["source_identity"], "2.0.0")
        self.assertEqual(schema["properties"]["source_identity"]["const"], "2.0.0")
        self.assertEqual(
            manifest["release_status_semantics"],
            {
                "status_field_scope": "SOURCE_CONTENT_MATURITY_ONLY",
                "stable_release_means": "FINAL_INTENDED_V2_0_0_SOURCE_CONTENT_WITH_NO_PLANNED_PRE_RELEASE_SOURCE_MUTATION",
                "asserts_source_verification": False,
                "asserts_administrator_result_acceptance": False,
                "asserts_main_integration": False,
                "asserts_git_tag": False,
                "asserts_public_release": False,
                "verification_evidence_source": "V2_05_VERIFICATION_AND_TR_006",
                "administrator_acceptance_evidence_source": "TR_007_ACCEPT_SECTION",
                "main_integration_evidence_source": "SEPARATELY_AUTHORIZED_I1",
                "tag_evidence_source": "SEPARATELY_AUTHORIZED_T1_AND_GIT_STATE",
                "publication_evidence_source": "SEPARATELY_AUTHORIZED_REL1_AND_RELEASE_PLATFORM_STATE",
            },
        )
        self.assertEqual(
            manifest["release_facts_at_p1"],
            {
                "SOURCE_CONTENT_FINAL": True,
                "SOURCE_VERIFICATION": "PENDING",
                "ADMINISTRATOR_RESULT_ACCEPTANCE": "PENDING",
                "MAIN_INTEGRATION": "NOT_AUTHORIZED",
                "TAG": "NOT_AUTHORIZED",
                "PUBLIC_RELEASE": "NOT_AUTHORIZED",
            },
        )

    def test_compatibility_family_finalization_is_narrow(self) -> None:
        profile = json.loads((ROOT / "specs/v2-compatibility-profile.json").read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "schemas/bce/2.0.0/bce-compatibility-profile.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(len(profile["compatibility_combinations"]), 6)
        for record in profile["future_record_families"].values():
            self.assertTrue(record["implemented"])
            self.assertFalse(record["authority_by_existence"])
            self.assertFalse(record["repository_writer_by_role"])
        self.assertEqual(schema["$defs"]["future_family"]["properties"]["implemented"], {"const": True})

    def test_validated_boot_target_is_67(self) -> None:
        self.assertEqual(len(CLI.BOOT_PACKAGE_FILE_PATHS), 67)
        self.assertEqual(tuple(CLI.BOOT_PACKAGE_FILE_PATHS), tuple(sorted(CLI.BOOT_PACKAGE_FILE_PATHS)))
        self.assertIn("schemas/bce/2.0.0/bce-official-project-plan.schema.json", CLI.BOOT_PACKAGE_FILE_PATHS)
        self.assertIn("specs/official-project-plan.md", CLI.BOOT_PACKAGE_FILE_PATHS)

    def test_provider_freshness_is_evidence_not_authority(self) -> None:
        manifest = json.loads((ROOT / "system-manifest.json").read_text(encoding="utf-8"))
        freshness = manifest["provider_documentation_freshness"]
        self.assertEqual(freshness["D1"]["required_before"], "V2-05_VERIFICATION_COMPLETION")
        self.assertEqual(freshness["D1"]["status_at_source_finalization"], "REQUIRED_NOT_YET_RECORDED")
        self.assertEqual(freshness["D2"]["required_after"], "CLEAN_MAIN_INTEGRATION")
        self.assertEqual(freshness["D2"]["required_before"], "TAG_OR_PUBLICATION")
        self.assertEqual(freshness["D2"]["material_staleness_result"], "PROVIDER_DOCUMENTATION_REFRESH_REQUIRED")
        self.assertFalse(freshness["provider_facts_are_normative_authority"])


if __name__ == "__main__":
    unittest.main()
