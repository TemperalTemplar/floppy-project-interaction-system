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
    "project-seed/.floppy/lifecycle-state.json",
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

POST_PROVISIONING_EXACT_DIMENSION_TRANSITIONS = frozenset(
    {
        "TR-002-ACCEPT-WORK-PACKAGE",
        "TR-016-ACCEPT-VERIFICATION-ONLY-WORK-PACKAGE",
    }
)

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
    state_records = {
        state.get("id"): state
        for state in states
        if isinstance(states, list)
        and isinstance(state, dict)
        and isinstance(state.get("id"), str)
    }

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
                elif transition_id in POST_PROVISIONING_EXACT_DIMENSION_TRANSITIONS:
                    target = state_records.get(to_state_id)
                    sources = [state_records.get(item) for item in from_state_ids]
                    if not isinstance(target, dict) or any(
                        not isinstance(item, dict) for item in sources
                    ):
                        errors.append(
                            f"transition {transition_id} exact changed dimensions "
                            "cannot be resolved"
                        )
                    else:
                        actual_changed_dimensions: set[str] = set()
                        target_dimensions = target.get("dimensions")
                        if not isinstance(target_dimensions, dict):
                            errors.append(
                                f"transition {transition_id} exact target dimensions "
                                "are invalid"
                            )
                        else:
                            for source in sources:
                                source_dimensions = source.get("dimensions")
                                if not isinstance(source_dimensions, dict):
                                    errors.append(
                                        f"transition {transition_id} exact source "
                                        "dimensions are invalid"
                                    )
                                    continue
                                actual_changed_dimensions.update(
                                    dimension
                                    for dimension in REQUIRED_DIMENSIONS
                                    if source_dimensions.get(dimension)
                                    != target_dimensions.get(dimension)
                                )
                                if source.get("active_implementation_section") != (
                                    target.get("active_implementation_section")
                                ):
                                    actual_changed_dimensions.add(
                                        "active_implementation_section"
                                    )
                            if set(changed_dimensions) != actual_changed_dimensions:
                                errors.append(
                                    "LIFECYCLE_CHANGED_DIMENSIONS_MISMATCH: "
                                    f"{transition_id} declared "
                                    f"{', '.join(sorted(set(changed_dimensions)))} "
                                    "actual "
                                    f"{', '.join(sorted(actual_changed_dimensions))}"
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
GIT_CONTROL_OPERATION_ENV = "FLOPPY_CONTROL_OPERATION"
GIT_CONTROL_SCOPE_ENV = "FLOPPY_CONTROL_SCOPE"
GIT_CONTROL_BRANCH_ENV = "FLOPPY_CONTROL_BRANCH"

PRE_FS12_BOUNDED_CONTROL_CORRECTION_PC2_SCOPE = frozenset(
    {
        "specs/lifecycle-transition-table.json",
        "tools/validate_floppy.py",
        "tests/test_lifecycle_specification.py",
        "tests/test_authorization_git_integrity.py",
        "system-manifest.json",
    }
)


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
        ".floppy/lifecycle-state.json",
        ".floppy/manifest.json",
        ".floppy/orchestrator-registry.json",
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



GIT_OPERATION_EVIDENCE_KEY = "git_integrity_operation"

_GIT_WORK_PACKAGE_ACCEPTANCE_TRANSITIONS = {
    (
        "TR-002-ACCEPT-WORK-PACKAGE",
        "LC-ROADMAP-ACCEPTED-NO-ACTIVE-WORK",
        "LC-WORK-PACKAGE-ACCEPTED-NO-ACTIVE-WORK",
    ),
    (
        "TR-002-ACCEPT-WORK-PACKAGE",
        "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE",
        "LC-WORK-PACKAGE-ACCEPTED-NO-ACTIVE-WORK",
    ),
    (
        "TR-016-ACCEPT-VERIFICATION-ONLY-WORK-PACKAGE",
        "LC-ROADMAP-ACCEPTED-NO-ACTIVE-WORK",
        "LC-VERIFICATION-ONLY-WORK-PACKAGE-ACCEPTED-PENDING",
    ),
    (
        "TR-016-ACCEPT-VERIFICATION-ONLY-WORK-PACKAGE",
        "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE",
        "LC-VERIFICATION-ONLY-WORK-PACKAGE-ACCEPTED-PENDING",
    ),
}

_GIT_CONTROL_TRANSITIONS = {
    "ACTIVATION_CONTROL_COMMIT": [
        (
            "TR-003-AUTHORIZE-SECTION-IMPLEMENTATION",
            "LC-WORK-PACKAGE-ACCEPTED-NO-ACTIVE-WORK",
            "LC-SECTION-AUTHORIZED-NOT-STARTED",
        ),
        (
            "TR-004-START-SECTION-IMPLEMENTATION",
            "LC-SECTION-AUTHORIZED-NOT-STARTED",
            "LC-SECTION-IMPLEMENTATION-IN-PROGRESS",
        ),
    ],
    "COMPLETION_VERIFICATION_CONTROL": [
        (
            "TR-005-RECORD-IMPLEMENTATION-COMPLETE",
            "LC-SECTION-IMPLEMENTATION-IN-PROGRESS",
            "LC-IMPLEMENTATION-COMPLETE-VERIFICATION-PENDING",
        ),
        (
            "TR-006-RECORD-VERIFICATION-COMPLETE",
            "LC-IMPLEMENTATION-COMPLETE-VERIFICATION-PENDING",
            "LC-VERIFICATION-COMPLETE-ACCEPTANCE-PENDING",
        ),
    ],
    "ADMINISTRATOR_ACCEPTANCE_CONTROL": [
        (
            "TR-007-ACCEPT-SECTION",
            "LC-VERIFICATION-COMPLETE-ACCEPTANCE-PENDING",
            "LC-SECTION-ACCEPTED-CLOSEOUT-NOT-PROPOSED",
        )
    ],
    "CLOSEOUT_PROPOSAL_CONTROL": [
        (
            "TR-008-PROPOSE-SECTION-CLOSEOUT",
            "LC-SECTION-ACCEPTED-CLOSEOUT-NOT-PROPOSED",
            "LC-SECTION-ACCEPTED-CLOSEOUT-PROPOSED",
        )
    ],
    "CLOSEOUT_APPLICATION_CONTROL": [
        (
            "TR-009-APPLY-SECTION-CLOSEOUT",
            "LC-SECTION-ACCEPTED-CLOSEOUT-PROPOSED",
            "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE",
        )
    ],
}

_GIT_STATE_PRESERVING_OPERATIONS = {
    "STATE_PRESERVING_AUTHORITY_HANDOFF",
    "ROOT_CONTROL_IMPLEMENTATION",
}

_GIT_NO_AUTHORITY_OPERATIONS = {
    "WORK_PACKAGE_ACCEPTANCE_CONTROL",
    "CLOSEOUT_PROPOSAL_CONTROL",
    "CLOSEOUT_APPLICATION_CONTROL",
}


def _git_integrity_section_record(
    manifest: dict[str, Any] | None,
    section: str,
) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        return {}
    key = f"fs_{section[3:]}_work_package"
    value = manifest.get(key)
    return value if isinstance(value, dict) else {}


def _git_integrity_section_from_context(
    manifest: dict[str, Any],
    parent_manifest: dict[str, Any] | None,
    active: dict[str, Any] | None,
    parent_active: dict[str, Any] | None,
) -> str | None:
    evidence = manifest.get(GIT_OPERATION_EVIDENCE_KEY)
    values = [
        evidence.get("section") if isinstance(evidence, dict) else None,
        active.get("section") if isinstance(active, dict) else None,
        parent_active.get("section") if isinstance(parent_active, dict) else None,
    ]
    for source in (manifest, parent_manifest):
        if not isinstance(source, dict):
            continue
        for key in ("closeout_application", "closeout_proposal"):
            record = source.get(key)
            values.append(record.get("section") if isinstance(record, dict) else None)
    for value in values:
        if isinstance(value, str) and re.fullmatch(r"FS-[0-9]{2}", value):
            return value
    return None


def _git_integrity_draft_path(
    manifest: dict[str, Any],
    parent_manifest: dict[str, Any] | None,
    section: str,
) -> str | None:
    for source in (manifest, parent_manifest):
        record = _git_integrity_section_record(source, section)
        candidate = _semantic_repository_path(record.get("path"))
        if candidate is not None:
            return candidate
    return f".floppy/templates/Floppy-E-{section}.draft.md"


def _git_integrity_closeout_path(
    manifest: dict[str, Any],
    parent_manifest: dict[str, Any] | None,
    section: str,
) -> str:
    for source in (manifest, parent_manifest):
        if not isinstance(source, dict):
            continue
        for key in ("closeout_application", "closeout_proposal"):
            record = source.get(key)
            if not isinstance(record, dict) or record.get("section") != section:
                continue
            candidate = _semantic_repository_path(record.get("record"))
            if candidate is not None:
                return candidate
    return f".floppy/closeouts/{section}-closeout.md"


def _git_integrity_control_paths(
    operation: str,
    manifest: dict[str, Any],
    parent_manifest: dict[str, Any] | None,
    section: str,
) -> set[str] | None:
    draft = _git_integrity_draft_path(manifest, parent_manifest, section)
    if draft is None:
        return None
    common = {
        ".floppy/floppies/Floppy-E-Current-Section.md",
        ".floppy/manifest.json",
        ".floppy/roadmap/roadmap.json",
        ".floppy/roadmap/roadmap.md",
        draft,
    }
    if operation == "WORK_PACKAGE_ACCEPTANCE_CONTROL":
        return common | {".floppy/lifecycle-state.json"}
    if operation == "ACTIVATION_CONTROL_COMMIT":
        return common | {
            ".floppy/lifecycle-state.json",
            ".floppy/orchestrator-registry.json",
        }
    if operation in {
        "STATE_PRESERVING_AUTHORITY_HANDOFF",
        "COMPLETION_VERIFICATION_CONTROL",
        "ADMINISTRATOR_ACCEPTANCE_CONTROL",
    }:
        return common | {
            ".floppy/lifecycle-state.json",
            ".floppy/orchestrator-registry.json",
        }
    if operation == "CLOSEOUT_PROPOSAL_CONTROL":
        return common | {
            ".floppy/lifecycle-state.json",
            _git_integrity_closeout_path(
                manifest,
                parent_manifest,
                section,
            ),
        }
    if operation == "CLOSEOUT_APPLICATION_CONTROL":
        try:
            next_section = f"FS-{int(section[3:]) + 1:02d}"
        except ValueError:
            return None
        next_draft = _git_integrity_draft_path(
            manifest,
            parent_manifest,
            next_section,
        )
        if next_draft is None:
            return None
        return common | {
            ".floppy/START-HERE.md",
            ".floppy/README.md",
            ".floppy/floppies/Floppy-D-Project-Map.md",
            ".floppy/lifecycle-state.json",
            ".floppy/orchestrator-registry.json",
            _git_integrity_closeout_path(
                manifest,
                parent_manifest,
                section,
            ),
            next_draft,
        }
    return None


def _git_integrity_manifest_writer(
    manifest: dict[str, Any] | None,
) -> tuple[str | None, str | None]:
    if not isinstance(manifest, dict):
        return None, None
    continuation = manifest.get("continuation_point")
    continuation = continuation if isinstance(continuation, dict) else {}
    authority = manifest.get("authority")
    authority = authority if isinstance(authority, dict) else {}
    writers = {
        value
        for value in (
            manifest.get("repository_writer"),
            continuation.get("repository_writer"),
            authority.get("repository_writer"),
        )
        if isinstance(value, str) and value
    }
    references = {
        value
        for value in (
            manifest.get("writer_authorization_reference"),
            continuation.get("writer_authorization_reference"),
            authority.get("writer_authorization_reference"),
        )
        if isinstance(value, str) and value
    }
    writer = next(iter(writers)) if len(writers) == 1 else None
    reference = next(iter(references)) if len(references) == 1 else None
    return writer, reference


def _git_integrity_operation_name(
    manifest: dict[str, Any],
    parent_manifest: dict[str, Any] | None,
    active: dict[str, Any] | None,
    parent_active: dict[str, Any] | None,
) -> str:
    evidence = manifest.get(GIT_OPERATION_EVIDENCE_KEY)
    if isinstance(evidence, dict):
        value = evidence.get("operation")
        if isinstance(value, str) and value:
            return value
    if (
        isinstance(parent_manifest, dict)
        and parent_active is None
        and isinstance(active, dict)
    ):
        return "ACTIVATION_CONTROL_COMMIT"
    if isinstance(parent_active, dict) and isinstance(active, dict):
        return "AUTHORIZED_IMPLEMENTATION_COMMIT"
    return "LEGACY_IMPLEMENTATION"


def _git_integrity_transition_evidence_valid(
    operation: str,
    manifest: dict[str, Any],
    parent_manifest: dict[str, Any] | None,
    errors: list[str],
) -> None:
    evidence = manifest.get(GIT_OPERATION_EVIDENCE_KEY)
    if operation == "WORK_PACKAGE_ACCEPTANCE_CONTROL":
        if not isinstance(evidence, dict):
            errors.append("GIT_INTEGRITY_CONTROL_EVIDENCE_MISSING")
            return
        transitions = evidence.get("transition_sequence")
        if not isinstance(transitions, list) or len(transitions) != 1:
            errors.append("GIT_INTEGRITY_TRANSITION_SEQUENCE_INVALID")
            return
        item = transitions[0]
        if not isinstance(item, dict):
            errors.append("GIT_INTEGRITY_TRANSITION_EVIDENCE_INVALID: index 0")
            return
        actual = (
            item.get("id"),
            item.get("pre_state"),
            item.get("post_state"),
        )
        if actual not in _GIT_WORK_PACKAGE_ACCEPTANCE_TRANSITIONS:
            errors.append("GIT_INTEGRITY_TRANSITION_SEQUENCE_INVALID: index 0")
        for field in ("actor", "decision"):
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(
                    "GIT_INTEGRITY_TRANSITION_EVIDENCE_INVALID: "
                    f"index 0 field {field}"
                )
        for field in ("inputs", "outputs", "validation_evidence"):
            value = item.get(field)
            if not isinstance(value, (list, dict)) or not value:
                errors.append(
                    "GIT_INTEGRITY_TRANSITION_EVIDENCE_INVALID: "
                    f"index 0 field {field}"
                )
        parent_status = (
            parent_manifest.get("status")
            if isinstance(parent_manifest, dict)
            else None
        )
        if parent_status != item.get("pre_state"):
            errors.append(
                "GIT_INTEGRITY_TRANSITION_PARENT_STATE_MISMATCH: "
                f"expected {item.get('pre_state')} found {parent_status}"
            )
        if manifest.get("status") != item.get("post_state"):
            errors.append(
                "GIT_INTEGRITY_TRANSITION_CANDIDATE_STATE_MISMATCH: "
                f"expected {item.get('post_state')} found {manifest.get('status')}"
            )
        return
    expected = _GIT_CONTROL_TRANSITIONS.get(operation)
    if expected is None:
        return
    if operation == "ACTIVATION_CONTROL_COMMIT":
        return
    if not isinstance(evidence, dict):
        errors.append("GIT_INTEGRITY_CONTROL_EVIDENCE_MISSING")
        return
    transitions = evidence.get("transition_sequence")
    if not isinstance(transitions, list) or len(transitions) != len(expected):
        errors.append("GIT_INTEGRITY_TRANSITION_SEQUENCE_INVALID")
        return
    for index, ((identifier, pre_state, post_state), item) in enumerate(
        zip(expected, transitions, strict=True)
    ):
        if not isinstance(item, dict):
            errors.append(
                f"GIT_INTEGRITY_TRANSITION_EVIDENCE_INVALID: index {index}"
            )
            continue
        if (
            item.get("id") != identifier
            or item.get("pre_state") != pre_state
            or item.get("post_state") != post_state
        ):
            errors.append(
                f"GIT_INTEGRITY_TRANSITION_SEQUENCE_INVALID: index {index}"
            )
        for field in ("actor", "decision"):
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(
                    f"GIT_INTEGRITY_TRANSITION_EVIDENCE_INVALID: "
                    f"index {index} field {field}"
                )
        for field in ("inputs", "outputs", "validation_evidence"):
            value = item.get(field)
            if not isinstance(value, (list, dict)) or not value:
                errors.append(
                    f"GIT_INTEGRITY_TRANSITION_EVIDENCE_INVALID: "
                    f"index {index} field {field}"
                )
    parent_status = (
        parent_manifest.get("status")
        if isinstance(parent_manifest, dict)
        else None
    )
    if parent_status != expected[0][1]:
        errors.append(
            "GIT_INTEGRITY_TRANSITION_PARENT_STATE_MISMATCH: "
            f"expected {expected[0][1]} found {parent_status}"
        )
    if manifest.get("status") != expected[-1][2]:
        errors.append(
            "GIT_INTEGRITY_TRANSITION_CANDIDATE_STATE_MISMATCH: "
            f"expected {expected[-1][2]} found {manifest.get('status')}"
        )


def _git_integrity_operation_evidence_valid(
    operation: str,
    manifest: dict[str, Any],
    parent_manifest: dict[str, Any] | None,
    section: str | None,
    expected_paths: set[str],
    errors: list[str],
) -> None:
    if operation == "ACTIVATION_CONTROL_COMMIT":
        active = manifest.get("active_work_authorization")
        if not isinstance(active, dict) or not _git_integrity_activation_evidence_valid(
            manifest,
            active,
            expected_paths,
        ):
            errors.append("GIT_INTEGRITY_ACTIVATION_EVIDENCE_INVALID")
        return
    if operation in {
        "AUTHORIZED_IMPLEMENTATION_COMMIT",
        "LEGACY_IMPLEMENTATION",
        "BOUNDED_VALIDATOR_CORRECTION",
    }:
        return
    evidence = manifest.get(GIT_OPERATION_EVIDENCE_KEY)
    if not isinstance(evidence, dict):
        errors.append("GIT_INTEGRITY_CONTROL_EVIDENCE_MISSING")
        return
    if evidence.get("operation") != operation:
        errors.append("GIT_INTEGRITY_CONTROL_OPERATION_MISMATCH")
    if evidence.get("section") != section:
        errors.append("GIT_INTEGRITY_CONTROL_SECTION_MISMATCH")
    paths = evidence.get("exact_control_paths")
    normalized_paths = {
        normalized
        for item in paths if isinstance(paths, list) and isinstance(item, str)
        if (normalized := _semantic_repository_path(item)) is not None
    } if isinstance(paths, list) else set()
    if (
        not isinstance(paths, list)
        or len(normalized_paths) != len(paths)
        or normalized_paths != expected_paths
    ):
        errors.append("GIT_INTEGRITY_CONTROL_PATH_EVIDENCE_INVALID")
    expected_exercised = operation == "ROOT_CONTROL_IMPLEMENTATION"
    if evidence.get("implementation_scope_exercised") is not expected_exercised:
        errors.append("GIT_INTEGRITY_SCOPE_EXERCISE_EVIDENCE_INVALID")
    if operation in _GIT_STATE_PRESERVING_OPERATIONS:
        parent_status = (
            parent_manifest.get("status")
            if isinstance(parent_manifest, dict)
            else None
        )
        if manifest.get("status") != parent_status:
            errors.append("GIT_INTEGRITY_STATE_PRESERVATION_FAILED")
        if evidence.get("transition_sequence") != []:
            errors.append("GIT_INTEGRITY_STATE_PRESERVING_TRANSITION_FORBIDDEN")
    _git_integrity_transition_evidence_valid(
        operation,
        manifest,
        parent_manifest,
        errors,
    )


def _git_integrity_clearance_valid(
    manifest: dict[str, Any],
    section: str,
    errors: list[str],
) -> None:
    continuation = manifest.get("continuation_point")
    continuation = continuation if isinstance(continuation, dict) else {}
    authority = manifest.get("authority")
    authority = authority if isinstance(authority, dict) else {}
    values = (
        manifest.get("active_work_authorization"),
        manifest.get("repository_writer"),
        manifest.get("writer_authorization_reference"),
        continuation.get("active_work_authorization"),
        continuation.get("repository_writer"),
        continuation.get("writer_authorization_reference"),
        continuation.get("active_implementation_section"),
        authority.get("active_work_authorization"),
        authority.get("active_implementation_authorization"),
        authority.get("active_implementation_section"),
        authority.get("current_authorized_section"),
        authority.get("repository_writer"),
        authority.get("writer_authorization_reference"),
        authority.get("authorization_id"),
    )
    if any(value is not None for value in values):
        errors.append("GIT_INTEGRITY_AUTHORITY_CLEARANCE_INCOMPLETE")
    writer, reference = _git_integrity_manifest_writer(manifest)
    if writer is not None or reference is not None:
        errors.append("GIT_INTEGRITY_WRITER_CLEARANCE_INCOMPLETE")
    record = _git_integrity_section_record(manifest, section)
    for field in (
        "authorization_id",
        "repository_writer",
        "writer_authorization_reference",
    ):
        if record.get(field) is not None:
            errors.append(
                f"GIT_INTEGRITY_SECTION_CLEARANCE_INCOMPLETE: {field}"
            )


def validate_authorization_git_integrity(
    root: Path,
    manifest: dict[str, Any],
    environ: dict[str, str] | None = None,
) -> list[str]:
    """Validate authorization, writer, operation class, and exact Git scope."""

    environment = os.environ if environ is None else environ
    if environment.get(GIT_CONTROL_OPERATION_ENV) in FS12_FINAL_OPERATIONS:
        return _validate_fs12_final_git_integrity(root, manifest, environment)
    candidate_evidence = manifest.get(GIT_OPERATION_EVIDENCE_KEY)
    runtime_requested = any(
        environment.get(name)
        for name in (
            GIT_AUTHORIZATION_ENV,
            GIT_WRITER_ENV,
            GIT_EXPECTED_HEAD_ENV,
            GIT_SCOPE_COMMIT_ENV,
            GIT_CONTROL_OPERATION_ENV,
            GIT_CONTROL_SCOPE_ENV,
            GIT_CONTROL_BRANCH_ENV,
        )
    ) or isinstance(candidate_evidence, dict)

    errors: list[str] = []
    scope_commit = environment.get(GIT_SCOPE_COMMIT_ENV)
    actual_paths: set[str] = set()
    parent_revision: str | None = None
    candidate_revision: str | None = None
    pending_candidate = not bool(scope_commit)

    head_result = _git_integrity_run(root, "rev-parse", "HEAD")
    if head_result.returncode != 0:
        errors.append(
            "GIT_INTEGRITY_HEAD_READ_FAILED: " + head_result.stderr.strip()
        )
        actual_head = None
    else:
        actual_head = head_result.stdout.strip()

    if scope_commit:
        resolved = _git_integrity_run(
            root,
            "rev-parse",
            "--verify",
            f"{scope_commit}^{{commit}}",
        )
        if resolved.returncode != 0:
            errors.append(f"GIT_INTEGRITY_SCOPE_COMMIT_INVALID: {scope_commit}")
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
        for command in (
            ("diff", "--name-only", "--"),
            ("diff", "--cached", "--name-only", "--"),
            ("ls-files", "--others", "--exclude-standard"),
        ):
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
    active = manifest.get("active_work_authorization")
    active_dict = active if isinstance(active, dict) else None
    parent_active_dict = parent_active if isinstance(parent_active, dict) else None
    operation = _git_integrity_operation_name(
        manifest,
        parent_manifest,
        active_dict,
        parent_active_dict,
    )
    requested_operation = environment.get(GIT_CONTROL_OPERATION_ENV)
    if requested_operation:
        operation = requested_operation
    section = _git_integrity_section_from_context(
        manifest,
        parent_manifest,
        active_dict,
        parent_active_dict,
    )

    if not runtime_requested and active is None and parent_active is None:
        return []

    effective_active: dict[str, Any] | None
    effective_manifest: dict[str, Any] | None
    if operation == "ADMINISTRATOR_ACCEPTANCE_CONTROL":
        effective_active = parent_active_dict
        effective_manifest = parent_manifest
    elif operation in _GIT_NO_AUTHORITY_OPERATIONS:
        effective_active = None
        effective_manifest = manifest
    else:
        effective_active = active_dict
        effective_manifest = manifest

    expected_authorization: str | None = None
    expected_writer: str | None = None
    continuation: dict[str, Any] = {}
    if isinstance(effective_manifest, dict):
        value = effective_manifest.get("continuation_point")
        continuation = value if isinstance(value, dict) else {}

    if effective_active is not None:
        expected_authorization = effective_active.get("authorization_id")
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
                effective_active.get("writer_authorization_reference"),
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
                errors.append(
                    "GIT_INTEGRITY_RECORDED_AUTHORIZATION_REFERENCE_MISSING"
                )
            else:
                errors.append(
                    "GIT_INTEGRITY_RECORDED_AUTHORIZATION_REFERENCE_CONFLICT: "
                    + ", ".join(sorted(recorded_references))
                )
        expected_writer = _git_integrity_expected_writer(
            effective_active,
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
    else:
        if environment.get(GIT_AUTHORIZATION_ENV):
            errors.append("GIT_INTEGRITY_UNEXPECTED_AUTHORIZATION_REFERENCE")
        if environment.get(GIT_WRITER_ENV):
            errors.append("GIT_INTEGRITY_UNEXPECTED_EXECUTING_WRITER")

    expected_branch = (
        effective_active.get("branch")
        if isinstance(effective_active, dict)
        else None
    )
    if not isinstance(expected_branch, str) or not expected_branch:
        supplied_control_branch = environment.get(GIT_CONTROL_BRANCH_ENV)
        expected_branch = (
            supplied_control_branch
            if isinstance(supplied_control_branch, str)
            and supplied_control_branch
            else None
        )
    if not isinstance(expected_branch, str) or not expected_branch:
        package = (
            _git_integrity_section_record(manifest, section)
            if isinstance(section, str)
            else {}
        )
        if not package and isinstance(parent_manifest, dict) and isinstance(section, str):
            package = _git_integrity_section_record(parent_manifest, section)
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

    expected_head = environment.get(GIT_EXPECTED_HEAD_ENV)
    if not expected_head and isinstance(effective_active, dict):
        value = effective_active.get("required_head")
        expected_head = value if isinstance(value, str) else None
    if not expected_head:
        errors.append("GIT_INTEGRITY_EXPECTED_HEAD_MISSING")
    elif actual_head is not None and actual_head != expected_head:
        errors.append(
            "GIT_INTEGRITY_HEAD_MISMATCH: "
            f"expected {expected_head} found {actual_head}"
        )

    implementation_paths: set[str] = set()
    if isinstance(active_dict, dict):
        scope = active_dict.get("exact_file_scope")
        if not isinstance(scope, list):
            errors.append("GIT_INTEGRITY_AUTHORIZED_SCOPE_INVALID")
        else:
            implementation_paths = {
                normalized
                for item in scope
                if isinstance(item, str)
                and (normalized := _semantic_repository_path(item)) is not None
            }
            if len(implementation_paths) != len(scope):
                errors.append("GIT_INTEGRITY_AUTHORIZED_SCOPE_INVALID")

    if candidate_revision is not None:
        committed_manifest = _git_integrity_manifest_at(root, candidate_revision)
        if committed_manifest is not None and committed_manifest != manifest:
            errors.append("GIT_INTEGRITY_CANDIDATE_MANIFEST_MISMATCH")

    expected_paths = set(implementation_paths)
    if operation == "BOUNDED_VALIDATOR_CORRECTION":
        encoded_scope = environment.get(GIT_CONTROL_SCOPE_ENV)
        try:
            supplied_scope = json.loads(encoded_scope) if encoded_scope else None
        except json.JSONDecodeError:
            supplied_scope = None
        if not isinstance(supplied_scope, list):
            errors.append("GIT_INTEGRITY_CONTROL_SCOPE_INVALID")
            expected_paths = set()
        else:
            expected_paths = {
                normalized
                for item in supplied_scope
                if isinstance(item, str)
                and (normalized := _semantic_repository_path(item)) is not None
            }
            if len(expected_paths) != len(supplied_scope):
                errors.append("GIT_INTEGRITY_CONTROL_SCOPE_INVALID")
            standard_allowed = all(
                item in {"tools/validate_floppy.py", "system-manifest.json"}
                or (item.startswith("tests/test_") and item.endswith(".py"))
                for item in expected_paths
            )
            pre_fs12_contract_allowed = (
                expected_paths
                == PRE_FS12_BOUNDED_CONTROL_CORRECTION_PC2_SCOPE
            )
            allowed = standard_allowed or pre_fs12_contract_allowed
            if (
                not allowed
                or "tools/validate_floppy.py" not in expected_paths
                or "system-manifest.json" not in expected_paths
                or not any(item.startswith("tests/test_") for item in expected_paths)
            ):
                errors.append("GIT_INTEGRITY_BOUNDED_CORRECTION_SCOPE_FORBIDDEN")
        if parent_manifest != manifest:
            errors.append("GIT_INTEGRITY_BOUNDED_CORRECTION_MANIFEST_CHANGED")
        if parent_active_dict is None and active_dict is None:
            pass
        elif isinstance(parent_active_dict, dict) and isinstance(active_dict, dict):
            if _git_integrity_authorization_signature(parent_active_dict) != (
                _git_integrity_authorization_signature(active_dict)
            ):
                errors.append(
                    "GIT_INTEGRITY_BOUNDED_CORRECTION_AUTHORIZATION_MUTATED"
                )
        else:
            errors.append(
                "GIT_INTEGRITY_BOUNDED_CORRECTION_AUTHORIZATION_MISSING"
            )
    elif operation == "ACTIVATION_CONTROL_COMMIT":
        if section is None:
            errors.append("GIT_INTEGRITY_ACTIVATION_CONTROL_PATHS_INVALID")
            expected_paths = set()
        else:
            derived = _git_integrity_control_paths(
                operation,
                manifest,
                parent_manifest,
                section,
            )
            if derived is None:
                errors.append("GIT_INTEGRITY_ACTIVATION_CONTROL_PATHS_INVALID")
                expected_paths = set()
            else:
                expected_paths = derived
        if actual_paths & implementation_paths:
            errors.append(
                "GIT_INTEGRITY_ACTIVATION_CHANGED_IMPLEMENTATION_PATHS: "
                + ", ".join(sorted(actual_paths & implementation_paths))
            )
    elif operation in {
        "WORK_PACKAGE_ACCEPTANCE_CONTROL",
        "STATE_PRESERVING_AUTHORITY_HANDOFF",
        "COMPLETION_VERIFICATION_CONTROL",
        "ADMINISTRATOR_ACCEPTANCE_CONTROL",
        "CLOSEOUT_PROPOSAL_CONTROL",
        "CLOSEOUT_APPLICATION_CONTROL",
    }:
        if section is None:
            errors.append("GIT_INTEGRITY_CONTROL_SECTION_INVALID")
            expected_paths = set()
        else:
            derived = _git_integrity_control_paths(
                operation,
                manifest,
                parent_manifest,
                section,
            )
            if derived is None:
                errors.append("GIT_INTEGRITY_CONTROL_PATHS_INVALID")
                expected_paths = set()
            else:
                expected_paths = derived
    elif operation in {
        "AUTHORIZED_IMPLEMENTATION_COMMIT",
        "ROOT_CONTROL_IMPLEMENTATION",
    }:
        expected_paths = set(implementation_paths)
    elif effective_active is None:
        errors.append("GIT_INTEGRITY_ACTIVE_AUTHORIZATION_MISSING")
        expected_paths = set()

    _git_integrity_operation_evidence_valid(
        operation,
        manifest,
        parent_manifest,
        section,
        expected_paths,
        errors,
    )

    if operation == "AUTHORIZED_IMPLEMENTATION_COMMIT":
        if not isinstance(parent_active_dict, dict) or not isinstance(active_dict, dict):
            errors.append("GIT_INTEGRITY_IMPLEMENTATION_PARENT_AUTHORIZATION_MISSING")
        else:
            parent_signature = _git_integrity_authorization_signature(parent_active_dict)
            candidate_signature = _git_integrity_authorization_signature(active_dict)
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
    elif operation == "ROOT_CONTROL_IMPLEMENTATION":
        if not isinstance(parent_active_dict, dict) or not isinstance(active_dict, dict):
            errors.append("GIT_INTEGRITY_ROOT_CONTROL_AUTHORIZATION_MISSING")
        elif _git_integrity_authorization_signature(parent_active_dict) != (
            _git_integrity_authorization_signature(active_dict)
        ):
            errors.append("GIT_INTEGRITY_ROOT_CONTROL_AUTHORIZATION_MUTATED")
    elif operation == "STATE_PRESERVING_AUTHORITY_HANDOFF":
        if not isinstance(parent_active_dict, dict) or not isinstance(active_dict, dict):
            errors.append("GIT_INTEGRITY_HANDOFF_AUTHORIZATION_MISSING")
        else:
            old_id = parent_active_dict.get("authorization_id")
            new_id = active_dict.get("authorization_id")
            if not isinstance(old_id, str) or not isinstance(new_id, str) or old_id == new_id:
                errors.append("GIT_INTEGRITY_HANDOFF_AUTHORIZATION_NOT_REPLACED")
            if parent_active_dict.get("section") != active_dict.get("section"):
                errors.append("GIT_INTEGRITY_HANDOFF_SECTION_CHANGED")
            parent_writer, parent_reference = _git_integrity_manifest_writer(parent_manifest)
            candidate_writer, candidate_reference = _git_integrity_manifest_writer(manifest)
            if parent_reference != old_id:
                errors.append("GIT_INTEGRITY_HANDOFF_PARENT_REFERENCE_INVALID")
            if candidate_reference != new_id:
                errors.append("GIT_INTEGRITY_HANDOFF_CANDIDATE_REFERENCE_INVALID")
            if parent_writer is None or candidate_writer is None or parent_writer == candidate_writer:
                errors.append("GIT_INTEGRITY_HANDOFF_WRITER_NOT_REPLACED")
            if old_id in {candidate_reference, active_dict.get("authorization_id")}:
                errors.append("GIT_INTEGRITY_HANDOFF_STALE_AUTHORIZATION_REMAINS")
            canonical = (
                root / ".floppy/lifecycle-state.json",
                root / ".floppy/orchestrator-registry.json",
            )
            if not all(path.is_file() for path in canonical):
                errors.append("GIT_INTEGRITY_HANDOFF_CANONICAL_BOOTSTRAP_MISSING")
    elif operation == "COMPLETION_VERIFICATION_CONTROL":
        if not isinstance(parent_active_dict, dict) or not isinstance(active_dict, dict):
            errors.append("GIT_INTEGRITY_COMPLETION_AUTHORIZATION_MISSING")
        elif _git_integrity_authorization_signature(parent_active_dict) != (
            _git_integrity_authorization_signature(active_dict)
        ):
            errors.append("GIT_INTEGRITY_COMPLETION_AUTHORIZATION_MUTATED")
    elif operation == "ADMINISTRATOR_ACCEPTANCE_CONTROL":
        if not isinstance(parent_active_dict, dict):
            errors.append("GIT_INTEGRITY_ACCEPTANCE_PARENT_AUTHORIZATION_MISSING")
        if active is not None:
            errors.append("GIT_INTEGRITY_ACCEPTANCE_AUTHORIZATION_REMAINS")
        if section is not None:
            _git_integrity_clearance_valid(manifest, section, errors)
    elif operation in _GIT_NO_AUTHORITY_OPERATIONS:
        if active is not None or parent_active is not None:
            errors.append("GIT_INTEGRITY_CONTROL_AUTHORIZATION_PRESENT")
        writer, reference = _git_integrity_manifest_writer(manifest)
        parent_writer, parent_reference = _git_integrity_manifest_writer(parent_manifest)
        if any(
            value is not None
            for value in (writer, reference, parent_writer, parent_reference)
        ):
            errors.append("GIT_INTEGRITY_CONTROL_WRITER_PRESENT")

    if operation in {
        "WORK_PACKAGE_ACCEPTANCE_CONTROL",
        "ACTIVATION_CONTROL_COMMIT",
    }:
        canonical = (
            root / ".floppy/lifecycle-state.json",
            root / ".floppy/orchestrator-registry.json",
        )
        if not all(path.is_file() for path in canonical):
            errors.append("GIT_INTEGRITY_CANONICAL_CONTROL_RECORDS_REQUIRED")

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
            value = line[3:] if len(line) > 3 else "<unknown>"
            if code == "??":
                untracked.append(value)
                continue
            if code[0] != " ":
                staged.append(value)
            if code[1] != " ":
                tracked.append(value)
        if untracked:
            rejected_untracked = list(untracked)
            if pending_candidate:
                rejected_untracked = [
                    value
                    for value in untracked
                    if (
                        (normalized := _semantic_repository_path(value)) is None
                        or normalized not in expected_paths
                    )
                ]
            if rejected_untracked:
                errors.append(
                    "GIT_INTEGRITY_UNTRACKED_PATHS: "
                    + ", ".join(sorted(rejected_untracked))
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
        errors.append("GIT_INTEGRITY_UNAUTHORIZED_PATHS: " + ", ".join(extra))
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
    """Validate an ordinary applied closeout without freezing its next section."""

    if not isinstance(manifest, dict):
        return ["CLOSEOUT_MANIFEST_INVALID"]

    proposal = manifest.get("closeout_proposal")
    application = manifest.get("closeout_application")
    closed_state = manifest.get("status") == (
        "LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE"
    )
    historical_application = (
        isinstance(application, dict)
        and application.get("transition")
        == "TR-009-APPLY-SECTION-CLOSEOUT"
        and application.get("status") == "APPLIED"
    )
    if not closed_state and not historical_application:
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

    continuation = manifest.get("continuation_point")
    continuation = continuation if isinstance(continuation, dict) else {}
    authority = manifest.get("authority")
    authority = authority if isinstance(authority, dict) else {}
    active = manifest.get("active_work_authorization")
    active = active if isinstance(active, dict) else None
    active_section = active.get("section") if isinstance(active, dict) else None

    if closed_state:
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
        active_authorization_remains = any(
            (
                active is not None,
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

    # Historical closeout remains authoritative after the next section progresses.
    # Only the closed section's own outcome and authority clearance remain frozen.
    if record.get("repository_writer") is not None:
        errors.append(f"CLOSEOUT_REPOSITORY_WRITER_REMAINS: {section}")
    if isinstance(application, dict) and any(
        application.get(field) is not None
        for field in (
            "repository_writer",
            "active_implementation_section",
            "current_authorized_section",
        )
    ):
        errors.append(f"CLOSEOUT_ACTIVE_AUTHORIZATION_REMAINS: {section}")

    if active is not None and active_section != next_section:
        errors.append(f"CLOSEOUT_ACTIVE_AUTHORIZATION_REMAINS: {section}")
    for field in ("active_implementation_section", "current_authorized_section"):
        value = authority.get(field)
        if value is not None and value != next_section:
            errors.append(f"CLOSEOUT_ACTIVE_AUTHORIZATION_REMAINS: {section}")
    if active is not None:
        authorization_id = active.get("authorization_id")
        if next_record.get("authorization_id") != authorization_id:
            errors.append(f"CLOSEOUT_NEXT_SECTION_AUTHORIZATION_MISMATCH: {next_section}")
        writer = continuation.get("repository_writer")
        if next_record.get("repository_writer") != writer:
            errors.append(f"CLOSEOUT_NEXT_SECTION_WRITER_MISMATCH: {next_section}")
    return errors


INITIAL_PROJECT_STATE = {
    "state_id": "LC-ONBOARDING-REQUIRED",
    "section": None,
    "authorization_id": None,
    "dimensions": {
        "roadmap": "ONBOARDING_REQUIRED",
        "work_package": "NOT_ACCEPTED",
        "authority": "NO_ACTIVE_WORK_AUTHORIZATION",
        "implementation": "NOT_STARTED",
        "verification": "NOT_STARTED",
        "acceptance": "PENDING",
        "closeout": "NOT_PROPOSED",
        "migration": "NONE",
        "final_closure": "OPEN",
    },
    "active_implementation_sections": [],
}
PROJECT_CONTROL_SERIALIZATION = "UTF-8/LF/canonical-json-v1"
PROJECT_LIFECYCLE_SCHEMA = "schemas/bce/1.0.0/bce-lifecycle-state.schema.json"


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _validate_canonical_json_file(
    path: Path,
    value: dict[str, Any],
    errors: list[str],
    label: str,
) -> None:
    try:
        actual = path.read_bytes()
    except OSError as exc:
        errors.append(f"{label} is unreadable: {exc}")
        return
    if actual != _canonical_json_bytes(value):
        errors.append(f"{label} serialization is not canonical UTF-8/LF JSON")


def _validate_initial_state_profile(
    state: dict[str, Any],
    errors: list[str],
    label: str,
) -> None:
    for field, expected in INITIAL_PROJECT_STATE.items():
        if state.get(field) != expected:
            errors.append(f"{label} has invalid initial {field}")
    checkpoint = state.get("base_checkpoint")
    if checkpoint is not None and (
        not isinstance(checkpoint, str)
        or re.fullmatch(r"[0-9a-f]{40}", checkpoint) is None
    ):
        errors.append(f"{label} base checkpoint is invalid")
    evidence = state.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"{label} evidence is missing")
    elif not all(isinstance(item, str) and item.strip() for item in evidence):
        errors.append(f"{label} evidence is invalid")


def _validate_project_control_records(
    *,
    root: Path,
    manifest: dict[str, Any],
    state: dict[str, Any],
    registry: dict[str, Any],
    errors: list[str],
    template: bool,
) -> None:
    control = manifest.get("control_state")
    if not isinstance(control, dict):
        errors.append("project manifest control_state record is missing")
        return

    expected_status = "TEMPLATE" if template else "PROVISIONED"
    required_control = {
        "provisioning_version": 1,
        "status": expected_status,
        "lifecycle_state": ".floppy/lifecycle-state.json",
        "lifecycle_state_schema": PROJECT_LIFECYCLE_SCHEMA,
        "orchestrator_registry": ".floppy/orchestrator-registry.json",
        "serialization": PROJECT_CONTROL_SERIALIZATION,
        "implementation_authority": False,
    }
    for field, expected in required_control.items():
        if control.get(field) != expected:
            errors.append(f"project manifest control_state {field} is invalid")

    records = manifest.get("records")
    if not isinstance(records, dict):
        errors.append("project manifest records registry is missing")
    else:
        if records.get("lifecycle_state") != ".floppy/lifecycle-state.json":
            errors.append("project manifest lifecycle-state record path is invalid")
        if records.get("orchestrator_registry") != ".floppy/orchestrator-registry.json":
            errors.append("project manifest orchestrator-registry record path is invalid")

    provisioning = registry.get("provisioning")
    if not isinstance(provisioning, dict):
        errors.append("project orchestrator registry provisioning record is missing")
    else:
        required_provisioning = {
            "version": 1,
            "status": expected_status,
            "serialization": PROJECT_CONTROL_SERIALIZATION,
            "initialized_by": "tools/initialize_project.py",
        }
        for field, expected in required_provisioning.items():
            if provisioning.get(field) != expected:
                errors.append(
                    f"project orchestrator registry provisioning {field} is invalid"
                )

    checkpoint = registry.get("project_checkpoint")
    if not isinstance(checkpoint, dict):
        errors.append("project orchestrator registry checkpoint is missing")
        return
    expected_checkpoint_fields = {"repository", "branch", "worktree", "checkpoint"}
    if set(checkpoint) != expected_checkpoint_fields:
        errors.append("project orchestrator registry checkpoint fields are invalid")

    agreement = {
        "repository": control.get("repository"),
        "branch": control.get("branch"),
        "worktree": control.get("worktree"),
        "checkpoint": control.get("checkpoint"),
    }
    if checkpoint != agreement:
        errors.append("project manifest and orchestrator registry checkpoint disagree")

    assignments = registry.get("current_assignments")
    if not isinstance(assignments, dict):
        errors.append("project orchestrator registry assignments are missing")
    else:
        if assignments.get("repository_writer") is not None:
            errors.append("newly provisioned project must not assign a repository writer")
        if assignments.get("writer_authorization_reference") is not None:
            errors.append(
                "newly provisioned project must not assign a writer authorization reference"
            )

    if state.get("base_checkpoint") != control.get("checkpoint"):
        errors.append("lifecycle-state base checkpoint disagrees with control_state")

    if template:
        for field in ("repository", "branch", "worktree", "checkpoint"):
            if control.get(field) is not None:
                errors.append(f"project seed control_state {field} must be null")
        if state.get("base_checkpoint") is not None:
            errors.append("project seed lifecycle-state base checkpoint must be null")
    else:
        repository = control.get("repository")
        worktree = control.get("worktree")
        branch = control.get("branch")
        commit = control.get("checkpoint")
        if not isinstance(repository, str) or not repository.strip():
            errors.append("provisioned project repository identity is missing")
        if not isinstance(worktree, str) or not worktree.strip():
            errors.append("provisioned project worktree identity is missing")
        else:
            try:
                expected_root = Path(
                    os.environ.get("FLOPPY_EXPECTED_PROJECT_ROOT", str(root))
                ).expanduser().resolve()
                recorded_root = Path(worktree).expanduser().resolve()
                if recorded_root != expected_root:
                    errors.append("provisioned project worktree identity is stale")
            except OSError:
                errors.append("provisioned project worktree identity is invalid")
        if branch is not None and (
            not isinstance(branch, str) or not branch.strip()
        ):
            errors.append("provisioned project branch identity is invalid")
        if commit is not None and (
            not isinstance(commit, str)
            or re.fullmatch(r"[0-9a-f]{40}", commit) is None
        ):
            errors.append("provisioned project checkpoint identity is invalid")

        serialized = "\n".join(
            json.dumps(value, ensure_ascii=False)
            for value in (manifest, state, registry)
        )
        if re.search(r"\{\{[^{}\n]+\}\}", serialized):
            errors.append("provisioned project contains unresolved template tokens")


def _validate_lifecycle_schema_instance(
    source_root: Path,
    state: dict[str, Any],
    errors: list[str],
    label: str,
) -> None:
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        errors.append(f"jsonschema is required for project control-state validation: {exc}")
        return
    schema = validate_json(source_root / PROJECT_LIFECYCLE_SCHEMA, errors)
    if schema is None:
        return
    failures = sorted(
        Draft202012Validator(schema).iter_errors(state),
        key=lambda item: (
            tuple(str(part) for part in item.absolute_path),
            item.message,
        ),
    )
    if failures:
        first = failures[0]
        location = ".".join(str(part) for part in first.absolute_path) or "<root>"
        errors.append(f"{label} violates lifecycle-state schema at {location}: {first.message}")


def validate_project_seed_provisioning(
    root: Path,
    system_manifest: dict[str, Any],
    errors: list[str],
) -> None:
    seed_root = root / "project-seed/.floppy"
    manifest = validate_json(seed_root / "manifest.json", errors)
    state = validate_json(seed_root / "lifecycle-state.json", errors)
    registry = validate_json(seed_root / "orchestrator-registry.json", errors)
    if not all(isinstance(item, dict) for item in (manifest, state, registry)):
        return

    _validate_canonical_json_file(
        seed_root / "manifest.json", manifest, errors, "project seed manifest"
    )
    _validate_canonical_json_file(
        seed_root / "lifecycle-state.json",
        state,
        errors,
        "project seed lifecycle-state",
    )
    _validate_canonical_json_file(
        seed_root / "orchestrator-registry.json",
        registry,
        errors,
        "project seed orchestrator registry",
    )
    _validate_initial_state_profile(state, errors, "project seed lifecycle-state")
    _validate_lifecycle_schema_instance(
        root, state, errors, "project seed lifecycle-state"
    )
    _validate_project_control_records(
        root=root,
        manifest=manifest,
        state=state,
        registry=registry,
        errors=errors,
        template=True,
    )

    registration = system_manifest.get("project_control_state_provisioning")
    if not isinstance(registration, dict):
        errors.append("system manifest does not register project control-state provisioning")
        return
    expected_registration = {
        "section": "FS-11",
        "status": "reusable_product",
        "provisioning_version": 1,
        "serialization": PROJECT_CONTROL_SERIALIZATION,
        "initializer": "tools/initialize_project.py",
        "cli": "tools/floppyctl.py",
        "validator": "tools/validate_floppy.py",
        "lifecycle_state_schema": PROJECT_LIFECYCLE_SCHEMA,
        "atomic_install": True,
        "rollback_on_failure": True,
        "overwrites_existing_control_state": False,
        "grants_implementation_authority": False,
    }
    for field, expected in expected_registration.items():
        if registration.get(field) != expected:
            errors.append(
                f"system manifest project control-state provisioning {field} is invalid"
            )
    artifacts = registration.get("artifacts")
    expected_artifacts = {
        "lifecycle_state_template": "project-seed/.floppy/lifecycle-state.json",
        "manifest_template": "project-seed/.floppy/manifest.json",
        "orchestrator_registry_template":
            "project-seed/.floppy/orchestrator-registry.json",
        "initializer": "tools/initialize_project.py",
        "cli": "tools/floppyctl.py",
        "validator": "tools/validate_floppy.py",
        "tests": "tests/test_project_provisioning.py",
    }
    if not isinstance(artifacts, dict) or set(artifacts) != set(expected_artifacts):
        errors.append(
            "system manifest project control-state provisioning artifacts are incomplete"
        )
        return
    for name, relative in expected_artifacts.items():
        record = artifacts.get(name)
        if not isinstance(record, dict) or record.get("path") != relative:
            errors.append(
                f"system manifest project control-state artifact path is invalid: {name}"
            )
            continue
        artifact_path = root / relative
        if not artifact_path.is_file():
            errors.append(f"project control-state artifact is missing: {relative}")
        elif record.get("sha256") != sha256(artifact_path):
            errors.append(
                f"project control-state artifact digest does not match: {relative}"
            )


def validate_provisioned_project_control_state(
    root: Path,
    manifest: dict[str, Any],
    errors: list[str],
) -> None:
    state = validate_json(root / ".floppy/lifecycle-state.json", errors)
    registry = validate_json(root / ".floppy/orchestrator-registry.json", errors)
    if not isinstance(state, dict) or not isinstance(registry, dict):
        return
    _validate_canonical_json_file(
        root / ".floppy/manifest.json", manifest, errors, "project manifest"
    )
    _validate_canonical_json_file(
        root / ".floppy/lifecycle-state.json",
        state,
        errors,
        "project lifecycle-state",
    )
    _validate_canonical_json_file(
        root / ".floppy/orchestrator-registry.json",
        registry,
        errors,
        "project orchestrator registry",
    )
    _validate_initial_state_profile(state, errors, "project lifecycle-state")
    _validate_lifecycle_schema_instance(
        Path(__file__).resolve().parents[1],
        state,
        errors,
        "project lifecycle-state",
    )
    _validate_project_control_records(
        root=root,
        manifest=manifest,
        state=state,
        registry=registry,
        errors=errors,
        template=False,
    )


def validate_self_hosted_control_mode(
    root: Path,
    manifest: dict[str, Any],
    errors: list[str],
) -> None:
    lifecycle_path = root / ".floppy/lifecycle-state.json"
    registry_path = root / ".floppy/orchestrator-registry.json"
    lifecycle_exists = lifecycle_path.is_file()
    registry_exists = registry_path.is_file()
    if lifecycle_exists != registry_exists:
        errors.append(
            "SELF_HOSTED_CONTROL_MODE_PARTIAL: lifecycle-state and orchestrator "
            "registry must appear together"
        )
        return
    if not lifecycle_exists:
        fs11 = manifest.get("fs_11_work_package")
        if isinstance(fs11, dict) and fs11.get("accepted") is True:
            authorization = manifest.get("active_work_authorization")
            if not isinstance(authorization, dict):
                errors.append(
                    "LEGACY_PRE_INTEGRATION_ACTIVE_AUTHORIZATION_MISSING"
                )
                return
            if authorization.get("section") != "FS-11":
                errors.append(
                    "LEGACY_PRE_INTEGRATION_AUTHORIZED_SECTION_INVALID"
                )
            authority = manifest.get("authority")
            authority = authority if isinstance(authority, dict) else {}
            writer = manifest.get(
                "repository_writer", authority.get("repository_writer")
            )
            reference = manifest.get(
                "writer_authorization_reference",
                authority.get("writer_authorization_reference"),
            )
            if writer is None or reference != authorization.get("authorization_id"):
                errors.append("LEGACY_PRE_INTEGRATION_WRITER_BINDING_INVALID")
        return

    lifecycle = validate_json(lifecycle_path, errors)
    registry = validate_json(registry_path, errors)
    if not isinstance(lifecycle, dict) or not isinstance(registry, dict):
        return

    _validate_canonical_json_file(
        lifecycle_path,
        lifecycle,
        errors,
        "canonical lifecycle-state",
    )
    _validate_canonical_json_file(
        registry_path,
        registry,
        errors,
        "canonical orchestrator registry",
    )
    _validate_lifecycle_schema_instance(
        root,
        lifecycle,
        errors,
        "canonical lifecycle-state",
    )

    if lifecycle.get("state_id") != manifest.get("status"):
        errors.append("CANONICAL_INTEGRATED_LIFECYCLE_STATE_MISMATCH")

    active = manifest.get("active_work_authorization")
    active = active if isinstance(active, dict) else None
    authority = manifest.get("authority")
    authority = authority if isinstance(authority, dict) else {}
    manifest_writer = manifest.get(
        "repository_writer", authority.get("repository_writer")
    )
    manifest_reference = manifest.get(
        "writer_authorization_reference",
        authority.get("writer_authorization_reference"),
    )
    manifest_section = authority.get("active_implementation_section")
    if manifest_section is None and active is not None:
        manifest_section = active.get("section")

    expected_authorization = (
        active.get("authorization_id") if active is not None else None
    )
    if lifecycle.get("authorization_id") != expected_authorization:
        errors.append("CANONICAL_INTEGRATED_AUTHORIZATION_MISMATCH")
    if lifecycle.get("section") not in {manifest_section, active.get("section") if active else None}:
        errors.append("CANONICAL_INTEGRATED_SECTION_MISMATCH")
    expected_sections = [manifest_section] if isinstance(manifest_section, str) else []
    if lifecycle.get("active_implementation_sections") != expected_sections:
        errors.append("CANONICAL_INTEGRATED_ACTIVE_SECTIONS_MISMATCH")

    dimensions = lifecycle.get("dimensions")
    dimensions = dimensions if isinstance(dimensions, dict) else {}
    expected_authority_dimension = (
        "EXACT_SECTION_IMPLEMENTATION_AUTHORIZATION"
        if active is not None
        else "NO_ACTIVE_WORK_AUTHORIZATION"
    )
    if dimensions.get("authority") != expected_authority_dimension:
        errors.append("CANONICAL_INTEGRATED_AUTHORITY_DIMENSION_MISMATCH")
    if active is not None and lifecycle.get("base_checkpoint") != active.get("base_checkpoint"):
        errors.append("CANONICAL_INTEGRATED_BASE_CHECKPOINT_MISMATCH")

    assignments = registry.get("current_assignments")
    assignments = assignments if isinstance(assignments, dict) else {}
    if assignments.get("repository_writer") != manifest_writer:
        errors.append("CANONICAL_INTEGRATED_WRITER_MISMATCH")
    if assignments.get("writer_authorization_reference") != manifest_reference:
        errors.append("CANONICAL_INTEGRATED_WRITER_REFERENCE_MISMATCH")
    expected_model = manifest_writer if active is not None else None
    if assignments.get("current_section_working_model") != expected_model:
        errors.append("CANONICAL_INTEGRATED_WORKING_MODEL_MISMATCH")

    rules = registry.get("rules")
    rules = rules if isinstance(rules, dict) else {}
    if rules.get("maximum_repository_writers") != 1:
        errors.append("CANONICAL_INTEGRATED_WRITER_LIMIT_INVALID")
    if rules.get("writer_requires_exact_authorization_reference") is not True:
        errors.append("CANONICAL_INTEGRATED_WRITER_REFERENCE_RULE_INVALID")
    if rules.get("status_or_role_grants_write_authority") is not False:
        errors.append("CANONICAL_INTEGRATED_ROLE_AUTHORITY_RULE_INVALID")

    orchestrators = registry.get("orchestrators")
    orchestrators = orchestrators if isinstance(orchestrators, list) else []
    identifiers = [
        item.get("id")
        for item in orchestrators
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    ]
    if len(identifiers) != len(set(identifiers)):
        errors.append("CANONICAL_INTEGRATED_DUPLICATE_ORCHESTRATOR")
    active_orchestrators = [
        item
        for item in orchestrators
        if isinstance(item, dict) and item.get("status") == "ACTIVE"
    ]
    if len(active_orchestrators) > 1:
        errors.append("CANONICAL_INTEGRATED_MULTIPLE_ACTIVE_ORCHESTRATORS")
    if manifest_writer is not None and identifiers.count(manifest_writer) != 1:
        errors.append("CANONICAL_INTEGRATED_WRITER_REGISTRATION_INVALID")

    checkpoint = registry.get("project_checkpoint")
    checkpoint = checkpoint if isinstance(checkpoint, dict) else {}
    if active is not None:
        expected_checkpoint = {
            "repository": active.get("repository"),
            "branch": active.get("branch"),
            "worktree": active.get("worktree"),
            "checkpoint": active.get("base_checkpoint"),
        }
        if checkpoint != expected_checkpoint:
            errors.append("CANONICAL_INTEGRATED_CHECKPOINT_MISMATCH")

    provisioning = registry.get("provisioning")
    provisioning = provisioning if isinstance(provisioning, dict) else {}
    if provisioning.get("status") in {None, "TEMPLATE"}:
        errors.append("CANONICAL_INTEGRATED_BOOTSTRAP_MARKER_REMAINS")




# === FS-12 FINAL-PROJECT CLOSURE VALIDATION BEGIN ===
FS12_FINAL_CLOSURE_SCHEMA = {
    "path": "schemas/bce/1.2.0/bce-lifecycle-state.schema.json",
    "$id": "urn:floppy-project-interaction-system:schema:bce-lifecycle-state:1.2.0",
}
FS12_FINAL_CLOSURE_PATHS = {
    ".floppy/README.md", ".floppy/START-HERE.md",
    ".floppy/closeouts/FINAL-PROJECT-CLOSURE.md",
    ".floppy/floppies/Floppy-D-Project-Map.md",
    ".floppy/floppies/Floppy-E-Current-Section.md",
    ".floppy/lifecycle-state.json", ".floppy/manifest.json",
    ".floppy/orchestrator-registry.json",
    ".floppy/roadmap/roadmap.json", ".floppy/roadmap/roadmap.md",
}
FS12_FINAL_OPERATIONS = {"FINAL_CLOSURE_PROPOSAL_CONTROL", "FINAL_CLOSURE_APPLICATION_CONTROL"}

def _fs12_actual_transition_delta(source: dict[str, Any], target: dict[str, Any]) -> set[str]:
    changed = {name for name in REQUIRED_DIMENSIONS if source["dimensions"][name] != target["dimensions"][name]}
    if source.get("active_implementation_section") != target.get("active_implementation_section"):
        changed.add("active_implementation_section")
    return changed

def validate_final_closure_extension(root: Path, manifest: dict[str, Any], errors: list[str]) -> None:
    schema_path = root / FS12_FINAL_CLOSURE_SCHEMA["path"]
    schema = validate_json(schema_path, errors)
    if schema is None: return
    if schema.get("$id") != FS12_FINAL_CLOSURE_SCHEMA["$id"] or schema.get("schema_version") != "1.2.0" or schema.get("normative_section") != "FS-12" or schema.get("status") != "normative" or schema.get("production_enforcement") is not False:
        errors.append("FS-12 final-closure lifecycle schema metadata is invalid")
    try:
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        errors.append(f"FS-12 final-closure lifecycle schema is invalid: {exc}")
    registry = manifest.get("final_project_closure")
    if not isinstance(registry, dict):
        errors.append("system manifest does not register FS-12 final-project closure")
    else:
        record = registry.get("artifacts", {}).get("lifecycle_state_schema") if isinstance(registry.get("artifacts"), dict) else None
        if not isinstance(record, dict) or record.get("path") != FS12_FINAL_CLOSURE_SCHEMA["path"] or record.get("$id") != FS12_FINAL_CLOSURE_SCHEMA["$id"] or record.get("sha256") != sha256(schema_path):
            errors.append("system manifest FS-12 lifecycle schema registration is invalid")
        if registry.get("exact_runtime_paths") != sorted(FS12_FINAL_CLOSURE_PATHS):
            errors.append("system manifest FS-12 final-closure path set is invalid")
    table = validate_json(root / "specs/lifecycle-transition-table.json", errors)
    if table is not None:
        states = {item.get("id"): item for item in table.get("states", []) if isinstance(item, dict)}
        transitions = {item.get("id"): item for item in table.get("transitions", []) if isinstance(item, dict)}
        expected = {
            "TR-014-PROPOSE-FINAL-CLOSURE": ("LC-MIGRATION-APPLIED-VERIFICATION-COMPLETE", "LC-PROJECT-CLOSURE-PROPOSED", {"acceptance", "final_closure"}),
            "TR-015-APPLY-FINAL-CLOSURE": ("LC-PROJECT-CLOSURE-PROPOSED", "LC-PROJECT-FINALLY-CLOSED", {"final_closure"}),
            "TR-021-PROPOSE-FINAL-CLOSURE-NO-MIGRATION": ("LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE", "LC-PROJECT-CLOSURE-PROPOSED-NO-MIGRATION", {"acceptance", "final_closure"}),
            "TR-022-APPLY-FINAL-CLOSURE-NO-MIGRATION": ("LC-PROJECT-CLOSURE-PROPOSED-NO-MIGRATION", "LC-PROJECT-FINALLY-CLOSED-NO-MIGRATION", {"final_closure"}),
        }
        for identifier, (source_id, target_id, dimensions) in expected.items():
            transition = transitions.get(identifier); source = states.get(source_id); target = states.get(target_id)
            if not all(isinstance(x, dict) for x in (transition, source, target)):
                errors.append(f"FS-12 final-closure route is missing: {identifier}"); continue
            if transition.get("from_state_ids") != [source_id] or transition.get("to_state_id") != target_id or set(transition.get("changed_dimensions", [])) != dimensions or _fs12_actual_transition_delta(source, target) != dimensions:
                errors.append(f"FS-12 final-closure route is inconsistent: {identifier}")
        if states.get("LC-PROJECT-CLOSURE-PROPOSED-NO-MIGRATION", {}).get("dimensions", {}).get("migration") != "NONE" or states.get("LC-PROJECT-FINALLY-CLOSED-NO-MIGRATION", {}).get("dimensions", {}).get("migration") != "NONE":
            errors.append("FS-12 no-migration final states must preserve migration NONE")
    record_path = root / ".floppy/closeouts/FINAL-PROJECT-CLOSURE.md"
    if record_path.exists():
        text = record_path.read_text(encoding="utf-8")
        begin = "<!-- FINAL_PROJECT_CLOSURE_PROPOSAL_BEGIN -->"; end = "<!-- FINAL_PROJECT_CLOSURE_PROPOSAL_END -->"
        if begin not in text or end not in text:
            errors.append("canonical final-project closure proposal block is missing")
        else:
            block = text[text.index(begin):text.index(end)+len(end)].encode("utf-8")
            digest = hashlib.sha256(block).hexdigest()
            proposal = manifest.get("final_closure_proposal")
            if not isinstance(proposal, dict) or proposal.get("proposal_sha256") != digest:
                errors.append("canonical final-project closure proposal digest mismatch")

def _validate_fs12_final_git_integrity(root: Path, manifest: dict[str, Any], environment: dict[str, str]) -> list[str]:
    errors: list[str] = []
    operation = environment.get(GIT_CONTROL_OPERATION_ENV)
    scope_commit = environment.get(GIT_SCOPE_COMMIT_ENV)
    revision = scope_commit or "HEAD"
    if scope_commit:
        result = _git_integrity_run(root, "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", revision, "--")
    else:
        result = _git_integrity_run(root, "diff", "--name-only", "--")
    actual = {_semantic_repository_path(x) for x in _git_integrity_lines(result) if _semantic_repository_path(x) is not None} if result.returncode == 0 else set()
    if actual != FS12_FINAL_CLOSURE_PATHS:
        errors.append("GIT_INTEGRITY_FINAL_CLOSURE_PATHS_INVALID: " + ", ".join(sorted(actual)))
    if manifest.get("active_work_authorization") is not None or manifest.get("active_control_work_authorization") is not None or manifest.get("repository_writer") is not None:
        errors.append("GIT_INTEGRITY_FINAL_CLOSURE_ACTIVE_AUTHORITY_FORBIDDEN")
    supplied = environment.get(GIT_AUTHORIZATION_ENV)
    writer = environment.get(GIT_WRITER_ENV)
    if operation == "FINAL_CLOSURE_PROPOSAL_CONTROL" and supplied:
        errors.append("GIT_INTEGRITY_FINAL_CLOSURE_PROPOSAL_AUTHORITY_FORBIDDEN")
    if operation == "FINAL_CLOSURE_APPLICATION_CONTROL" and supplied != "FINAL_CLOSURE_APPLICATION":
        errors.append("GIT_INTEGRITY_FINAL_CLOSURE_APPLICATION_AUTHORITY_MISSING")
    if writer:
        errors.append("GIT_INTEGRITY_FINAL_CLOSURE_WRITER_FORBIDDEN")
    expected_head = environment.get(GIT_EXPECTED_HEAD_ENV)
    head = _git_integrity_run(root, "rev-parse", "HEAD")
    if not expected_head or head.returncode != 0 or head.stdout.strip() != expected_head:
        errors.append("GIT_INTEGRITY_FINAL_CLOSURE_HEAD_MISMATCH")
    return errors
# === FS-12 FINAL-PROJECT CLOSURE VALIDATION END ===

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
    validate_project_seed_provisioning(root, manifest, errors)
    validate_final_closure_extension(root, manifest, errors)

    control_path = root / ".floppy/manifest.json"
    if control_path.is_file():
        control_manifest = validate_json(control_path, errors)
        if control_manifest is not None:
            validate_self_hosted_control_mode(root, control_manifest, errors)
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

        lifecycle_path = root / ".floppy/lifecycle-state.json"
        registry_path = root / ".floppy/orchestrator-registry.json"
        control_declared = isinstance(manifest.get("control_state"), dict)
        if control_declared or lifecycle_path.exists() or registry_path.exists():
            if not lifecycle_path.is_file():
                errors.append("provisioned project lifecycle-state record is missing")
            if not registry_path.is_file():
                errors.append("provisioned project orchestrator-registry record is missing")
            if lifecycle_path.is_file() and registry_path.is_file():
                validate_provisioned_project_control_state(root, manifest, errors)
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
