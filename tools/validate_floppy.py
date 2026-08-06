#!/usr/bin/env python3
"""Validate either the Floppy source repository or an initialized project."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SOURCE_REQUIRED = [
    "VERSION",
    "README.md",
    "ABOUT.md",
    "BOOTSTRAP.md",
    "system-manifest.json",
    "orchestrator/Floppy_Z.md",
    "orchestrator/README.md",
    "onboarding/Floppy_1E.md",
    "onboarding/README.md",
    "protocols/00-source-repository-policy.md",
    "protocols/01-new-project-onboarding.md",
    "protocols/02-project-intake.md",
    "protocols/03-active-session.md",
    "protocols/04-everyday-closeout.md",
    "protocols/05-revision-application.md",
    "project-seed/.floppy/manifest.json",
    "project-seed/.floppy/roadmap/roadmap.json",
    "project-seed/.floppy/roadmap/roadmap.md",
    "specs/lifecycle-state-model.md",
    "specs/lifecycle-transition-table.json",
    "schemas/drafts/bce-lifecycle-state.schema.json",
    "schemas/drafts/bce-work-authorization.schema.json",
    "schemas/drafts/bce-lifecycle-transition.schema.json",
    "schemas/bce/1.0.0/bce-lifecycle-state.schema.json",
    "schemas/bce/1.0.0/bce-work-authorization.schema.json",
    "schemas/bce/1.0.0/bce-lifecycle-transition.schema.json",
    "tools/initialize_project.py",
]

PROJECT_REQUIRED = [
    ".floppy/manifest.json",
    ".floppy/START-HERE.md",
    ".floppy/floppies/Floppy-A-HITL.md",
    ".floppy/floppies/Floppy-B-Development-Issues.md",
    ".floppy/floppies/Floppy-C-Project-Baseline.md",
    ".floppy/floppies/Floppy-D-Project-Map.md",
    ".floppy/floppies/Floppy-E-Current-Section.md",
    ".floppy/roadmap/roadmap.json",
    ".floppy/roadmap/roadmap.md",
]

DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"

LIFECYCLE_ARTIFACTS = {
    "state_model": {
        "path": "specs/lifecycle-state-model.md",
    },
    "transition_table": {
        "path": "specs/lifecycle-transition-table.json",
    },
    "draft_lifecycle_state_schema": {
        "path": "schemas/drafts/bce-lifecycle-state.schema.json",
        "$id": (
            "urn:floppy-project-interaction-system:"
            "draft:bce-lifecycle-state:fs-01"
        ),
    },
    "draft_work_authorization_schema": {
        "path": "schemas/drafts/bce-work-authorization.schema.json",
        "$id": (
            "urn:floppy-project-interaction-system:"
            "draft:bce-work-authorization:fs-01"
        ),
    },
    "draft_lifecycle_transition_schema": {
        "path": "schemas/drafts/bce-lifecycle-transition.schema.json",
        "$id": (
            "urn:floppy-project-interaction-system:"
            "draft:bce-lifecycle-transition:fs-01"
        ),
    },
}


NORMATIVE_BCE_ARTIFACTS = {
    "lifecycle_state": {
        "path": "schemas/bce/1.0.0/bce-lifecycle-state.schema.json",
        "$id": (
            "urn:floppy-project-interaction-system:"
            "schema:bce-lifecycle-state:1.0.0"
        ),
    },
    "work_authorization": {
        "path": "schemas/bce/1.0.0/bce-work-authorization.schema.json",
        "$id": (
            "urn:floppy-project-interaction-system:"
            "schema:bce-work-authorization:1.0.0"
        ),
    },
    "lifecycle_transition": {
        "path": "schemas/bce/1.0.0/bce-lifecycle-transition.schema.json",
        "$id": (
            "urn:floppy-project-interaction-system:"
            "schema:bce-lifecycle-transition:1.0.0"
        ),
    },
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

MANDATORY_PROHIBITED_IMPLICATIONS = {
    "PI-001": "Roadmap acceptance does not imply section authorization.",
    "PI-002": "Work-package acceptance does not imply section authorization.",
    "PI-003": "Draft creation does not imply section activation.",
    "PI-004": (
        "Implementation completion does not imply verification completion."
    ),
    "PI-005": (
        "Implementation completion does not imply administrator acceptance."
    ),
    "PI-006": (
        "Verification completion does not imply administrator acceptance."
    ),
    "PI-007": "Section acceptance does not imply section closeout.",
    "PI-008": (
        "A closeout proposal does not imply closeout application."
    ),
    "PI-009": (
        "Section closeout does not imply next-section authorization."
    ),
    "PI-010": "A migration plan does not imply migration authorization.",
    "PI-011": (
        "Migration application does not imply migration verification."
    ),
    "PI-012": (
        "A final-closure proposal does not imply final closure."
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--mode", choices=("source", "project"), required=True)
    return parser.parse_args()


def validate_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return None

    if not isinstance(data, dict):
        errors.append(f"JSON root must be an object: {path}")
        return None

    return data


def sha256(path: Path) -> str:
    """Return a stable UTF-8 text digest with LF line endings.

    Git may materialize tracked text as CRLF on Windows. Registered source
    artifacts are UTF-8 text, so integrity checks normalize CRLF and lone CR
    to LF before hashing. This preserves one digest across supported platforms.
    """

    text = path.read_text(encoding="utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def collect_refs(value: Any) -> list[str]:
    refs: list[str] = []

    if isinstance(value, dict):
        for key, child in value.items():
            if key == "$ref" and isinstance(child, str):
                refs.append(child)
            refs.extend(collect_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.extend(collect_refs(child))

    return refs


def validate_unique_ids(
    values: Any,
    label: str,
    errors: list[str],
) -> set[str]:
    if not isinstance(values, list):
        errors.append(f"{label} must be a list")
        return set()

    identifiers: list[str] = []

    for item in values:
        if not isinstance(item, dict):
            errors.append(f"{label} entries must be objects")
            continue

        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"{label} entry has missing or invalid id")
            continue

        identifiers.append(identifier)

    if len(identifiers) != len(set(identifiers)):
        errors.append(f"{label} identifiers must be unique")

    return set(identifiers)


def validate_draft_schema(
    path: Path,
    expected_id: str,
    errors: list[str],
) -> None:
    schema = validate_json(path, errors)
    if schema is None:
        return

    if schema.get("$schema") != DRAFT_2020_12:
        errors.append(f"draft schema does not declare Draft 2020-12: {path}")

    if schema.get("$id") != expected_id:
        errors.append(f"draft schema has incorrect $id: {path}")

    if schema.get("status") != "draft_non_normative":
        errors.append(f"draft schema status is not draft_non_normative: {path}")

    if schema.get("normative_section") != "FS-02":
        errors.append(f"draft schema normative_section is not FS-02: {path}")

    if schema.get("current_section") != "FS-01":
        errors.append(f"draft schema current_section is not FS-01: {path}")

    if schema.get("production_enforcement") is not False:
        errors.append(f"draft schema production_enforcement must be false: {path}")

    definitions = schema.get("$defs")
    if not isinstance(definitions, dict) or not definitions:
        errors.append(f"draft schema must contain non-empty $defs: {path}")
        return

    refs = collect_refs(schema)
    if not refs:
        errors.append(f"draft schema must contain local $ref values: {path}")
        return

    for ref in refs:
        prefix = "#/$defs/"
        if not ref.startswith(prefix):
            errors.append(f"draft schema contains non-local $ref {ref}: {path}")
            continue

        target = ref.removeprefix(prefix)
        if target not in definitions:
            errors.append(f"draft schema contains unresolved $ref {ref}: {path}")


def validate_transition_table(path: Path, errors: list[str]) -> None:
    table = validate_json(path, errors)
    if table is None:
        return

    if table.get("format_version") != 1:
        errors.append("lifecycle transition table format_version must be 1")

    if table.get("current_section") != "FS-01":
        errors.append("lifecycle transition table current_section must be FS-01")

    if table.get("declarative_only") is not True:
        errors.append("lifecycle transition table must be declarative only")

    if table.get("execution_capability") is not False:
        errors.append("lifecycle transition table must not claim execution capability")

    if table.get("applies_transitions") is not False:
        errors.append("lifecycle transition table must not apply transitions")

    if table.get("writes_lifecycle_state") is not False:
        errors.append("lifecycle transition table must not write lifecycle state")

    if table.get("production_schema_enforcement") is not False:
        errors.append(
            "lifecycle transition table must not claim production schema enforcement"
        )

    if table.get("one_active_implementation_section_maximum") != 1:
        errors.append("lifecycle transition table must permit at most one active section")

    dimensions = table.get("dimensions")
    if not isinstance(dimensions, dict):
        errors.append("lifecycle transition table dimensions must be an object")
    elif set(dimensions) != REQUIRED_DIMENSIONS:
        errors.append("lifecycle transition table dimensions are incomplete or unknown")

    states = table.get("states")
    state_ids = validate_unique_ids(states, "lifecycle states", errors)

    if isinstance(states, list):
        for state in states:
            if not isinstance(state, dict):
                continue

            state_dimensions = state.get("dimensions")
            if not isinstance(state_dimensions, dict):
                errors.append(
                    f"lifecycle state {state.get('id')} dimensions must be an object"
                )
            elif set(state_dimensions) != REQUIRED_DIMENSIONS:
                errors.append(
                    f"lifecycle state {state.get('id')} dimensions are incomplete"
                )

    transitions = table.get("transitions")
    validate_unique_ids(transitions, "lifecycle transitions", errors)

    if isinstance(transitions, list):
        for transition in transitions:
            if not isinstance(transition, dict):
                continue

            transition_id = transition.get("id", "<unknown>")
            missing_fields = REQUIRED_TRANSITION_FIELDS - set(transition)
            if missing_fields:
                errors.append(
                    f"transition {transition_id} is missing required fields: "
                    f"{', '.join(sorted(missing_fields))}"
                )
                continue

            from_state_ids = transition.get("from_state_ids")
            if not isinstance(from_state_ids, list) or not from_state_ids:
                errors.append(f"transition {transition_id} has no from-state")
            else:
                for state_id in from_state_ids:
                    if state_id not in state_ids:
                        errors.append(
                            f"transition {transition_id} references unknown "
                            f"from-state {state_id}"
                        )

            to_state_id = transition.get("to_state_id")
            if to_state_id not in state_ids:
                errors.append(
                    f"transition {transition_id} references unknown "
                    f"to-state {to_state_id}"
                )

            changed_dimensions = transition.get("changed_dimensions")
            if not isinstance(changed_dimensions, list) or not changed_dimensions:
                errors.append(
                    f"transition {transition_id} has no changed dimensions"
                )
            else:
                allowed_dimensions = REQUIRED_DIMENSIONS | {
                    "active_implementation_section"
                }
                unknown_dimensions = set(changed_dimensions) - allowed_dimensions
                if unknown_dimensions:
                    errors.append(
                        f"transition {transition_id} has unknown changed dimensions: "
                        f"{', '.join(sorted(unknown_dimensions))}"
                    )

            authority = transition.get("required_human_authority")
            if not isinstance(authority, dict):
                errors.append(
                    f"transition {transition_id} human authority must be an object"
                )
            else:
                if not authority.get("actor"):
                    errors.append(
                        f"transition {transition_id} human authority actor is missing"
                    )
                if not authority.get("decision"):
                    errors.append(
                        f"transition {transition_id} human authority decision is missing"
                    )

            for field in (
                "preconditions",
                "required_inputs",
                "required_outputs",
                "stop_conditions",
                "forbidden_side_effects",
            ):
                value = transition.get(field)
                if not isinstance(value, list) or not value:
                    errors.append(
                        f"transition {transition_id} must contain non-empty {field}"
                    )

    implications = table.get("prohibited_implications")
    implication_ids = validate_unique_ids(
        implications,
        "prohibited implications",
        errors,
    )

    if isinstance(implications, list):
        implication_by_id = {
            item.get("id"): item
            for item in implications
            if isinstance(item, dict)
        }

        for implication_id, statement in MANDATORY_PROHIBITED_IMPLICATIONS.items():
            if implication_id not in implication_ids:
                errors.append(
                    f"mandatory prohibited implication is missing: {implication_id}"
                )
                continue

            if implication_by_id[implication_id].get("statement") != statement:
                errors.append(
                    f"mandatory prohibited implication has changed: {implication_id}"
                )


def validate_lifecycle_artifacts(
    root: Path,
    manifest: dict[str, Any],
    errors: list[str],
) -> None:
    lifecycle = manifest.get("lifecycle_specification")
    if not isinstance(lifecycle, dict):
        errors.append("system manifest does not register FS-01 lifecycle artifacts")
        return

    if lifecycle.get("section") != "FS-01":
        errors.append("system manifest lifecycle section is not FS-01")

    if lifecycle.get("status") != "formal_specification":
        errors.append("system manifest lifecycle status is not formal_specification")

    if lifecycle.get("declarative_only") is not True:
        errors.append("system manifest lifecycle model must be declarative only")

    for false_field in (
        "execution_capability",
        "applies_transitions",
        "writes_lifecycle_state",
        "production_enforcement",
    ):
        if lifecycle.get(false_field) is not False:
            errors.append(
                f"system manifest lifecycle {false_field} must be false"
            )

    artifacts = lifecycle.get("artifacts")
    if not isinstance(artifacts, dict):
        errors.append("system manifest lifecycle artifacts must be an object")
        return

    if set(artifacts) != set(LIFECYCLE_ARTIFACTS):
        errors.append("system manifest lifecycle artifact registry is incomplete")
        return

    for artifact_name, expected in LIFECYCLE_ARTIFACTS.items():
        record = artifacts.get(artifact_name)
        if not isinstance(record, dict):
            errors.append(
                f"system manifest lifecycle artifact is invalid: {artifact_name}"
            )
            continue

        expected_path = expected["path"]
        if record.get("path") != expected_path:
            errors.append(
                f"system manifest lifecycle artifact path is invalid: {artifact_name}"
            )
            continue

        artifact_path = root / expected_path
        if not artifact_path.is_file():
            errors.append(f"lifecycle artifact is missing: {expected_path}")
            continue

        digest = record.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            errors.append(
                f"system manifest lifecycle artifact digest is invalid: {artifact_name}"
            )
        elif digest != sha256(artifact_path):
            errors.append(
                f"lifecycle artifact digest does not match: {expected_path}"
            )

        expected_id = expected.get("$id")
        if expected_id is not None and record.get("$id") != expected_id:
            errors.append(
                f"system manifest lifecycle artifact $id is invalid: {artifact_name}"
            )

    validate_transition_table(
        root / LIFECYCLE_ARTIFACTS["transition_table"]["path"],
        errors,
    )

    for artifact_name in (
        "draft_lifecycle_state_schema",
        "draft_work_authorization_schema",
        "draft_lifecycle_transition_schema",
    ):
        expected = LIFECYCLE_ARTIFACTS[artifact_name]
        validate_draft_schema(
            root / expected["path"],
            expected["$id"],
            errors,
        )



def validate_normative_bce_schemas(
    root: Path,
    manifest: dict[str, Any],
    errors: list[str],
) -> None:
    """Validate registered FS-02 schemas as development tooling only."""

    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        errors.append(
            "jsonschema is required for normative BCE schema "
            f"development and verification only: {exc}"
        )
        return

    registry = manifest.get("normative_bce_schemas")
    if not isinstance(registry, dict):
        errors.append("system manifest does not register normative BCE schemas")
        return

    expected_metadata = {
        "section": "FS-02",
        "status": "reusable_product",
        "schema_version": "1.0.0",
        "json_schema_draft": "2020-12",
        "ordinary_operation_required": False,
        "production_enforcement": False,
        "validation_scope": "development_and_verification_only",
        "validator": "tools/validate_floppy.py",
    }

    for field, expected in expected_metadata.items():
        if registry.get(field) != expected:
            errors.append(
                f"system manifest normative BCE {field} is invalid"
            )

    artifacts = registry.get("artifacts")
    if not isinstance(artifacts, dict):
        errors.append("system manifest normative BCE artifacts are invalid")
        return

    if set(artifacts) != set(NORMATIVE_BCE_ARTIFACTS):
        errors.append(
            "system manifest normative BCE artifact registry is incomplete"
        )
        return

    for artifact_name, expected in NORMATIVE_BCE_ARTIFACTS.items():
        record = artifacts.get(artifact_name)
        if not isinstance(record, dict):
            errors.append(
                f"system manifest normative BCE artifact is invalid: "
                f"{artifact_name}"
            )
            continue

        expected_path = expected["path"]
        if record.get("path") != expected_path:
            errors.append(
                f"system manifest normative BCE artifact path is invalid: "
                f"{artifact_name}"
            )
            continue

        schema_path = root / expected_path
        schema = validate_json(schema_path, errors)
        if schema is None:
            continue

        expected_id = expected["$id"]
        if record.get("$id") != expected_id:
            errors.append(
                f"system manifest normative BCE artifact $id is invalid: "
                f"{artifact_name}"
            )

        digest = record.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            errors.append(
                f"system manifest normative BCE artifact digest is invalid: "
                f"{artifact_name}"
            )
        elif digest != sha256(schema_path):
            errors.append(
                f"normative BCE artifact digest does not match: "
                f"{expected_path}"
            )

        if schema.get("$schema") != DRAFT_2020_12:
            errors.append(
                f"normative BCE schema does not declare Draft 2020-12: "
                f"{schema_path}"
            )

        if schema.get("$id") != expected_id:
            errors.append(
                f"normative BCE schema has incorrect $id: {schema_path}"
            )

        if schema.get("status") != "normative":
            errors.append(
                f"normative BCE schema status is not normative: {schema_path}"
            )

        if schema.get("schema_version") != "1.0.0":
            errors.append(
                f"normative BCE schema version is not 1.0.0: {schema_path}"
            )

        if schema.get("normative_section") != "FS-02":
            errors.append(
                f"normative BCE schema section is not FS-02: {schema_path}"
            )

        if schema.get("production_enforcement") is not False:
            errors.append(
                f"normative BCE schema production_enforcement must be false: "
                f"{schema_path}"
            )

        for ref in collect_refs(schema):
            if not ref.startswith("#/$defs/"):
                errors.append(
                    f"normative BCE schema contains non-local $ref {ref}: "
                    f"{schema_path}"
                )

        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            errors.append(
                f"invalid normative BCE Draft 2020-12 schema "
                f"{schema_path}: {exc}"
            )



def validate_verification_only_lifecycle_extension(root: Path, manifest: dict[str, Any], errors: list[str]) -> None:
    """Validate the CTRL-02 lifecycle-state 1.1.0 extension."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        errors.append(f"jsonschema is required for CTRL-02 validation: {exc}")
        return
    registry = manifest.get("verification_only_lifecycle_extension")
    if not isinstance(registry, dict):
        errors.append("system manifest does not register verification-only lifecycle extension")
        return
    record = registry.get("artifacts", {}).get("lifecycle_state")
    if not isinstance(record, dict):
        errors.append("verification-only lifecycle-state registration is invalid")
        return
    path = root / record.get("path", "")
    schema = validate_json(path, errors)
    if schema is None:
        return
    if schema.get("$id") != "urn:floppy-project-interaction-system:schema:bce-lifecycle-state:1.1.0": errors.append("verification-only lifecycle-state $id is invalid")
    if schema.get("schema_version") != "1.1.0": errors.append("verification-only lifecycle-state version is invalid")
    if record.get("sha256") != sha256(path): errors.append("verification-only lifecycle-state digest does not match")
    try: Draft202012Validator.check_schema(schema)
    except Exception as exc: errors.append(f"invalid verification-only lifecycle schema: {exc}")

