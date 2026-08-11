# Official Project Plan — V2-05 Normative Contract

## Authority and identity ordering

The Official Project Plan (OPP) is the accepted planning baseline for V2 projects. OPP existence, review-candidate existence, or plan acceptance grants no implementation authority, repository writer, migration authority, main-modification authority, integration authority, tag authority, release authority, or final-closure authority.

Before acceptance, Floppy 1E produces a noncanonical `OFFICIAL PROJECT PLAN REVIEW CANDIDATE`. Its machine representation has exactly `candidate_format`, `candidate_format_version`, and `substantive_plan`. Constants are `floppy-official-project-plan-review-candidate` and `1.0.0`. No `project_id`, plan ID, accepted-state revision ID, binding, provenance, acceptance, or revision field exists before acceptance.

The candidate substantive digest is external evidence named `candidate_substantive_sha256`. Hash only parsed `substantive_plan` with UTF-8 canonical JSON using sorted keys, `ensure_ascii=False`, separators `(",", ":")`, and `allow_nan=False`. The digest is not inserted into the candidate object.

## Sixteen reviewed substantive fields

`substantive_plan` contains exactly: `project_identity`, `intended_observable_final_outcome`, `accepted_scope`, `accepted_exclusions`, `major_constraints`, `verified_starting_state`, `important_assumptions`, `known_unknowns`, `accepted_architectural_decisions`, `section_roadmap`, `deferred_work`, `explicitly_rejected_work`, `migration_deployment_considerations`, `project_level_risks`, `authority_model`, and `first_proposed_work_section`.

Nested structures and constants are normative in the JSON schema. In particular, the first proposed section is `DRAFT_NOT_AUTHORIZED`, work-package acceptance `NOT_ACCEPTED`, implementation/verification `NOT_STARTED`, and its implementation authorization, section working model, and repository writer are mandatory nulls. The authority model preserves administrator final authority and requires separate explicit implementation authorization.

## Accepted-origin transaction

After explicit administrator acceptance of the exact external candidate digest, one logical accepted-origin transaction freezes the candidate digest; creates one random canonical lowercase UUIDv4 `project_id` exactly once; derives `plan_id = OPP-<project_id>`, initial plan/accepted-state revision `ORIGINAL`, `CO-<project_id>`, and `ORCH-<project_id>-00000001`; renders accepted machine/human roadmap and digests; adds accepted mechanics around the unchanged sixteen-field substantive projection; and requires the final projection digest to equal the reviewed digest or stops with `OFFICIAL_PROJECT_PLAN_UNREVIEWED_SUBSTANTIVE_CHANGE`.

The transaction next establishes accepted OPP history and aliases, V2-03 accepted state, then downstream protected-state and V2-04 shared-origin linkage. Only after accepted state exists are the paired Continuity Overseer and initial Project Orchestrator prompts rendered. A partial accepted-origin transaction is invalid and no durable project ID may escape it.

## Accepted record and immutable history

The accepted root has exactly 28 fields and `additionalProperties=false`. `format=floppy-official-project-plan`, `format_version=1.0.0`, `contract_version=2.0.0`, `plan_id=OPP-<project_id>`, and `plan_revision_id=accepted_state_revision_id`.

Active aliases:
- `.floppy/project-plan/official-project-plan.json`
- `.floppy/project-plan/official-project-plan.md`

Immutable history:
- `.floppy/project-plan/history/<accepted_state_revision_id>.json`
- `.floppy/project-plan/history/<accepted_state_revision_id>.md`

Every revision identifies its immutable history path as canonical identity. The active aliases are `MUTABLE_POINTER_COPY_TO_CURRENT_ACCEPTED_REVISION` and must be byte-for-byte copies of the current immutable revision. Prior history is never rewritten.

## Non-circular accepted-state/origin chain

`project_origin_binding` carries only `origin_contract`, project ID, accepted-state path/revision ID, Continuity Overseer ID, initial Project Orchestrator ID, and `shared_origin_linkage=DERIVED_AFTER_ACCEPTED_STATE_ESTABLISHMENT`.

The OPP MUST NOT embed `protected_state_sha256` or `shared_origin_sha256`. The lawful chain is `OPP accepted machine digest -> accepted-state accepted-plan binding -> protected_state_sha256 -> V2-04 shared_origin_sha256`. Downstream digests never feed back into the already-hashed OPP.

For an OPP-active accepted revision, the V2-03 `protected_state.accepted_plan` object binds at least `plan_id`, `plan_revision_id`, `canonical_machine_path`, `active_machine_alias`, canonical accepted-plan `machine_sha256`, and `substantive_projection_sha256`. This is a downstream binding from accepted state to the already-complete OPP and therefore does not create a digest cycle.

The immutable human revision and active human alias are byte-identical. The human form records `Plan ID: <plan_id>`, `Plan revision: <plan_revision_id>`, and `Machine SHA-256: <canonical accepted machine digest>` so machine/human identity can be verified deterministically.

## Roadmap and provider equivalence

`roadmap_binding` fixes `.floppy/roadmap/roadmap.json`, `.floppy/roadmap/roadmap.md`, their SHA-256 values, and `section_roadmap_sha256`. Validation recomputes those values and proves the OPP section-roadmap projection corresponds to accepted roadmap evidence.

Class A/B/C differ only in transport. Their normalized result preserves the same project ID, plan/revision and OPP digests, accepted-state revision, Continuity Overseer/initial orchestrator linkage, accepted roadmap, first section `DRAFT_NOT_AUTHORIZED`, implementation authorization `NONE`, repository writer `NONE`, and migration `NONE`.

## Existing project and V1 behavior

Existing non-Floppy work is inspected and preserved before questioning; verified existing state becomes `verified_starting_state`. Existing pre-OPP V2 projects preserve project ID, ORIGINAL state, shared origin, Continuity Overseer identity, and orchestrator history; OPP adoption uses a new lawfully accepted V2-03 revision rather than rewriting ORIGINAL. Supported V1 projects may continue as V1 without project-ID backfill, OPP, Continuity Overseer, migration, or accepted-state rewriting. Explicit V2 adoption layers V2 records without silently changing frozen V1 schemas.

## Provider documentation freshness

D1 is required before V2-05 verification completion and records provider, official documentation consulted where practical, verification date, capability facts checked, result, and capability class. Provider facts remain `NON_NORMATIVE_TRANSPORT_GUIDANCE`. D2 occurs after clean-main integration validation and before T1/REL1; material staleness produces `PROVIDER_DOCUMENTATION_REFRESH_REQUIRED` and blocks tag/publication pending separately authorized correction.

## Source-content finality

P1 establishes `VERSION=2.0.0`, `system-manifest.system_version=2.0.0`, `system-manifest.status=stable-release`, and compatibility source identity `2.0.0`. Here `stable-release` means only final intended V2.0.0 source content with no planned pre-release source mutation. It does not establish source verification, administrator result acceptance, main integration, tag, or public release; those remain V1/TR-006, A2/TR-007, I1, T1, and REL1 facts respectively.
