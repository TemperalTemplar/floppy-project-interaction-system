from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "project-seed" / ".floppy" / "orchestrator-registry.json"
HANDOFF_PATH = ROOT / "project-seed" / ".floppy" / "templates" / "orchestrator-handoff.md"
SEED_MANIFEST_PATH = ROOT / "project-seed" / ".floppy" / "manifest.json"
SYSTEM_MANIFEST_PATH = ROOT / "system-manifest.json"
BOOTSTRAP_PATH = ROOT / "BOOTSTRAP.md"
FLOPPY_Z_PATH = ROOT / "orchestrator" / "Floppy_Z.md"

ALLOWED_STATUSES = {"ACTIVE", "PAUSED", "HANDOFF_PENDING", "RETIRED"}


class RegistryValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RegistryValidationError(message)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_lf_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def validate_registry(registry: dict[str, Any]) -> None:
    require(set(registry["status_values"]) == ALLOWED_STATUSES, "invalid status values")

    rules = registry["rules"]
    require(rules["maximum_active_orchestrators"] == 1, "active orchestrator limit")
    require(rules["maximum_repository_writers"] == 1, "writer limit")
    require(rules["writer_requires_exact_authorization_reference"] is True, "writer reference rule")
    require(rules["status_or_role_grants_write_authority"] is False, "status/role authority rule")

    orchestrators = registry["orchestrators"]
    ids = [item["id"] for item in orchestrators]
    require(len(ids) == len(set(ids)), "duplicate orchestrator id")
    require(all(item["status"] in ALLOWED_STATUSES for item in orchestrators), "invalid orchestrator status")

    active = [item for item in orchestrators if item["status"] == "ACTIVE"]
    require(len(active) <= 1, "more than one active orchestrator")

    assignments = registry["current_assignments"]
    require(assignments["current_orchestrator"] in ids, "current orchestrator missing")
    current_model = assignments["current_section_working_model"]
    require(current_model is None or isinstance(current_model, str), "invalid section working model")

    writer = assignments["repository_writer"]
    reference = assignments["writer_authorization_reference"]
    require(writer is None or isinstance(writer, str), "repository writer must be one model or null")

    if writer is None:
        require(reference is None, "writer reference exists without writer")
    else:
        require(bool(writer.strip()), "repository writer is blank")
        require(isinstance(reference, str) and bool(reference.strip()), "writer authorization reference missing")

    for orchestrator in orchestrators:
        require(orchestrator.get("write_authority", False) is False, "role/status granted write authority")


class OrchestratorRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_json(REGISTRY_PATH)
        cls.seed_manifest = load_json(SEED_MANIFEST_PATH)
        cls.system_manifest = load_json(SYSTEM_MANIFEST_PATH)

    def test_seed_registry_is_valid(self) -> None:
        validate_registry(self.registry)

    def test_checkpoint_and_reporting_fields_are_present(self) -> None:
        checkpoint = self.registry["project_checkpoint"]
        self.assertEqual(
            set(checkpoint),
            {"repository", "branch", "worktree", "checkpoint"},
        )
        orchestrator = self.registry["orchestrators"][0]
        self.assertEqual(orchestrator["reports_to"], "ADMINISTRATOR")
        self.assertIn("current_section_working_model_reports_to", orchestrator)

    def test_multiple_active_orchestrators_are_rejected(self) -> None:
        candidate = copy.deepcopy(self.registry)
        candidate["orchestrators"].append(
            {
                "id": "SECOND_ORCHESTRATOR",
                "role": "PROJECT_ORCHESTRATOR",
                "status": "ACTIVE",
                "reports_to": "ADMINISTRATOR",
                "current_section_working_model_reports_to": "SECOND_ORCHESTRATOR",
            }
        )
        candidate["orchestrators"][0]["status"] = "ACTIVE"
        with self.assertRaises(RegistryValidationError):
            validate_registry(candidate)

    def test_multiple_repository_writers_are_rejected(self) -> None:
        candidate = copy.deepcopy(self.registry)
        candidate["current_assignments"]["repository_writer"] = [
            "MODEL_A",
            "MODEL_B",
        ]
        candidate["current_assignments"]["writer_authorization_reference"] = "AUTH"
        with self.assertRaises(RegistryValidationError):
            validate_registry(candidate)

    def test_writer_requires_exact_authorization_reference(self) -> None:
        candidate = copy.deepcopy(self.registry)
        candidate["current_assignments"]["repository_writer"] = "MODEL_A"
        candidate["current_assignments"]["writer_authorization_reference"] = ""
        with self.assertRaises(RegistryValidationError):
            validate_registry(candidate)

    def test_status_and_role_do_not_grant_write_authority(self) -> None:
        candidate = copy.deepcopy(self.registry)
        candidate["orchestrators"][0]["status"] = "ACTIVE"
        candidate["orchestrators"][0]["role"] = "PROJECT_ORCHESTRATOR"
        validate_registry(candidate)
        self.assertIsNone(candidate["current_assignments"]["repository_writer"])

        candidate["orchestrators"][0]["write_authority"] = True
        with self.assertRaises(RegistryValidationError):
            validate_registry(candidate)

    def test_handoff_template_contains_required_transfer_fields(self) -> None:
        text = HANDOFF_PATH.read_text(encoding="utf-8")
        required = (
            "Exact repository checkpoint",
            "Lifecycle state",
            "Current authority",
            "Current section working model",
            "Repository writer",
            "Writer authorization reference",
            "Completed work",
            "Unresolved work",
            "Next legal operation",
            "Prohibited operations",
        )
        for item in required:
            self.assertIn(item, text)

    def test_seed_manifest_loads_registry_after_floppy_e(self) -> None:
        config = self.seed_manifest["orchestrator_registry"]
        self.assertEqual(config["path"], ".floppy/orchestrator-registry.json")
        self.assertEqual(
            config["handoff_template"],
            ".floppy/templates/orchestrator-handoff.md",
        )
        order = self.seed_manifest["required_read_order"]
        self.assertEqual(
            order.index(".floppy/orchestrator-registry.json"),
            order.index(".floppy/floppies/Floppy-E-Current-Section.md") + 1,
        )

    def test_bootstrap_and_floppy_z_require_registration(self) -> None:
        bootstrap = BOOTSTRAP_PATH.read_text(encoding="utf-8")
        floppy_z = FLOPPY_Z_PATH.read_text(encoding="utf-8")
        for text in (bootstrap, floppy_z):
            self.assertIn(".floppy/orchestrator-registry.json", text)
            self.assertIn("ACTIVE", text)
            self.assertIn("HANDOFF_PENDING", text)
            self.assertIn("status and role", text.lower())
            self.assertIn("runtime", text.lower())

    def test_system_manifest_digests_match(self) -> None:
        registration = self.system_manifest["project_orchestrator_registration"]
        artifacts = registration["artifacts"]
        self.assertEqual(
            artifacts["registry_template"]["sha256"],
            sha256(REGISTRY_PATH),
        )
        self.assertEqual(
            artifacts["handoff_template"]["sha256"],
            sha256(HANDOFF_PATH),
        )
        self.assertEqual(
            self.system_manifest["orchestrator"]["sha256"],
            sha256_lf_text(FLOPPY_Z_PATH),
        )


if __name__ == "__main__":
    unittest.main()