def validate_verification_only_contract(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("work_package_type") != "VERIFICATION_ONLY_NO_REUSABLE_PRODUCT_CHANGE": return errors
    if record.get("implementation_state") != "NOT_REQUIRED": errors.append("VERIFICATION_ONLY_IMPLEMENTATION_MUST_BE_NOT_REQUIRED")
    if record.get("authorization_id") is not None: errors.append("VERIFICATION_ONLY_AUTHORIZATION_MUST_BE_NULL")
    if record.get("repository_writer") is not None: errors.append("VERIFICATION_ONLY_WRITER_MUST_BE_NULL")
    if record.get("writer_authorization_reference") is not None: errors.append("VERIFICATION_ONLY_WRITER_REFERENCE_MUST_BE_NULL")
    if record.get("reusable_product_paths") not in ([], None): errors.append("VERIFICATION_ONLY_PRODUCT_PATHS_MUST_BE_EMPTY")
    if record.get("reusable_product_commits") not in ([], None): errors.append("VERIFICATION_ONLY_PRODUCT_COMMITS_MUST_BE_EMPTY")
    if record.get("product_commit") is not None: errors.append("VERIFICATION_ONLY_PRODUCT_COMMIT_MUST_BE_NULL")
    return errors

SEMANTIC_SCHEMA_PATHS = {
    "lifecycle_states": "schemas/bce/1.0.0/bce-lifecycle-state.schema.json",
    "work_authorizations": "schemas/bce/1.0.0/bce-work-authorization.schema.json",
    "lifecycle_transitions": "schemas/bce/1.0.0/bce-lifecycle-transition.schema.json",
}


def _semantic_add(errors: list[str], message: str) -> None:
    if message not in errors:
        errors.append(message)


def _semantic_list(
    bundle: dict[str, Any],
    name: str,
    errors: list[str],
) -> list[dict[str, Any]]:
    value = bundle.get(name)
    if not isinstance(value, list) or not all(
        isinstance(item, dict) for item in value
    ):
        _semantic_add(errors, f"SEMANTIC_RECORD_LIST_INVALID: {name}")
        return []
    return value


def _semantic_index(
    records: list[dict[str, Any]],
    id_field: str,
    label: str,
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    encoded: dict[str, str] = {}

    for record in records:
        identifier = record.get(id_field)
        if not isinstance(identifier, str) or not identifier:
            _semantic_add(errors, f"SEMANTIC_IDENTIFIER_MISSING: {label}")
            continue

        canonical = json.dumps(
            record,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        if identifier in encoded:
            kind = (
                "DUPLICATE"
                if encoded[identifier] == canonical
                else "CONFLICTING"
            )
            _semantic_add(
                errors,
                f"SEMANTIC_{kind}_IDENTIFIER: {label} {identifier}",
            )
            continue

        encoded[identifier] = canonical
        result[identifier] = record

    return result


def _semantic_schema_check(
    root: Path,
    records: dict[str, list[dict[str, Any]]],
    errors: list[str],
) -> None:
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        _semantic_add(
            errors,
            f"SEMANTIC_SCHEMA_DEPENDENCY_MISSING: {exc}",
        )
        return

    for name, relative in SEMANTIC_SCHEMA_PATHS.items():
        schema = validate_json(root / relative, errors)
        if schema is None:
            continue

        validator = Draft202012Validator(schema)
        for index, record in enumerate(records[name]):
            if name == "lifecycle_states" and record.get("schema_version") == "1.1.0":
                schema_11 = validate_json(root / "schemas/bce/1.1.0/bce-lifecycle-state.schema.json", errors)
                if schema_11 is not None:
                    validator = Draft202012Validator(schema_11)
            failures = sorted(
                validator.iter_errors(record),
                key=lambda item: (
                    tuple(str(part) for part in item.absolute_path),
                    item.message,
                ),
            )
            if failures:
                location = ".".join(
                    str(part) for part in failures[0].absolute_path
                ) or "<root>"
                _semantic_add(
                    errors,
                    f"SEMANTIC_SCHEMA_INVALID: {name}[{index}] "
                    f"{location}",
                )


def _semantic_repository_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None

    normalized = value.replace("\\", "/")
    parts = normalized.split("/")
    if (
        normalized.startswith("/")
        or (parts and parts[0].endswith(":"))
        or any(part in {"", ".", ".."} for part in parts)
    ):
        return None
    return normalized


def validate_bce_semantics(
    bundle: dict[str, Any],
    root: Path | None = None,
) -> list[str]:
    """Validate cross-record BCE relationships without changing any record."""

    if not isinstance(bundle, dict):
        return ["SEMANTIC_BUNDLE_INVALID"]

    root = (
        root.expanduser().resolve()
        if root is not None
        else Path(__file__).resolve().parents[1]
    )
    errors: list[str] = []

    states = _semantic_list(bundle, "lifecycle_states", errors)
    authorizations = _semantic_list(
        bundle,
        "work_authorizations",
        errors,
    )
    transitions = _semantic_list(
        bundle,
        "lifecycle_transitions",
        errors,
    )
    bindings = _semantic_list(
        bundle,
        "authorization_bindings",
        errors,
    )
    represented = _semantic_list(
        bundle,
        "represented_transitions",
        errors,
    )
    evidence_records = _semantic_list(bundle, "evidence", errors)
    commits = _semantic_list(bundle, "commits", errors)

    _semantic_schema_check(
        root,
        {
            "lifecycle_states": states,
            "work_authorizations": authorizations,
            "lifecycle_transitions": transitions,
        },
        errors,
    )

    state_by_id = _semantic_index(
        states,
        "state_id",
        "lifecycle_state",
        errors,
    )
    authorization_by_id = _semantic_index(
        authorizations,
        "authorization_id",
        "work_authorization",
        errors,
    )
    transition_by_id = _semantic_index(
        transitions,
        "id",
        "lifecycle_transition",
        errors,
    )
    binding_by_id = _semantic_index(
        bindings,
        "authorization_id",
        "authorization_binding",
        errors,
    )
    represented_by_id = _semantic_index(
        represented,
        "id",
        "represented_transition",
        errors,
    )
    evidence_by_id = _semantic_index(
        evidence_records,
        "id",
        "evidence",
        errors,
    )
    _semantic_index(commits, "id", "commit", errors)

    table = validate_json(
        root / "specs/lifecycle-transition-table.json",
        errors,
    )
    if table is None:
        return errors

    state_definitions = {
        record["id"]: record
        for record in table.get("states", [])
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }
    transition_definitions = {
        record["id"]: record
        for record in table.get("transitions", [])
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }

    if len(states) != 1:
        _semantic_add(
            errors,
            "SEMANTIC_CURRENT_LIFECYCLE_COUNT: "
            f"expected 1 found {len(states)}",
        )
        current_state = None
    else:
        current_state = states[0]

    active_authorization_id: str | None = None
    active_authorization: dict[str, Any] | None = None

    if current_state is not None:
        state_id = current_state.get("state_id")
        definition = state_definitions.get(state_id)
        if definition is None:
            _semantic_add(
                errors,
                f"SEMANTIC_UNKNOWN_LIFECYCLE_STATE: {state_id}",
            )
        elif current_state.get("dimensions") != definition.get(
            "dimensions"
        ):
            _semantic_add(
                errors,
                f"SEMANTIC_LIFECYCLE_DIMENSIONS_MISMATCH: {state_id}",
            )

        dimensions = current_state.get("dimensions", {})
        authority = (
            dimensions.get("authority")
            if isinstance(dimensions, dict)
            else None
        )
        section = current_state.get("section")
        authorization_id = current_state.get("authorization_id")
        active_sections = current_state.get(
            "active_implementation_sections"
        )

        if authority in {
            "EXACT_SECTION_IMPLEMENTATION_AUTHORIZATION",
            "EXACT_MIGRATION_AUTHORIZATION",
        }:
            if (
                not isinstance(authorization_id, str)
                or authorization_id not in authorization_by_id
            ):
                _semantic_add(
                    errors,
                    "SEMANTIC_ACTIVE_AUTHORIZATION_MISSING",
                )
            else:
                active_authorization_id = authorization_id
                active_authorization = authorization_by_id[authorization_id]

            expected_sections = (
                [section]
                if authority
                == "EXACT_SECTION_IMPLEMENTATION_AUTHORIZATION"
                else []
            )
            if active_sections != expected_sections:
                _semantic_add(
                    errors,
                    "SEMANTIC_ACTIVE_SECTION_MISMATCH",
                )
        else:
            if authorization_id is not None:
                _semantic_add(
                    errors,
                    "SEMANTIC_UNAUTHORIZED_AUTHORIZATION_REFERENCE",
                )
            if active_sections != []:
                _semantic_add(
                    errors,
                    "SEMANTIC_UNAUTHORIZED_ACTIVE_SECTION",
                )

        if active_authorization is not None:
            if active_authorization.get("section") != section:
                _semantic_add(
                    errors,
                    "SEMANTIC_AUTHORIZATION_SECTION_MISMATCH",
                )
            if (
                active_authorization.get("base_checkpoint")
                != current_state.get("base_checkpoint")
            ):
                _semantic_add(
                    errors,
                    "SEMANTIC_AUTHORIZATION_CHECKPOINT_MISMATCH",
                )

    registry = bundle.get("orchestrator_registry")
    if not isinstance(registry, dict):
        _semantic_add(errors, "SEMANTIC_ORCHESTRATOR_REGISTRY_INVALID")
        registry = {}

    orchestrator_by_id = _semantic_index(
        [
            record
            for record in registry.get("orchestrators", [])
            if isinstance(record, dict)
        ],
        "id",
        "orchestrator",
        errors,
    )
    assignments = registry.get("current_assignments")
    if not isinstance(assignments, dict):
        _semantic_add(errors, "SEMANTIC_CURRENT_ASSIGNMENTS_INVALID")
        assignments = {}

    current_orchestrator = assignments.get("current_orchestrator")
    if (
        current_orchestrator is not None
        and current_orchestrator not in orchestrator_by_id
    ):
        _semantic_add(
            errors,
            f"SEMANTIC_UNKNOWN_ORCHESTRATOR: {current_orchestrator}",
        )

    repository_writer = assignments.get("repository_writer")
    writer_valid = (
        repository_writer is None
        or isinstance(repository_writer, str)
    )
    if isinstance(repository_writer, list) and len(repository_writer) > 1:
        _semantic_add(
            errors,
            "SEMANTIC_MULTIPLE_CURRENT_WRITERS: "
            f"found {len(repository_writer)}",
        )
        writer_valid = False
    elif not writer_valid:
        _semantic_add(errors, "SEMANTIC_REPOSITORY_WRITER_INVALID")

    if active_authorization_id is not None:
        binding = binding_by_id.get(active_authorization_id)
        if binding is None:
            _semantic_add(
                errors,
                "SEMANTIC_AUTHORIZATION_BINDING_MISSING: "
                f"{active_authorization_id}",
            )
        else:
            orchestrator_id = binding.get("orchestrator_id")
            if orchestrator_id not in orchestrator_by_id:
                _semantic_add(
                    errors,
                    f"SEMANTIC_UNKNOWN_ORCHESTRATOR: {orchestrator_id}",
                )
            elif orchestrator_id != current_orchestrator:
                _semantic_add(
                    errors,
                    "SEMANTIC_ORCHESTRATOR_ASSIGNMENT_MISMATCH",
                )

            working_model_id = binding.get("working_model_id")
            if working_model_id != assignments.get(
                "current_section_working_model"
            ):
                _semantic_add(
                    errors,
                    f"SEMANTIC_UNKNOWN_WORKING_MODEL: "
                    f"{working_model_id}",
                )

            writer_id = binding.get("repository_writer_id")
            if writer_valid and writer_id != repository_writer:
                _semantic_add(
                    errors,
                    f"SEMANTIC_UNKNOWN_REPOSITORY_WRITER: {writer_id}",
                )

        if (
            writer_valid
            and assignments.get("writer_authorization_reference")
            != active_authorization_id
        ):
            _semantic_add(
                errors,
                "SEMANTIC_WRITER_AUTHORIZATION_MISMATCH",
            )

    for transition_id, transition in transition_by_id.items():
        definition = transition_definitions.get(transition_id)
        if definition is None:
            _semantic_add(
                errors,
                f"SEMANTIC_UNKNOWN_TRANSITION: {transition_id}",
            )
            continue

        for field in (
            "from_state_ids",
            "to_state_id",
            "changed_dimensions",
            "preconditions",
        ):
            if transition.get(field) != definition.get(field):
                _semantic_add(
                    errors,
                    "SEMANTIC_TRANSITION_DEFINITION_MISMATCH: "
                    f"{transition_id}",
                )
                break

    represented_evidence: set[str] = set()
    for represented_id, record in represented_by_id.items():
        transition_id = record.get("transition_id")
        definition = transition_definitions.get(transition_id)
        if definition is None or transition_id not in transition_by_id:
            _semantic_add(
                errors,
                f"SEMANTIC_UNKNOWN_TRANSITION: {transition_id}",
            )
            continue

        source = record.get("from_state_id")
        destination = record.get("to_state_id")
        if source not in definition.get("from_state_ids", []):
            _semantic_add(
                errors,
                "SEMANTIC_ILLEGAL_TRANSITION_SOURCE: "
                f"{represented_id} {source}",
            )
        if destination != definition.get("to_state_id"):
            _semantic_add(
                errors,
                "SEMANTIC_ILLEGAL_TRANSITION_DESTINATION: "
                f"{represented_id} {destination}",
            )

        satisfied = record.get("satisfied_preconditions", [])
        if not isinstance(satisfied, list):
            satisfied = []
        if any(
            item not in satisfied
            for item in definition.get("preconditions", [])
        ):
            _semantic_add(
                errors,
                "SEMANTIC_TRANSITION_PRECONDITION_MISSING: "
                f"{represented_id}",
            )

        refs = record.get("evidence_refs", [])
        if isinstance(refs, list):
            represented_evidence.update(
                item for item in refs if isinstance(item, str)
            )

    required_evidence = (
        current_state.get("evidence", [])
        if current_state is not None
        else []
    )
    if isinstance(required_evidence, list):
        for reference in required_evidence:
            if reference not in represented_evidence:
                _semantic_add(
                    errors,
                    "SEMANTIC_REQUIRED_EVIDENCE_UNREPRESENTED: "
                    f"{reference}",
                )
            elif (
                reference not in evidence_by_id
                or evidence_by_id[reference].get("present") is not True
            ):
                _semantic_add(
                    errors,
                    f"SEMANTIC_REQUIRED_EVIDENCE_MISSING: {reference}",
                )

    for commit in commits:
        commit_id = commit.get("id", "<unknown>")
        authorization_id = commit.get("authorization_id")
        authorization = authorization_by_id.get(authorization_id)
        if authorization is None:
            _semantic_add(
                errors,
                "SEMANTIC_COMMIT_AUTHORIZATION_UNKNOWN: "
                f"{commit_id} {authorization_id}",
            )
            continue

        scope = {
            normalized
            for path in authorization.get("exact_file_scope", [])
            if (
                normalized := _semantic_repository_path(path)
            ) is not None
        }
        paths = commit.get("paths")
        if not isinstance(paths, list):
            _semantic_add(
                errors,
                f"SEMANTIC_COMMIT_PATHS_INVALID: {commit_id}",
            )
            continue

        for path in paths:
            normalized = _semantic_repository_path(path)
            if normalized is None or normalized not in scope:
                _semantic_add(
                    errors,
                    "SEMANTIC_COMMIT_PATH_OUTSIDE_SCOPE: "
                    f"{commit_id} {path}",
                )

    return errors


GIT_AUTHORIZATION_ENV = "FLOPPY_AUTHORIZATION_REFERENCE"
GIT_WRITER_ENV = "FLOPPY_REPOSITORY_WRITER"
GIT_EXPECTED_HEAD_ENV = "FLOPPY_EXPECTED_HEAD"
GIT_SCOPE_COMMIT_ENV = "FLOPPY_SCOPE_COMMIT"


def _git_integrity_run(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    """Run one direct, read-only Git command without persistent configuration."""

    return subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={root.as_posix()}",
            "-C",
            str(root),
            *arguments,
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def _git_integrity_lines(result: subprocess.CompletedProcess[str]) -> list[str]:
    return [
        line
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def _git_integrity_expected_writer(
    active: dict[str, Any],
    continuation: dict[str, Any],
    errors: list[str],
) -> str | None:
    values: list[Any] = [
        active.get("repository_writer"),
        continuation.get("repository_writer"),
    ]
    writers: set[str] = set()
    for value in values:
        if isinstance(value, list):
            if len(value) > 1:
                errors.append(
                    "GIT_INTEGRITY_MULTIPLE_REGISTERED_WRITERS: "
                    + ", ".join(str(item) for item in value)
                )
            elif len(value) == 1 and isinstance(value[0], str) and value[0]:
                writers.add(value[0])
        elif isinstance(value, str) and value:
            writers.add(value)

    if not writers:
        errors.append("GIT_INTEGRITY_REGISTERED_WRITER_MISSING")
        return None
    if len(writers) != 1:
        errors.append(
            "GIT_INTEGRITY_REGISTERED_WRITER_CONFLICT: "
            + ", ".join(sorted(writers))
        )
        return None
    return next(iter(writers))


def _git_integrity_manifest_at(
    root: Path,
    revision: str,
) -> dict[str, Any] | None:
    result = _git_integrity_run(
        root,
        "show",
        f"{revision}:.floppy/manifest.json",
    )
    if result.returncode != 0:
        return None
    try:
        value = json.loads(result.stdout)
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def _git_integrity_authorization_signature(
    active: dict[str, Any],
) -> dict[str, Any]:
    return {
        key: active.get(key)
        for key in (
            "authorization_id",
            "authorization_kind",
            "section",
            "exact_file_scope",
            "base_checkpoint",
            "branch",
            "worktree",
            "repository_writer",
            "writer_authorization_reference",
        )
    }


def _git_integrity_activation_paths(
    manifest: dict[str, Any],
    active: dict[str, Any],
) -> set[str] | None:
    section = active.get("section")
    if not isinstance(section, str) or not re.fullmatch(r"FS-[0-9]{2}", section):
        return None
    package_key = f"fs_{section[3:]}_work_package"
    package = manifest.get(package_key)
    if not isinstance(package, dict):
        return None
    draft_path = _semantic_repository_path(package.get("path"))
    if draft_path is None:
        return None
    return {
        ".floppy/floppies/Floppy-E-Current-Section.md",
        ".floppy/manifest.json",
        ".floppy/roadmap/roadmap.json",
        ".floppy/roadmap/roadmap.md",
        draft_path,
    }


def _git_integrity_activation_evidence_valid(
    manifest: dict[str, Any],
    active: dict[str, Any],
    expected_paths: set[str],
) -> bool:
    evidence = manifest.get("authorization_activation")
    if not isinstance(evidence, dict):
        return False
    if evidence.get("authorization_id") != active.get("authorization_id"):
        return False
    if evidence.get("operation") != "ACTIVATION_CONTROL_COMMIT":
        return False
    if evidence.get("implementation_scope_exercised") is not False:
        return False
    paths = evidence.get("exact_control_paths")
    if not isinstance(paths, list):
        return False
    normalized_paths = {
        normalized
        for item in paths
        if isinstance(item, str)
        and (normalized := _semantic_repository_path(item)) is not None
    }
    if len(normalized_paths) != len(paths) or normalized_paths != expected_paths:
        return False
    transitions = evidence.get("transition_sequence")
    expected = [
        {
            "id": "TR-003-AUTHORIZE-SECTION-IMPLEMENTATION",
            "pre_state": "LC-WORK-PACKAGE-ACCEPTED-NO-ACTIVE-WORK",
            "post_state": "LC-SECTION-AUTHORIZED-NOT-STARTED",
        },
        {
            "id": "TR-004-START-SECTION-IMPLEMENTATION",
            "pre_state": "LC-SECTION-AUTHORIZED-NOT-STARTED",
            "post_state": "LC-SECTION-IMPLEMENTATION-IN-PROGRESS",
        },
    ]
    if transitions != expected:
        return False
    if manifest.get("status") != "LC-SECTION-IMPLEMENTATION-IN-PROGRESS":
        return False
    authority = manifest.get("authority")
    if not isinstance(authority, dict):
        return False
    if authority.get("last_applied_transition") != (
        "TR-004-START-SECTION-IMPLEMENTATION"
    ):
        return False
    if authority.get("active_implementation_section") != active.get("section"):
        return False
    return True


def validate_authorization_git_integrity(
    root: Path,
    manifest: dict[str, Any],
    environ: dict[str, str] | None = None,
) -> list[str]:
    """Validate authorization, writer, operation kind, and exact Git scope."""

    environment = os.environ if environ is None else environ
    runtime_requested = any(
        environment.get(name)
        for name in (
            GIT_AUTHORIZATION_ENV,
            GIT_WRITER_ENV,
            GIT_EXPECTED_HEAD_ENV,
            GIT_SCOPE_COMMIT_ENV,
        )
    )
    active = manifest.get("active_work_authorization")
    if active is None and not runtime_requested:
        return []
    if not isinstance(active, dict):
        return ["GIT_INTEGRITY_ACTIVE_AUTHORIZATION_MISSING"]

    errors: list[str] = []
    continuation = manifest.get("continuation_point")
    if not isinstance(continuation, dict):
        continuation = {}

    expected_authorization = active.get("authorization_id")
    if not isinstance(expected_authorization, str) or not expected_authorization:
        errors.append("GIT_INTEGRITY_ACTIVE_AUTHORIZATION_INVALID")
        expected_authorization = None

    supplied_authorization = environment.get(GIT_AUTHORIZATION_ENV)
    if not supplied_authorization:
        errors.append("GIT_INTEGRITY_AUTHORIZATION_REFERENCE_MISSING")
    elif (
        expected_authorization is not None
        and supplied_authorization != expected_authorization
    ):
        errors.append(
            "GIT_INTEGRITY_AUTHORIZATION_REFERENCE_MISMATCH: "
            f"expected {expected_authorization} found {supplied_authorization}"
        )

    recorded_references = {
        value
        for value in (
            active.get("writer_authorization_reference"),
            continuation.get("active_work_authorization"),
            continuation.get("writer_authorization_reference"),
        )
        if isinstance(value, str) and value
    }
    if (
        expected_authorization is not None
        and recorded_references != {expected_authorization}
    ):
        if not recorded_references:
            errors.append("GIT_INTEGRITY_RECORDED_AUTHORIZATION_REFERENCE_MISSING")
        else:
            errors.append(
                "GIT_INTEGRITY_RECORDED_AUTHORIZATION_REFERENCE_CONFLICT: "
                + ", ".join(sorted(recorded_references))
            )

    expected_writer = _git_integrity_expected_writer(
        active,
        continuation,
        errors,
    )
    supplied_writer = environment.get(GIT_WRITER_ENV)
    if not supplied_writer:
        errors.append("GIT_INTEGRITY_EXECUTING_WRITER_MISSING")
    elif expected_writer is not None and supplied_writer != expected_writer:
        errors.append(
            "GIT_INTEGRITY_EXECUTING_WRITER_MISMATCH: "
            f"expected {expected_writer} found {supplied_writer}"
        )

    expected_branch = active.get("branch")
    if not isinstance(expected_branch, str) or not expected_branch:
        section = active.get("section")
        package_key = (
            f"fs_{section[3:]}_work_package"
            if isinstance(section, str) and re.fullmatch(r"FS-[0-9]{2}", section)
            else "fs_06_work_package"
        )
        package = manifest.get(package_key)
        expected_branch = package.get("branch") if isinstance(package, dict) else None
    if not isinstance(expected_branch, str) or not expected_branch:
        errors.append("GIT_INTEGRITY_EXPECTED_BRANCH_MISSING")
        expected_branch = None

    branch_result = _git_integrity_run(
        root,
        "symbolic-ref",
        "--quiet",
        "--short",
        "HEAD",
    )
    if branch_result.returncode == 1:
        if expected_branch is not None:
            errors.append(
                "GIT_INTEGRITY_DETACHED_HEAD: "
                f"expected branch {expected_branch}"
            )
    elif branch_result.returncode != 0:
        errors.append(
            "GIT_INTEGRITY_BRANCH_READ_FAILED: "
            + branch_result.stderr.strip()
        )
    else:
        actual_branch = branch_result.stdout.strip()
        if expected_branch is not None and actual_branch != expected_branch:
            errors.append(
                "GIT_INTEGRITY_BRANCH_MISMATCH: "
                f"expected {expected_branch} found {actual_branch}"
            )

    head_result = _git_integrity_run(root, "rev-parse", "HEAD")
    if head_result.returncode != 0:
        errors.append(
            "GIT_INTEGRITY_HEAD_READ_FAILED: "
            + head_result.stderr.strip()
        )
        actual_head = None
    else:
        actual_head = head_result.stdout.strip()

    expected_head = environment.get(GIT_EXPECTED_HEAD_ENV)
    if not expected_head:
        value = active.get("required_head")
        expected_head = value if isinstance(value, str) else None
    if not expected_head:
        errors.append("GIT_INTEGRITY_EXPECTED_HEAD_MISSING")
    elif actual_head is not None and actual_head != expected_head:
        errors.append(
            "GIT_INTEGRITY_HEAD_MISMATCH: "
            f"expected {expected_head} found {actual_head}"
        )

    scope = active.get("exact_file_scope")
    if not isinstance(scope, list):
        errors.append("GIT_INTEGRITY_AUTHORIZED_SCOPE_INVALID")
        implementation_paths: set[str] = set()
    else:
        implementation_paths = {
            normalized
            for item in scope
            if isinstance(item, str)
            and (normalized := _semantic_repository_path(item)) is not None
        }
        if len(implementation_paths) != len(scope):
            errors.append("GIT_INTEGRITY_AUTHORIZED_SCOPE_INVALID")

    scope_commit = environment.get(GIT_SCOPE_COMMIT_ENV)
    actual_paths: set[str] = set()
    parent_revision: str | None = None
    candidate_revision: str | None = None
    pending_candidate = not bool(scope_commit)

    if scope_commit:
        resolved = _git_integrity_run(
            root,
            "rev-parse",
            "--verify",
            f"{scope_commit}^{{commit}}",
        )
        if resolved.returncode != 0:
            errors.append(
                "GIT_INTEGRITY_SCOPE_COMMIT_INVALID: "
                f"{scope_commit}"
            )
        else:
            candidate_revision = resolved.stdout.strip()
            parent_revision = f"{candidate_revision}^"
            if actual_head is not None and candidate_revision != actual_head:
                errors.append(
                    "GIT_INTEGRITY_SCOPE_COMMIT_NOT_HEAD: "
                    f"{candidate_revision}"
                )
            changed = _git_integrity_run(
                root,
                "diff-tree",
                "--root",
                "--no-commit-id",
                "--name-only",
                "-r",
                candidate_revision,
                "--",
            )
            if changed.returncode != 0:
                errors.append(
                    "GIT_INTEGRITY_SCOPE_READ_FAILED: "
                    + changed.stderr.strip()
                )
            else:
                actual_paths = {
                    normalized
                    for item in _git_integrity_lines(changed)
                    if (normalized := _semantic_repository_path(item)) is not None
                }
    else:
        parent_revision = "HEAD"
        pending_commands = [
            ("diff", "--name-only", "--"),
            ("diff", "--cached", "--name-only", "--"),
            ("ls-files", "--others", "--exclude-standard"),
        ]
        for command in pending_commands:
            result = _git_integrity_run(root, *command)
            if result.returncode != 0:
                errors.append(
                    "GIT_INTEGRITY_SCOPE_READ_FAILED: "
                    + result.stderr.strip()
                )
                continue
            for item in _git_integrity_lines(result):
                normalized = _semantic_repository_path(item)
                if normalized is not None:
                    actual_paths.add(normalized)

    parent_manifest = (
        _git_integrity_manifest_at(root, parent_revision)
        if parent_revision is not None
        else None
    )
    parent_active = (
        parent_manifest.get("active_work_authorization")
        if isinstance(parent_manifest, dict)
        else None
    )

    if candidate_revision is not None:
        committed_manifest = _git_integrity_manifest_at(root, candidate_revision)
        if committed_manifest is not None and committed_manifest != manifest:
            errors.append("GIT_INTEGRITY_CANDIDATE_MANIFEST_MISMATCH")

    operation = "LEGACY_IMPLEMENTATION"
    expected_paths = set(implementation_paths)
    if parent_active is None and isinstance(parent_manifest, dict):
        operation = "ACTIVATION_CONTROL_COMMIT"
        activation_paths = _git_integrity_activation_paths(manifest, active)
        if activation_paths is None:
            errors.append("GIT_INTEGRITY_ACTIVATION_CONTROL_PATHS_INVALID")
            expected_paths = set()
        else:
            expected_paths = activation_paths
            if not _git_integrity_activation_evidence_valid(
                manifest,
                active,
                activation_paths,
            ):
                errors.append("GIT_INTEGRITY_ACTIVATION_EVIDENCE_INVALID")
        if actual_paths & implementation_paths:
            errors.append(
                "GIT_INTEGRITY_ACTIVATION_CHANGED_IMPLEMENTATION_PATHS: "
                + ", ".join(sorted(actual_paths & implementation_paths))
            )
    elif isinstance(parent_active, dict):
        operation = "AUTHORIZED_IMPLEMENTATION_COMMIT"
        parent_signature = _git_integrity_authorization_signature(parent_active)
        candidate_signature = _git_integrity_authorization_signature(active)
        changed_fields = sorted(
            key
            for key in parent_signature
            if parent_signature[key] != candidate_signature[key]
        )
        if changed_fields:
            errors.append(
                "GIT_INTEGRITY_AUTHORIZATION_MUTATED: "
                + ", ".join(changed_fields)
            )
        parent_activation = parent_manifest.get("authorization_activation")
        candidate_activation = manifest.get("authorization_activation")
        if parent_activation != candidate_activation:
            errors.append("GIT_INTEGRITY_ACTIVATION_EVIDENCE_MUTATED")

    status_result = _git_integrity_run(
        root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if status_result.returncode != 0:
        errors.append(
            "GIT_INTEGRITY_WORKTREE_READ_FAILED: "
            + status_result.stderr.strip()
        )
    else:
        staged: list[str] = []
        tracked: list[str] = []
        untracked: list[str] = []
        for line in status_result.stdout.splitlines():
            if not line:
                continue
            code = line[:2]
            path = line[3:] if len(line) > 3 else "<unknown>"
            if code == "??":
                untracked.append(path)
                continue
            if code[0] != " ":
                staged.append(path)
            if code[1] != " ":
                tracked.append(path)
        if untracked:
            errors.append(
                "GIT_INTEGRITY_UNTRACKED_PATHS: "
                + ", ".join(sorted(untracked))
            )
        if not pending_candidate:
            if staged:
                errors.append(
                    "GIT_INTEGRITY_STAGED_CHANGES: "
                    + ", ".join(sorted(staged))
                )
            if tracked:
                errors.append(
                    "GIT_INTEGRITY_TRACKED_CHANGES: "
                    + ", ".join(sorted(tracked))
                )

    extra = sorted(actual_paths - expected_paths)
    missing = sorted(expected_paths - actual_paths)
    if extra:
        errors.append(
            "GIT_INTEGRITY_UNAUTHORIZED_PATHS: " + ", ".join(extra)
        )
    if missing:
        errors.append(
            "GIT_INTEGRITY_REQUIRED_PATHS_MISSING: " + ", ".join(missing)
        )

    return errors

def _closeout_reference_present(record: dict[str, Any], *fields: str) -> bool:
    for field in fields:
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            return True
        if isinstance(value, dict) and value:
            return True
        if isinstance(value, list) and value:
            return True
    return False


def _closeout_section_number(section: Any) -> int | None:
    if not isinstance(section, str) or not section.startswith("FS-"):
        return None
    try:
        return int(section[3:])
    except ValueError:
        return None


def _validate_ordinary_closeout_completeness(
    manifest: dict[str, Any],
    root: Path,
) -> list[str]:
    """Validate the currently represented applied section closeout."""

    if not isinstance(manifest, dict):
        return ["CLOSEOUT_MANIFEST_INVALID"]

    proposal = manifest.get("closeout_proposal")
    application = manifest.get("closeout_application")
    closed_state = manifest.get("status") == (
        "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE"
    )
    if not closed_state:
        return []

    errors: list[str] = []
    section = (
        application.get("section")
        if isinstance(application, dict)
        else None
    )
    if not isinstance(section, str) and isinstance(proposal, dict):
        section = proposal.get("section")
    number = _closeout_section_number(section)
    if number is None:
        return ["CLOSEOUT_SECTION_INVALID"]

    record_key = f"fs_{number:02d}_work_package"
    record = manifest.get(record_key)
    if not isinstance(record, dict) or record.get("section") != section:
        record = next(
            (
                item
                for item in reversed(
                    manifest.get("historical_work_authorizations", [])
                )
                if isinstance(item, dict) and item.get("section") == section
            ),
            None,
        )
    if not isinstance(record, dict):
        return [f"CLOSEOUT_SECTION_RECORD_MISSING: {section}"]

    implementation_complete = (
        record.get("implementation_complete") is True
        or record.get("implementation_status") == "COMPLETE"
        or record.get("implementation_state") == "COMPLETE"
    )
    if not implementation_complete:
        errors.append(f"CLOSEOUT_IMPLEMENTATION_INCOMPLETE: {section}")

    verification_complete = (
        record.get("verification_complete") is True
        or record.get("verification_status") == "COMPLETE"
        or record.get("verification_state") == "COMPLETE"
    )
    if not verification_complete:
        errors.append(f"CLOSEOUT_VERIFICATION_INCOMPLETE: {section}")

    if record.get("administrator_acceptance") != "ACCEPTED":
        errors.append(
            f"CLOSEOUT_ADMINISTRATOR_ACCEPTANCE_MISSING: {section}"
        )

    if not _closeout_reference_present(
        record,
        "implementation_checkpoint",
        "implementation_completion_checkpoint",
        "accepted_implementation_checkpoint",
        "reusable_product_commit",
        "product_commit",
        "completion_evidence",
    ):
        errors.append(f"CLOSEOUT_IMPLEMENTATION_EVIDENCE_MISSING: {section}")

    if not _closeout_reference_present(
        record,
        "verification_evidence",
        "completion_evidence",
        "completion_record_checkpoint",
    ):
        errors.append(f"CLOSEOUT_VERIFICATION_EVIDENCE_MISSING: {section}")

    proposal_valid = (
        isinstance(proposal, dict)
        and proposal.get("section") == section
        and proposal.get("transition")
        == "TR-008-PROPOSE-SECTION-CLOSEOUT"
        and proposal.get("status") in {"APPROVED_AND_APPLIED", "APPLIED"}
        and isinstance(proposal.get("proposal_commit_checkpoint"), str)
        and bool(proposal.get("proposal_commit_checkpoint"))
        and isinstance(proposal.get("record"), str)
        and bool(proposal.get("record"))
        and (root / proposal["record"]).is_file()
    )
    if not proposal_valid:
        errors.append(f"CLOSEOUT_PROPOSAL_INCOMPLETE: {section}")

    application_valid = (
        isinstance(application, dict)
        and application.get("section") == section
        and application.get("status") == "APPLIED"
        and isinstance(application.get("application_commit_checkpoint"), str)
        and bool(application.get("application_commit_checkpoint"))
        and isinstance(application.get("record"), str)
        and bool(application.get("record"))
        and (root / application["record"]).is_file()
    )
    if not application_valid:
        errors.append(f"CLOSEOUT_APPLICATION_INCOMPLETE: {section}")

    proposal_checkpoint = (
        proposal.get("proposal_commit_checkpoint")
        if isinstance(proposal, dict)
        else None
    )
    application_checkpoint = (
        application.get("application_commit_checkpoint")
        if isinstance(application, dict)
        else None
    )
    transition_valid = (
        isinstance(application, dict)
        and application.get("transition")
        == "TR-009-APPLY-SECTION-CLOSEOUT"
        and application.get("resulting_lifecycle_state")
        == "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE"
        and application.get("approved_proposal_checkpoint")
        == proposal_checkpoint
        and proposal_checkpoint != application_checkpoint
        and record.get("section_closeout") == "APPLIED"
        and record.get("closeout_applied") is True
        and record.get("closeout_application_transition")
        == "TR-009-APPLY-SECTION-CLOSEOUT"
    )
    if not transition_valid:
        errors.append(f"CLOSEOUT_APPLICATION_TRANSITION_INVALID: {section}")

    next_number = number + 1
    next_section = f"FS-{next_number:02d}"
    next_key = f"fs_{next_number:02d}"
    records = manifest.get("records")
    if not isinstance(records, dict):
        records = {}
    draft_path = None
    for source in (application, proposal, record):
        if isinstance(source, dict):
            candidate = source.get(f"{next_key}_draft_path")
            if isinstance(candidate, str) and candidate:
                draft_path = candidate
                break
    if draft_path is None:
        candidate = records.get(f"{next_key}_work_package_draft")
        if isinstance(candidate, str) and candidate:
            draft_path = candidate
    if draft_path is None or not (root / draft_path).is_file():
        errors.append(f"CLOSEOUT_NEXT_DRAFT_MISSING: {next_section}")

    next_record = manifest.get(f"{next_key}_work_package")
    if not isinstance(next_record, dict):
        next_record = {}

    if next_record.get("active") is not False:
        errors.append(f"CLOSEOUT_NEXT_SECTION_ACTIVE: {next_section}")
    if next_record.get("accepted") is not False:
        errors.append(f"CLOSEOUT_NEXT_SECTION_ACCEPTED: {next_section}")
    next_authorized = any(
        (
            next_record.get("activation_authorized") is True,
            next_record.get("implementation_authorized") is True,
            next_record.get("authorization_id") not in {None, ""},
            next_record.get("status") not in {
                "DRAFT_NOT_AUTHORIZED",
                "NOT AUTHORIZED",
            },
            isinstance(application, dict)
            and application.get(next_key) != "NOT AUTHORIZED",
        )
    )
    if next_authorized:
        errors.append(f"CLOSEOUT_NEXT_SECTION_AUTHORIZED: {next_section}")

    continuation = manifest.get("continuation_point")
    if not isinstance(continuation, dict):
        continuation = {}
    authority = manifest.get("authority")
    if not isinstance(authority, dict):
        authority = {}
    active_authorization_remains = any(
        (
            manifest.get("active_work_authorization") is not None,
            continuation.get("active_work_authorization") is not None,
            authority.get("active_implementation_section") is not None,
            authority.get("current_authorized_section") is not None,
            isinstance(application, dict)
            and application.get("active_implementation_section") is not None,
            isinstance(application, dict)
            and application.get("current_authorized_section") is not None,
        )
    )
    if active_authorization_remains:
        errors.append(f"CLOSEOUT_ACTIVE_AUTHORIZATION_REMAINS: {section}")

    writer_remains = any(
        (
            record.get("repository_writer") is not None,
            continuation.get("repository_writer") is not None,
            next_record.get("repository_writer") is not None,
            isinstance(application, dict)
            and application.get("repository_writer") is not None,
        )
    )
    if writer_remains:
        errors.append(f"CLOSEOUT_REPOSITORY_WRITER_REMAINS: {section}")

    return errors

def validate_source(root: Path, errors: list[str]) -> None:
    manifest = validate_json(root / "system-manifest.json", errors)
    version = (root / "VERSION").read_text(encoding="utf-8").strip()

    if manifest and manifest.get("system_version") != version:
        errors.append("VERSION and system-manifest.json disagree")

    if not manifest:
        return

    if manifest.get("entrypoints", {}).get("about") != "ABOUT.md":
        errors.append("system manifest does not register canonical ABOUT.md")

    architecture = manifest.get("architecture", {})
    if architecture.get("name") != "BCE \u2014 Bootable Context Environment":
        errors.append("system manifest does not identify the BCE architecture")
    if architecture.get("about_path") != "ABOUT.md":
        errors.append("system manifest BCE about path is invalid")

    orchestrator = manifest.get("orchestrator", {})
    orchestrator_path = orchestrator.get("canonical_path")
    if not orchestrator_path or not (root / orchestrator_path).is_file():
        errors.append("system manifest orchestrator path is missing")
    elif orchestrator.get("sha256") != sha256(root / orchestrator_path):
        errors.append("canonical Floppy Z digest does not match system manifest")

    builder = manifest.get("initial_project_roadmap_builder", {})
    builder_path = builder.get("canonical_path")
    if not builder_path or not (root / builder_path).is_file():
        errors.append("system manifest Floppy 1E path is missing")
    elif builder.get("sha256") != sha256(root / builder_path):
        errors.append("canonical Floppy 1E digest does not match system manifest")
    if builder.get("implementation_authority") is not False:
        errors.append("Floppy 1E must not grant implementation authority")
    if builder.get("mutable_during_project_work") is not False:
        errors.append("Floppy 1E must be immutable during project work")

    validate_lifecycle_artifacts(root, manifest, errors)
    validate_normative_bce_schemas(root, manifest, errors)
    validate_verification_only_lifecycle_extension(root, manifest, errors)

    control_path = root / ".floppy/manifest.json"
    if control_path.is_file():
        control_manifest = validate_json(control_path, errors)
        if control_manifest is not None:
            errors.extend(
                validate_authorization_git_integrity(
                    root,
                    control_manifest,
                )
            )


def validate_project(root: Path, errors: list[str]) -> None:
    manifest = validate_json(root / ".floppy/manifest.json", errors)
    roadmap = validate_json(root / ".floppy/roadmap/roadmap.json", errors)

    if manifest:
        for relative in manifest.get("required_read_order", []):
            if not (root / relative).is_file():
                errors.append(f"manifest read-order file missing: {relative}")

        system = manifest.get("system", {})
        if system.get("source_read_only_during_project_work") is not True:
            errors.append("project manifest does not enforce source read-only boundary")
        if system.get("about") != "ABOUT.md":
            errors.append(
                "project manifest does not preserve canonical ABOUT provenance"
            )
        if system.get("architecture") != "BCE \u2014 Bootable Context Environment":
            errors.append("project manifest does not identify the BCE architecture")

        floppies = manifest.get("floppies", {})
        if set(floppies) != {"A", "B", "C", "D", "E"}:
            errors.append("project manifest must map project Floppies A through E only")

        onboarding = manifest.get("onboarding", {})
        if onboarding.get("controller") != "onboarding/Floppy_1E.md":
            errors.append("project manifest does not reference canonical Floppy 1E")
        if onboarding.get("implementation_authority") is not False:
            errors.append(
                "project manifest incorrectly grants Floppy 1E implementation authority"
            )

        roadmap_paths = manifest.get("roadmap", {})
        for key in ("machine_readable", "user_readable"):
            relative = roadmap_paths.get(key)
            if not relative or not (root / relative).is_file():
                errors.append(f"project roadmap path missing or invalid: {key}")

        errors.extend(validate_closeout_completeness(manifest, root))

    if roadmap:
        if roadmap.get("current_authorized_section") is not None:
            errors.append(
                "new project roadmap must not authorize a section during initialization"
            )

        controller = roadmap.get("source_controller", {})
        if controller.get("mutable_in_project") is not False:
            errors.append(
                "project roadmap must preserve canonical Floppy 1E as read-only"
            )


def main() -> int:
    args = parse_args()
    root = args.path.expanduser().resolve()
    errors: list[str] = []
    required = SOURCE_REQUIRED if args.mode == "source" else PROJECT_REQUIRED

    for relative in required:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    if not errors:
        if args.mode == "source":
            validate_source(root, errors)
        else:
            validate_project(root, errors)

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"VALIDATION PASSED: {args.mode} at {root}")
    return 0


# BEGIN CTRL-02 VERIFICATION-ONLY CLOSEOUT CORRECTION

_VERIFICATION_ONLY_CLOSEOUT_TYPE = "VERIFICATION_ONLY_NO_REUSABLE_PRODUCT_CHANGE"
_VERIFICATION_ONLY_PROPOSAL_STATE = "LC-VERIFICATION-ONLY-SECTION-ACCEPTED-CLOSEOUT-PROPOSED"
_VERIFICATION_ONLY_FINAL_STATE = "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE"
_VERIFICATION_ONLY_COMPLETION_TRANSITION = "TR-017-RECORD-VERIFICATION-ONLY-COMPLETE"
_VERIFICATION_ONLY_PROPOSAL_TRANSITION = "TR-019-PROPOSE-VERIFICATION-ONLY-SECTION-CLOSEOUT"
_VERIFICATION_ONLY_APPLICATION_TRANSITION = "TR-020-APPLY-VERIFICATION-ONLY-SECTION-CLOSEOUT"


def _verification_only_error(errors, code, section):
    diagnostic = f"{code}: {section}"
    if diagnostic not in errors:
        errors.append(diagnostic)


def _verification_only_closeout_context(manifest):
    proposal = manifest.get("closeout_proposal")
    application = manifest.get("closeout_application")
    section = None
    for candidate in (application, proposal):
        if isinstance(candidate, dict):
            value = candidate.get("section")
            if isinstance(value, str) and value:
                section = value
                break

    candidates = []
    for key, value in manifest.items():
        if not (
            isinstance(key, str)
            and key.startswith("fs_")
            and key.endswith("_work_package")
            and isinstance(value, dict)
            and value.get("work_package_type") == _VERIFICATION_ONLY_CLOSEOUT_TYPE
        ):
            continue
        record_section = value.get("section", value.get("id"))
        if not isinstance(record_section, str):
            digits = key[3:5]
            record_section = f"FS-{digits}" if digits.isdigit() else None
        if isinstance(record_section, str):
            candidates.append((record_section, value))

    if section is not None:
        exact = [item for item in candidates if item[0] == section]
        return exact[0] if len(exact) == 1 else None
    return candidates[0] if len(candidates) == 1 else None


def _verification_only_no_change_evidence_valid(record):
    evidence = record.get("verification_evidence")
    if not isinstance(evidence, dict):
        return False
    if evidence.get("result") != "PASSED":
        return False
    if evidence.get("recorded_transition") != _VERIFICATION_ONLY_COMPLETION_TRANSITION:
        return False
    tests = evidence.get("complete_repository_tests")
    if not (
        isinstance(tests, dict)
        and tests.get("status") == "PASSED"
        and isinstance(tests.get("test_count"), int)
        and tests.get("test_count") > 0
    ):
        return False
    if evidence.get("source_validator") != "PASSED":
        return False
    if evidence.get("floppyctl_source_validation") != "PASSED":
        return False
    tracked_json = evidence.get("tracked_json")
    if not (
        isinstance(tracked_json, dict)
        and tracked_json.get("status") == "PASSED"
        and isinstance(tracked_json.get("file_count"), int)
        and tracked_json.get("file_count") > 0
    ):
        return False
    findings = evidence.get("accepted_no_change_findings")
    if not isinstance(findings, dict):
        return False
    required = {
        "work_package_type": _VERIFICATION_ONLY_CLOSEOUT_TYPE,
        "implementation_state": "NOT_REQUIRED",
        "qualifying_real_migration_paths": 0,
        "qualifying_real_source_format_fixtures": [],
        "reusable_product_paths": [],
        "reusable_product_path_count": 0,
        "reusable_product_commits": [],
        "reusable_product_commit_count": 0,
        "product_commit": None,
        "real_project_modification": "NOT_PERFORMED",
        "active_authorization": None,
        "repository_writer": None,
        "writer_authorization_reference": None,
    }
    return all(findings.get(key) == value for key, value in required.items())


def _verification_only_product_scope_empty(record):
    for value in (
        record.get("reusable_product_paths"),
        record.get("exact_reusable_product_paths"),
    ):
        if value not in (None, []):
            return False
    for value in (
        record.get("reusable_product_commits"),
        record.get("reusable_product_commit"),
    ):
        if value not in (None, []):
            return False
    if record.get("reusable_product_path_count", 0) != 0:
        return False
    if record.get("reusable_product_commit_count", 0) != 0:
        return False
    return record.get("product_commit") is None


def _verification_only_authority_empty(manifest, record):
    authority = manifest.get("authority")
    authority = authority if isinstance(authority, dict) else {}
    fields = (
        "active_work_authorization",
        "active_control_work_authorization",
        "active_implementation_authorization",
        "active_migration_authorization",
        "active_implementation_section",
        "current_authorized_section",
        "authorization_id",
    )
    return all(container.get(field) is None for container in (manifest, authority, record) for field in fields)


def _verification_only_writer_empty(manifest, record):
    authority = manifest.get("authority")
    authority = authority if isinstance(authority, dict) else {}
    return all(
        container.get("repository_writer") is None
        and container.get("writer_authorization_reference") is None
        for container in (manifest, authority, record)
    )


def _verification_only_next_section_valid(manifest, root, application):
    section = application.get("section")
    if not isinstance(section, str) or not section.startswith("FS-"):
        return False, "UNKNOWN"
    try:
        next_section = f"FS-{int(section[3:]) + 1:02d}"
    except ValueError:
        return False, "UNKNOWN"
    next_key = f"fs_{next_section[3:]}_work_package"
    next_record = manifest.get(next_key)
    if not isinstance(next_record, dict):
        return False, next_section
    draft_path = application.get(f"fs_{next_section[3:]}_draft_path")
    if not isinstance(draft_path, str) or not draft_path or not (root / draft_path).is_file():
        return False, next_section

    # TR-020 establishes the existence and identity of the next-section draft
    # and work-package record.  It does not permanently freeze that section in
    # its application-time inactive state.  Later current-state progression is
    # validated by the lifecycle and authorization validators.
    for identity_field in ("section", "id"):
        value = next_record.get(identity_field)
        if value is not None and value != next_section:
            return False, next_section

    required_flags = ("accepted", "active", "implementation_authorized")
    if any(not isinstance(next_record.get(field), bool) for field in required_flags):
        return False, next_section

    authorization_id = next_record.get("authorization_id")
    repository_writer = next_record.get("repository_writer")
    writer_reference = next_record.get("writer_authorization_reference")
    for value in (authorization_id, repository_writer, writer_reference):
        if value is not None and (not isinstance(value, str) or not value.strip()):
            return False, next_section

    accepted = next_record["accepted"]
    active = next_record["active"]
    authorized = next_record["implementation_authorized"]
    if active and not authorized:
        return False, next_section
    if authorized and not accepted:
        return False, next_section
    if authorized:
        if authorization_id is None or repository_writer is None:
            return False, next_section
        if writer_reference is not None and writer_reference != authorization_id:
            return False, next_section
    elif any(value is not None for value in (authorization_id, repository_writer, writer_reference)):
        return False, next_section
    return True, next_section


def _validate_verification_only_closeout_completeness(manifest, root, section, record):
    errors = []
    state = manifest.get("status")
    proposal = manifest.get("closeout_proposal")
    application = manifest.get("closeout_application")

    implementation = record.get("implementation_state", record.get("implementation"))
    if implementation != "NOT_REQUIRED":
        _verification_only_error(errors, "CLOSEOUT_VERIFICATION_ONLY_IMPLEMENTATION_INVALID", section)
    if record.get("implementation_complete") is True:
        _verification_only_error(errors, "CLOSEOUT_VERIFICATION_ONLY_IMPLEMENTATION_COMPLETE_FORBIDDEN", section)
    if any(record.get(field) is not None for field in (
        "implementation_checkpoint",
        "implementation_evidence",
        "implementation_completion_evidence",
    )):
        _verification_only_error(errors, "CLOSEOUT_VERIFICATION_ONLY_IMPLEMENTATION_EVIDENCE_FORBIDDEN", section)

    verification = record.get("verification_state", record.get("verification"))
    if verification != "COMPLETE":
        _verification_only_error(errors, "CLOSEOUT_VERIFICATION_INCOMPLETE", section)
    if not _verification_only_no_change_evidence_valid(record):
        _verification_only_error(errors, "CLOSEOUT_VERIFICATION_ONLY_EVIDENCE_MISSING", section)
    if record.get("administrator_acceptance") != "ACCEPTED":
        _verification_only_error(errors, "CLOSEOUT_ADMINISTRATOR_ACCEPTANCE_MISSING", section)
    if not _verification_only_product_scope_empty(record):
        _verification_only_error(errors, "CLOSEOUT_VERIFICATION_ONLY_PRODUCT_SCOPE_INVALID", section)
    if not _verification_only_authority_empty(manifest, record):
        _verification_only_error(errors, "CLOSEOUT_ACTIVE_AUTHORIZATION_REMAINS", section)
    if not _verification_only_writer_empty(manifest, record):
        _verification_only_error(errors, "CLOSEOUT_REPOSITORY_WRITER_REMAINS", section)

    if not isinstance(proposal, dict):
        _verification_only_error(errors, "CLOSEOUT_PROPOSAL_INCOMPLETE", section)
    else:
        if proposal.get("section") != section:
            _verification_only_error(errors, "CLOSEOUT_PROPOSAL_INCOMPLETE", section)
        if proposal.get("transition") != _VERIFICATION_ONLY_PROPOSAL_TRANSITION:
            _verification_only_error(errors, "CLOSEOUT_PROPOSAL_TRANSITION_INVALID", section)
        record_path = proposal.get("record")
        if not isinstance(record_path, str) or not (root / record_path).is_file():
            _verification_only_error(errors, "CLOSEOUT_PROPOSAL_INCOMPLETE", section)

    applied = (
        state == _VERIFICATION_ONLY_FINAL_STATE
        or record.get("closeout") == "APPLIED"
        or record.get("section_closeout") == "APPLIED"
        or record.get("closeout_applied") is True
    )
    if applied:
        if not isinstance(application, dict):
            _verification_only_error(errors, "CLOSEOUT_APPLICATION_TRANSITION_INVALID", section)
        else:
            if application.get("section") != section:
                _verification_only_error(errors, "CLOSEOUT_APPLICATION_TRANSITION_INVALID", section)
            if application.get("transition") != _VERIFICATION_ONLY_APPLICATION_TRANSITION:
                _verification_only_error(errors, "CLOSEOUT_APPLICATION_TRANSITION_INVALID", section)
            if application.get("status") != "APPLIED":
                _verification_only_error(errors, "CLOSEOUT_APPLICATION_TRANSITION_INVALID", section)
            next_valid, next_section = _verification_only_next_section_valid(manifest, root, application)
            if not next_valid:
                _verification_only_error(errors, "CLOSEOUT_NEXT_DRAFT_OR_STATE_INVALID", next_section)
    else:
        if state != _VERIFICATION_ONLY_PROPOSAL_STATE:
            _verification_only_error(errors, "CLOSEOUT_VERIFICATION_ONLY_LIFECYCLE_INVALID", section)
        if isinstance(application, dict) and application.get("status") == "APPLIED":
            _verification_only_error(errors, "CLOSEOUT_APPLICATION_TRANSITION_INVALID", section)
    return errors


def validate_closeout_completeness(manifest, root):
    context = _verification_only_closeout_context(manifest)
    if context is None:
        return _validate_ordinary_closeout_completeness(manifest, root)
    section, record = context
    return _validate_verification_only_closeout_completeness(manifest, root, section, record)

# END CTRL-02 VERIFICATION-ONLY CLOSEOUT CORRECTION

if __name__ == "__main__":
    raise SystemExit(main())
