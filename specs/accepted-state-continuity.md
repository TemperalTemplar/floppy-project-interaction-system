# Accepted-State Continuity Protection

**Owner:** `V2-03`  
**Canonical runtime record:** `.floppy/accepted-state.json`  
**Schema:** `schemas/bce/2.0.0/bce-accepted-state.schema.json`  
**Status:** reusable V2 product contract

## 1. Purpose

Accepted-state continuity prevents context loss, model replacement, or re-onboarding from silently reconstructing or replacing project state that the administrator already accepted.

The governing rule is: **Context loss is not authority to reconstruct accepted work.**

The accepted-state record is evidence. It is not operational authority.

## 2. Record family

One accepted project uses one durable accepted-state record family at `.floppy/accepted-state.json`. The record contains one immutable `project_id`, one immutable `original` accepted state, zero or more append-only accepted project-level revisions, one `current_accepted_revision` pointer, and explicit authority-isolation constants.

The source package contains the schema and this specification. A blank accepted-state record is not placed in `project-seed/.floppy/`.

## 3. project_id

`project_id` is a random UUIDv4 in canonical lowercase hyphenated form. It is created exactly once when protected accepted state is formally established: during accepted onboarding for a new project, during accepted formal adoption for an existing non-Floppy project, or during an explicit controlled V2-03 adoption for an older Floppy project.

It is immutable thereafter and must never be derived from project name, repository URL, filesystem path, Git commit, branch, administrator identity, provider, model, conversation, scope, or project outcome. Repository rename, move, continuity-preserving fork, model replacement, orchestrator replacement, or lawful accepted revision does not change it.

## 4. Protected state and accepted-plan binding

Every original or accepted revision contains `protected_state`. It preserves at least project origin, original intent, accepted scope, and accepted project-plan binding. Accepted exclusions, major constraints, and verified starting state belong there when applicable.

The accepted-state record does not reconstruct or replace the accepted plan. It binds accepted plan evidence durably.

## 5. protected_state_sha256

Hash only the parsed `protected_state` object. Canonical bytes are exactly equivalent to:

```python
json.dumps(
    protected_state,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
    allow_nan=False,
).encode("utf-8")
```

Store lowercase hexadecimal SHA-256. The digest excludes the whole accepted-state file and excludes the `protected_state_sha256` field. Serialization has recursive deterministic key ordering, no insignificant whitespace, UTF-8 bytes, no BOM, no trailing newline in the hashed bytes, direct Unicode, and native JSON value types. NaN and Infinity are invalid. Checkout CRLF/LF differences outside parsed JSON string values cannot affect the digest; actual characters inside JSON strings are not normalized.

## 6. Historical roles

The record distinguishes `ORIGINAL`, `CURRENT_ACCEPTED`, and `SUPERSEDED_BUT_HISTORICAL` without rewriting historical revision objects. `ORIGINAL` is the immutable original object. `CURRENT_ACCEPTED` is the revision named by `current_accepted_revision`. Every prior accepted revision remains preserved as `SUPERSEDED_BUT_HISTORICAL`.

If the current pointer is `ORIGINAL`, the original identity remains ORIGINAL while also being the pointer target. When a later accepted revision is appended, older stored revision objects remain byte-for-byte identical as logical JSON objects; historical roles are derived from the pointer.

## 7. Lawful accepted revision

A project-level accepted revision must be explicitly accepted by the administrator, append a new immutable revision object, name the immediately prior current revision in `supersedes_revision_id`, carry its own accepted checkpoint/evidence where applicable, contain its own protected-state digest, advance the current pointer to the newly appended revision, and preserve `project_id`, `original`, and every older revision object exactly.

Ordinary implementation progress, section closeout, model replacement, or context loss is not a project-level accepted revision.

## 8. Deterministic validation

At minimum the validator distinguishes `ACCEPTED_STATE_HISTORY_REWRITE` and `ACCEPTED_STATE_SILENT_DRIFT`.

`ACCEPTED_STATE_HISTORY_REWRITE` covers mutation, removal, reordering, or replacement of protected accepted history, including project ID or original-state replacement. `ACCEPTED_STATE_SILENT_DRIFT` covers integrity or continuity drift such as a protected-state digest mismatch or removal of an already-activated accepted-state record/registration.

Validation is repository-backed when Git history is available. It compares the candidate against the lawful prior repository state and never uses model judgment, semantic similarity, or conversation memory.

## 9. Presence rules

No activation registration plus no record is `VALID LEGACY / PRE-ACCEPTANCE`.

Activation `ACTIVE` plus missing record is `ACCEPTED_STATE_REQUIRED_RECORD_MISSING`.

Record present plus activation missing is `ACCEPTED_STATE_UNREGISTERED_RECORD`.

Activation `ACTIVE` plus record present requires schema, project ID, hash, binding, history, pointer, and authority-isolation validation.

An older Floppy project that never adopted V2-03 remains lawful without the record. The validator never fabricates a record or project ID and never silently backfills old projects. Once activation existed in committed history, deleting registration or record is continuity drift and cannot restore legacy status.

## 10. Project manifest activation

A project that adopts accepted-state continuity records this project-side activation in `.floppy/manifest.json`:

```json
{
  "accepted_state_continuity": {
    "status": "ACTIVE",
    "contract_version": "2.0.0",
    "record": ".floppy/accepted-state.json",
    "schema": "schemas/bce/2.0.0/bce-accepted-state.schema.json"
  }
}
```

The authoritative project ID remains only in the accepted-state record. For new-project acceptance, activation and record are one accepted transaction; a partial activation is invalid.

## 11. Authority isolation

Accepted-state existence grants no implementation authority, repository writer, migration authority, integration authority, or release authority. Current operational lifecycle and authorization records remain separate and controlling.

## 12. Compatibility and seed boundary

V2-03 does not modify frozen V1 lifecycle or authorization schemas, `schemas/bce/2.0.0/bce-compatibility-profile.schema.json`, or `project-seed/.floppy/*`. Older projects are not automatically migrated.

## 13. Later-package boundary

V2-03 provides the stable accepted-origin substrate only. V2-04 owns Continuity Overseer runtime, paired role linkage, persistence, scope-drift orchestration, and Project Orchestrator succession. V2-05 owns Official Project Plan final binding, end-to-end paired-bootstrap proof, integration, and release.

<!-- V2_05_OFFICIAL_PROJECT_PLAN_LINKAGE_BEGIN -->
## V2-05 Official Project Plan linkage

V2-03 remains the authority for durable accepted state. V2-05 adds a non-circular Official Project Plan binding without changing the V2-03 schema or hashing algorithm. For an OPP-active accepted revision, `protected_state.accepted_plan` binds `plan_id`, `plan_revision_id`, `canonical_machine_path`, `active_machine_alias`, the canonical accepted OPP `machine_sha256`, and `substantive_projection_sha256`. These values must agree with the active accepted OPP.

During initial formal adoption, the reviewed OPP substantive digest is frozen before `project_id` exists. One UUIDv4 is then created, the accepted-state ORIGINAL record and OPP ORIGINAL history revision are established in the same accepted-origin transaction, and the final OPP substantive digest must equal the candidate digest. A mismatch is `OFFICIAL_PROJECT_PLAN_UNREVIEWED_SUBSTANTIVE_CHANGE`.

A later accepted-state revision creates a new immutable OPP history revision; prior OPP history is not rewritten. OPP acceptance grants no operational authority and V1 projects receive no automatic backfill or migration.
<!-- V2_05_OFFICIAL_PROJECT_PLAN_LINKAGE_END -->
