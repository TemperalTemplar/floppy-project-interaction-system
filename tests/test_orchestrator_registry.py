from __future__ import annotations

import copy
import hashlib
import json
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "project-seed" / ".floppy" / "orchestrator-registry.json"
LIFECYCLE_PATH = ROOT / "project-seed" / ".floppy" / "lifecycle-state.json"
HANDOFF_PATH = ROOT / "project-seed" / ".floppy" / "templates" / "orchestrator-handoff.md"
SEED_MANIFEST_PATH = ROOT / "project-seed" / ".floppy" / "manifest.json"
SYSTEM_MANIFEST_PATH = ROOT / "system-manifest.json"
BOOTSTRAP_PATH = ROOT / "BOOTSTRAP.md"
FLOPPY_Z_PATH = ROOT / "orchestrator" / "Floppy_Z.md"

ALLOWED_STATUSES = {"ACTIVE", "PAUSED", "HANDOFF_PENDING", "RETIRED"}


def load_validator_module():
    path = ROOT / "tools" / "validate_floppy.py"
    spec = importlib.util.spec_from_file_location("validate_floppy_self_hosted", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator_module()


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

    checkpoint = registry["project_checkpoint"]
    require(
        set(checkpoint) == {"repository", "branch", "worktree", "checkpoint"},
        "checkpoint fields",
    )
    for field in ("repository", "branch", "worktree", "checkpoint"):
        value = checkpoint[field]
        require(
            value is None or (isinstance(value, str) and bool(value.strip())),
            f"invalid checkpoint {field}",
        )

    provisioning = registry["provisioning"]
    require(provisioning["version"] == 1, "provisioning version")
    require(provisioning["status"] == "TEMPLATE", "provisioning status")
    require(
        provisioning["serialization"] == "UTF-8/LF/canonical-json-v1",
        "provisioning serialization",
    )
    require(
        provisioning["initialized_by"] == "tools/initialize_project.py",
        "provisioning initializer",
    )

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
        cls.lifecycle = load_json(LIFECYCLE_PATH)
        cls.seed_manifest = load_json(SEED_MANIFEST_PATH)
        cls.system_manifest = load_json(SYSTEM_MANIFEST_PATH)

    def test_seed_registry_is_valid(self) -> None:
        validate_registry(self.registry)

    def test_seed_lifecycle_state_is_onboarding_only(self) -> None:
        self.assertEqual(
            self.lifecycle["state_id"],
            "LC-ONBOARDING-REQUIRED",
        )
        self.assertIsNone(self.lifecycle["section"])
        self.assertIsNone(self.lifecycle["authorization_id"])
        self.assertIsNone(self.lifecycle["base_checkpoint"])
        self.assertEqual(
            self.lifecycle["dimensions"]["authority"],
            "NO_ACTIVE_WORK_AUTHORIZATION",
        )
        self.assertEqual(
            self.lifecycle["active_implementation_sections"],
            [],
        )

    def test_seed_control_records_are_canonical_json(self) -> None:
        for path in (REGISTRY_PATH, LIFECYCLE_PATH, SEED_MANIFEST_PATH):
            parsed = load_json(path)
            expected = (
                json.dumps(
                    parsed,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            ).encode("utf-8")
            actual = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            self.assertEqual(actual, expected)

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
            sha256_lf_text(REGISTRY_PATH),
        )
        provisioning = self.system_manifest["project_control_state_provisioning"]
        self.assertEqual(
            provisioning["artifacts"]["lifecycle_state_template"]["sha256"],
            sha256_lf_text(LIFECYCLE_PATH),
        )
        self.assertEqual(
            provisioning["artifacts"]["orchestrator_registry_template"]["sha256"],
            sha256_lf_text(REGISTRY_PATH),
        )
        self.assertEqual(
            artifacts["handoff_template"]["sha256"],
            sha256_lf_text(HANDOFF_PATH),
        )
        self.assertEqual(
            self.system_manifest["orchestrator"]["sha256"],
            sha256_lf_text(FLOPPY_Z_PATH),
        )


class CanonicalIntegratedControlModeTests(unittest.TestCase):
    AUTHORIZATION = "FS_11_INT_01_SELF_HOSTED_RECONCILIATION"
    WRITER = "FS_11_INT_01_WORKING_MODEL"
    BRANCH = "feature/fs-11-canonical-fixture"
    CHECKPOINT = "2" * 40

    def canonical_write(self, path: Path, value: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(
            (
                json.dumps(
                    value,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            ).encode("utf-8")
        )

    def manifest(self) -> dict:
        active = {
            "authorization_id": self.AUTHORIZATION,
            "authorization_kind": "section_implementation",
            "section": "FS-11",
            "repository": "example/floppy",
            "base_checkpoint": self.CHECKPOINT,
            "branch": self.BRANCH,
            "worktree": r"D:\A\Floppy-CTRL-02",
            "exact_file_scope": [".floppy/manifest.json"],
        }
        return {
            "status": "LC-SECTION-IMPLEMENTATION-IN-PROGRESS",
            "active_work_authorization": active,
            "repository_writer": self.WRITER,
            "writer_authorization_reference": self.AUTHORIZATION,
            "authority": {
                "active_implementation_section": "FS-11",
                "repository_writer": self.WRITER,
                "writer_authorization_reference": self.AUTHORIZATION,
            },
        }

    def lifecycle(self) -> dict:
        return {
            "state_id": "LC-SECTION-IMPLEMENTATION-IN-PROGRESS",
            "section": "FS-11",
            "authorization_id": self.AUTHORIZATION,
            "base_checkpoint": self.CHECKPOINT,
            "dimensions": {
                "roadmap": "ACCEPTED",
                "work_package": "ACCEPTED_PLANNING_BASELINE",
                "authority": "EXACT_SECTION_IMPLEMENTATION_AUTHORIZATION",
                "implementation": "IN_PROGRESS",
                "verification": "PENDING",
                "acceptance": "PENDING",
                "closeout": "NOT_PROPOSED",
                "migration": "NONE",
                "final_closure": "OPEN",
            },
            "active_implementation_sections": ["FS-11"],
            "evidence": ["canonical bootstrap fixture"],
        }

    def registry(self) -> dict:
        return {
            "artifact": "project-orchestrator-registry",
            "format_version": 1,
            "status_values": ["ACTIVE", "PAUSED", "HANDOFF_PENDING", "RETIRED"],
            "rules": {
                "maximum_active_orchestrators": 1,
                "maximum_repository_writers": 1,
                "writer_requires_exact_authorization_reference": True,
                "status_or_role_grants_write_authority": False,
            },
            "project_checkpoint": {
                "repository": "example/floppy",
                "branch": self.BRANCH,
                "worktree": r"D:\A\Floppy-CTRL-02",
                "checkpoint": self.CHECKPOINT,
            },
            "provisioning": {
                "version": 1,
                "status": "CANONICAL_INTEGRATED",
                "serialization": "UTF-8/LF/canonical-json-v1",
                "initialized_by": "FS_11_INT_01_BOOTSTRAP",
            },
            "current_assignments": {
                "current_orchestrator": "PROJECT_ORCHESTRATOR",
                "current_section_working_model": self.WRITER,
                "repository_writer": self.WRITER,
                "writer_authorization_reference": self.AUTHORIZATION,
            },
            "orchestrators": [
                {
                    "id": "PROJECT_ORCHESTRATOR",
                    "role": "PROJECT_ORCHESTRATOR",
                    "status": "PAUSED",
                },
                {
                    "id": self.WRITER,
                    "role": "SECTION_WORKING_MODEL",
                    "status": "ACTIVE",
                },
            ],
        }

    def fixture(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        schema_source = ROOT / "schemas/bce/1.0.0/bce-lifecycle-state.schema.json"
        schema_target = root / "schemas/bce/1.0.0/bce-lifecycle-state.schema.json"
        schema_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(schema_source, schema_target)
        manifest = self.manifest()
        self.canonical_write(root / ".floppy/manifest.json", manifest)
        self.canonical_write(root / ".floppy/lifecycle-state.json", self.lifecycle())
        self.canonical_write(root / ".floppy/orchestrator-registry.json", self.registry())
        return td, root, manifest

    def validate(self, root: Path, manifest: dict) -> list[str]:
        errors: list[str] = []
        VALIDATOR.validate_self_hosted_control_mode(root, manifest, errors)
        return errors

    def test_complete_canonical_bootstrap_passes(self) -> None:
        td, root, manifest = self.fixture()
        with td:
            self.assertEqual([], self.validate(root, manifest))

    def test_partial_canonical_bootstrap_fails_without_fallback(self) -> None:
        td, root, manifest = self.fixture()
        with td:
            (root / ".floppy/orchestrator-registry.json").unlink()
            self.assertEqual(
                [
                    "SELF_HOSTED_CONTROL_MODE_PARTIAL: lifecycle-state and "
                    "orchestrator registry must appear together"
                ],
                self.validate(root, manifest),
            )

    def test_canonical_records_must_be_canonical_json(self) -> None:
        td, root, manifest = self.fixture()
        with td:
            registry_path = root / ".floppy/orchestrator-registry.json"
            registry_path.write_text(
                json.dumps(self.registry(), indent=2) + "\n",
                encoding="utf-8",
            )
            errors = self.validate(root, manifest)
            self.assertIn(
                "canonical orchestrator registry serialization is not canonical UTF-8/LF JSON",
                errors,
            )

    def test_canonical_authorization_projection_mismatch_fails(self) -> None:
        td, root, manifest = self.fixture()
        with td:
            lifecycle = self.lifecycle()
            lifecycle["authorization_id"] = "STALE"
            self.canonical_write(root / ".floppy/lifecycle-state.json", lifecycle)
            self.assertIn(
                "CANONICAL_INTEGRATED_AUTHORIZATION_MISMATCH",
                self.validate(root, manifest),
            )

    def test_canonical_registry_requires_one_registered_writer(self) -> None:
        td, root, manifest = self.fixture()
        with td:
            registry = self.registry()
            registry["orchestrators"] = registry["orchestrators"][:1]
            self.canonical_write(root / ".floppy/orchestrator-registry.json", registry)
            self.assertIn(
                "CANONICAL_INTEGRATED_WRITER_REGISTRATION_INVALID",
                self.validate(root, manifest),
            )

    def test_canonical_registry_rejects_multiple_active_orchestrators(self) -> None:
        td, root, manifest = self.fixture()
        with td:
            registry = self.registry()
            registry["orchestrators"][0]["status"] = "ACTIVE"
            self.canonical_write(root / ".floppy/orchestrator-registry.json", registry)
            self.assertIn(
                "CANONICAL_INTEGRATED_MULTIPLE_ACTIVE_ORCHESTRATORS",
                self.validate(root, manifest),
            )

    def test_canonical_checkpoint_must_match_active_authorization(self) -> None:
        td, root, manifest = self.fixture()
        with td:
            registry = self.registry()
            registry["project_checkpoint"]["checkpoint"] = "3" * 40
            self.canonical_write(root / ".floppy/orchestrator-registry.json", registry)
            self.assertIn(
                "CANONICAL_INTEGRATED_CHECKPOINT_MISMATCH",
                self.validate(root, manifest),
            )

    def test_canonical_bootstrap_marker_must_be_cleared(self) -> None:
        td, root, manifest = self.fixture()
        with td:
            registry = self.registry()
            registry["provisioning"]["status"] = "TEMPLATE"
            self.canonical_write(root / ".floppy/orchestrator-registry.json", registry)
            self.assertIn(
                "CANONICAL_INTEGRATED_BOOTSTRAP_MARKER_REMAINS",
                self.validate(root, manifest),
            )


# V2_04_ORCHESTRATOR_REGISTRY_TEST
class V204OrchestratorRegistryBoundaryTests(unittest.TestCase):
    def test_continuity_overseer_does_not_replace_registry(self) -> None:
        system = load_json(SYSTEM_MANIFEST_PATH)
        registry = load_json(REGISTRY_PATH)
        continuity = system["continuity_overseer"]
        self.assertEqual(
            continuity["orchestrator_registry_authority"],
            ".floppy/orchestrator-registry.json",
        )
        self.assertFalse(
            continuity["competing_current_controller_registry"]
        )
        self.assertEqual(
            registry["rules"]["maximum_active_orchestrators"], 1
        )

    def test_handoff_template_contains_v2_04_succession_fingerprint(self) -> None:
        text = HANDOFF_PATH.read_text(encoding="utf-8")
        for value in (
            "Continuity Overseer ID",
            "Succession ID",
            "Authority state SHA-256",
            "Predecessor availability",
            "Successor Project Orchestrator ID",
            "Stale-handoff verification result",
        ):
            self.assertIn(value, text)

if __name__ == "__main__":
    unittest.main()
