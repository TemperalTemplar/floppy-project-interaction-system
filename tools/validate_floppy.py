#!/usr/bin/env python3
"""Validate either the Floppy source repository or an initialized project."""

from __future__ import annotations

import argparse
import hashlib
import json
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


def validate_closeout_completeness(
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


if __name__ == "__main__":
    raise SystemExit(main())
