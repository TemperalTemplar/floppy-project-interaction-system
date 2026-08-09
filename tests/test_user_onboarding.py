from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_floppy.py"
CLI_PATH = ROOT / "tools" / "floppyctl.py"
STARTER = ROOT / "docs/getting-started/README.md"
PROVIDER_GUIDES = {
    "ChatGPT": "docs/getting-started/ChatGPT.md",
    "Gemini": "docs/getting-started/Gemini.md",
    "Grok": "docs/getting-started/Grok.md",
    "DeepSeek": "docs/getting-started/DeepSeek.md",
    "Other-AI": "docs/getting-started/Other-AI.md",
}
CAPABILITY_FIELDS = [
    "repository_read",
    "repository_write",
    "command_execution",
    "artifact_transfer",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module("validate_floppy_v2_02", VALIDATOR_PATH)


def normalized_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class V2UserOnboardingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.system = json.loads((ROOT / "system-manifest.json").read_text(encoding="utf-8"))
        cls.registry = cls.system["user_onboarding"]

    def test_source_registration_is_exact(self) -> None:
        self.assertEqual(self.system["entrypoints"]["user_onboarding"], "docs/getting-started/README.md")
        self.assertEqual(self.registry["owner"], "V2-02")
        self.assertEqual(self.registry["status"], "reusable_product")
        self.assertEqual(self.registry["canonical_starter"], "docs/getting-started/README.md")
        self.assertEqual(self.registry["provider_guides"], PROVIDER_GUIDES)
        self.assertEqual(self.registry["capability_fields"], CAPABILITY_FIELDS)
        self.assertFalse(self.registry["provider_brand_selects_class"])
        self.assertFalse(self.registry["capability_grants_authority"])
        for record in self.registry["artifacts"].values():
            path = ROOT / record["path"]
            self.assertTrue(path.is_file(), record["path"])
            self.assertEqual(normalized_sha256(path), record["sha256"])

    def test_exactly_one_canonical_universal_starter_prompt_exists(self) -> None:
        paths = [STARTER, *(ROOT / value for value in PROVIDER_GUIDES.values())]
        marker = "FLOPPY_CANONICAL_UNIVERSAL_STARTER_PROMPT_BEGIN"
        self.assertEqual(sum(path.read_text(encoding="utf-8").count(marker) for path in paths), 1)
        text = STARTER.read_text(encoding="utf-8")
        for field in CAPABILITY_FIELDS:
            self.assertIn(field, text)
        for route in ("ROUTE A", "ROUTE B", "ROUTE C"):
            self.assertIn(route, text)

    def test_provider_brand_does_not_select_class(self) -> None:
        self.assertFalse(self.registry["provider_brand_selects_class"])
        for guide in PROVIDER_GUIDES.values():
            text = (ROOT / guide).read_text(encoding="utf-8")
            self.assertIn("canonical", text.lower())
            self.assertIn("provider", text.lower())

    def test_actual_capability_vectors_select_repository_workflow(self) -> None:
        a = VALIDATOR.classify_v2_session_capabilities({
            "repository_read": True,
            "repository_write": True,
            "command_execution": False,
            "artifact_transfer": True,
        })
        b = VALIDATOR.classify_v2_session_capabilities({
            "repository_read": True,
            "repository_write": False,
            "command_execution": False,
            "artifact_transfer": True,
        })
        c = VALIDATOR.classify_v2_session_capabilities({
            "repository_read": False,
            "repository_write": False,
            "command_execution": True,
            "artifact_transfer": False,
        })
        self.assertEqual(a["workflow_class"], "CLASS_A")
        self.assertEqual(b["workflow_class"], "CLASS_B")
        self.assertEqual(c["workflow_class"], "CLASS_C")
        self.assertTrue(c["capabilities"]["command_execution"])
        self.assertFalse(c["capabilities"]["artifact_transfer"])
        for result in (a, b, c):
            self.assertFalse(result["grants_floppy_authority"])
            self.assertFalse(result["grants_repository_writer"])

    def test_contradictory_vector_stops(self) -> None:
        result = VALIDATOR.classify_v2_session_capabilities({
            "repository_read": False,
            "repository_write": True,
            "command_execution": False,
            "artifact_transfer": True,
        })
        self.assertEqual(result["status"], "STOP")
        self.assertEqual(result["reason"], "CONTRADICTORY_CAPABILITY_VECTOR")

    def test_class_b_profile_matches_superseded_semantics(self) -> None:
        profile = json.loads((ROOT / "specs/v2-compatibility-profile.json").read_text(encoding="utf-8"))
        record = profile["provider_capability_classes"]["CLASS_B"]
        self.assertTrue(record["repository_read"])
        self.assertFalse(record["repository_write"])
        self.assertFalse(record["command_execution"])
        self.assertTrue(record["artifact_transfer"])
        self.assertFalse(record["grants_floppy_authority"])
        self.assertFalse(record["grants_repository_writer"])

    def test_routes_and_existing_project_preservation_are_registered(self) -> None:
        routes = self.registry["routes"]
        self.assertEqual(set(routes), {"A", "B", "C"})
        self.assertEqual(routes["A"]["kind"], "IDEA_ONLY")
        self.assertEqual(routes["B"]["kind"], "EXISTING_NON_FLOPPY_PROJECT")
        self.assertEqual(routes["C"]["kind"], "EXISTING_FLOPPY_PROJECT")
        self.assertTrue(routes["B"]["preserve_existing_project"])
        self.assertEqual(routes["C"]["first_read"], ".floppy/manifest.json")
        self.assertTrue(routes["C"]["follow_required_read_order"])
        self.assertFalse(routes["C"]["restart_on_context_loss"])

    def test_user_and_project_onboarding_are_separate(self) -> None:
        separation = self.registry["onboarding_separation"]
        self.assertEqual(separation["user_onboarding"], "TRANSPORT_AND_ROUTE_SELECTION")
        self.assertEqual(separation["project_onboarding"], "onboarding/Floppy_1E.md")
        self.assertFalse(separation["user_onboarding_grants_implementation_authority"])
        self.assertFalse(separation["project_onboarding_grants_implementation_authority"])

    def test_paired_bootstrap_handoff_is_user_facing_not_runtime(self) -> None:
        paired = self.registry["paired_bootstrap_handoff"]
        self.assertEqual(paired["owner"], "V2-02")
        self.assertTrue(paired["issue_prompts_together"])
        self.assertTrue(paired["separate_conversations"])
        self.assertTrue(paired["same_accepted_project_origin"])
        self.assertFalse(paired["creates_implementation_authority"])
        self.assertFalse(paired["creates_repository_writer"])
        self.assertFalse(paired["automatic_prompt_generation_runtime"])
        self.assertEqual(paired["runtime_owner"], "V2-04")
        self.assertEqual(
            paired["shared_origin_minimum"],
            [
                "project identity",
                "original intended observable outcome",
                "accepted scope",
                "accepted exclusions",
                "major constraints",
                "verified starting state",
                "accepted project plan and roadmap",
                "exact repository checkpoint where applicable",
                "authority state",
                "Continuity Overseer identity",
                "initial Project Orchestrator identity",
            ],
        )
        text = STARTER.read_text(encoding="utf-8")
        self.assertIn("Continuity Overseer prompt", text)
        self.assertIn("Initial Project Orchestrator / Floppy Z prompt", text)

    def test_later_work_package_runtime_is_not_implemented(self) -> None:
        excluded = self.registry["not_implemented_here"]
        expected = {
            "durable_project_origin_storage_or_schema",
            "continuity_overseer_runtime",
            "continuity_overseer_persistence",
            "automatic_paired_prompt_generation_runtime",
            "durable_overseer_orchestrator_linkage",
            "scope_drift_detection",
            "orchestrator_succession",
            "replacement_orchestrator_lineage",
            "official_project_plan_generation_or_binding",
        }
        self.assertEqual(set(excluded), expected)

    def test_floppyctl_onboarding_is_read_only_registry_output(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "--root", str(ROOT), "onboarding"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout), self.registry)


if __name__ == "__main__":
    unittest.main()
