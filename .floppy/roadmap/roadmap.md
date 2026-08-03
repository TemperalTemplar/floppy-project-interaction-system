# BCE Control Layer Development Roadmap

```text
Development roadmap:
ACCEPTED

Lifecycle state:
LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE

Applied transition:
TR-009-APPLY-SECTION-CLOSEOUT

Authority:
NO_ACTIVE_WORK_AUTHORIZATION

Active implementation section:
NONE

Current authorized section:
NONE

FS-01:
CLOSED

FS-02:
CLOSED

FS-03:
DRAFT_NOT_AUTHORIZED

FS-03 accepted:
NO

FS-03 active:
FALSE

FS-03 implementation authorized:
NO

Repository writer:
NONE

Push, integration, merge, release, tag, migration, production:
NOT AUTHORIZED
```

## Sections

| Section | Plan or work package | Activation | Implementation | Verification | Acceptance | Closeout |
|---|---|---|---|---|---|---|
| FS-01 | `ACCEPTED AS PLANNING BASELINE` | `COMPLETED_HISTORICAL` | `COMPLETE` | `COMPLETE` | `ACCEPTED` | `APPLIED — CLOSED` |
| FS-02 | `ACCEPTED` | `COMPLETED` | `COMPLETE` | `COMPLETE` | `ACCEPTED` | `APPLIED — CLOSED` |
| FS-03 | `DRAFT_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` | `NOT STARTED` | `NOT ACCEPTED` | `NOT_PROPOSED` |
| FS-04 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` | `NOT STARTED` | `NOT ACCEPTED` | `NOT_PROPOSED` |
| FS-05 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` | `NOT STARTED` | `NOT ACCEPTED` | `NOT_PROPOSED` |
| FS-06 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` | `NOT STARTED` | `NOT ACCEPTED` | `NOT_PROPOSED` |
| FS-07 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` | `NOT STARTED` | `NOT ACCEPTED` | `NOT_PROPOSED` |
| FS-08 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` | `NOT STARTED` | `NOT ACCEPTED` | `NOT_PROPOSED` |
| FS-09 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` | `NOT STARTED` | `NOT ACCEPTED` | `NOT_PROPOSED` |
| FS-10 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` | `NOT STARTED` | `NOT ACCEPTED` | `NOT_PROPOSED` |
| FS-11 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` | `NOT STARTED` | `NOT ACCEPTED` | `NOT_PROPOSED` |
| FS-12 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` | `NOT STARTED` | `NOT ACCEPTED` | `NOT_PROPOSED` |

## Remaining Section Work Packages

### FS-03 — Semantic Validator

**Objective**

Add cross-record semantic checks to the existing validator. Reuse the FS-02 normative schemas. Validate lifecycle state, authorization consistency, orchestrator and writer references, transition legality, and required evidence references. Produce concise diagnostics.

**Exact reusable-product paths**

- `tools/validate_floppy.py`
- `tests/test_bce_semantics.py`

**Commit maximum**

`2` reusable-product commits.

**Required tests**

- Valid lifecycle, authorization, orchestrator, writer, transition, and evidence references pass.
- Each inconsistent cross-record condition fails with one concise diagnostic.
- Existing FS-02 schema validation remains passing.
- The full test suite passes.

**Explicit exclusions**

- No new validation framework.
- No domain layer.
- No loader hierarchy.
- No new package tree.

**Closeout requirement**

Record implementation and verification completion, obtain explicit administrator acceptance, propose and apply closeout as distinct commits, create the FS-04 draft inactive and unauthorized, and clear active authorization and repository writer.


### FS-04 — Read-only floppyctl

**Objective**

Create a thin read-only CLI over the existing validator. Initial commands are limited to status, validate, and inspect.

**Exact reusable-product paths**

- `tools/floppyctl.py`
- `tests/test_floppyctl.py`

**Commit maximum**

`2` reusable-product commits.

**Required tests**

- status reports lifecycle and authorization state without writes.
- validate invokes the existing validator and preserves its diagnostics.
- inspect reads only the selected registered record.
- Unknown commands and invalid arguments fail concisely.
- The full test suite passes.

**Explicit exclusions**

- No plugin system.
- No command framework.
- No service layer.
- No repository abstraction.

**Closeout requirement**

Record implementation and verification completion, obtain explicit administrator acceptance, propose and apply closeout as distinct commits, create the FS-05 draft inactive and unauthorized, and clear active authorization and repository writer.


### FS-05 — Closeout Completeness

**Objective**

Implement closeout-completeness checks as rules in the existing validator and expose them through the existing CLI.

**Exact reusable-product paths**

- `tools/validate_floppy.py`
- `tools/floppyctl.py`
- `tests/test_closeout_completeness.py`

**Commit maximum**

`1` reusable-product commit.

**Required tests**

- A complete accepted closeout record passes.
- Missing acceptance, evidence, transition, or next-section draft references fail concisely.
- The CLI reports the same result as the validator.
- The full test suite passes.

**Explicit exclusions**

- No separate closeout-validation engine.
- No duplicate rule loader.
- No independent closeout command framework.

**Closeout requirement**

Record implementation and verification completion, obtain explicit administrator acceptance, propose and apply closeout as distinct commits, create the FS-06 draft inactive and unauthorized, and clear active authorization and repository writer.


### FS-06 — Authorization and Git Integrity

**Objective**

Add read-only checks for exact branch, HEAD, worktree cleanliness, authorization reference, registered writer, and authorized file scope. Use Git directly.

**Exact reusable-product paths**

- `tools/validate_floppy.py`
- `tools/floppyctl.py`
- `tests/test_authorization_git_integrity.py`

**Commit maximum**

`2` reusable-product commits.

**Required tests**

- Exact branch, HEAD, clean worktree, authorization reference, writer, and file scope pass.
- Each mismatch fails with the exact violated condition.
- Checks make no repository changes.
- The full test suite passes.

**Explicit exclusions**

- No custom work-package hashing.
- No repository transactions.
- No lock management.
- No Git abstraction framework.

**Closeout requirement**

Record implementation and verification completion, obtain explicit administrator acceptance, propose and apply closeout as distinct commits, create the FS-07 draft inactive and unauthorized, and clear active authorization and repository writer.


### FS-07 — Secret and Unsafe-content Scanning

**Objective**

Scan only files included in a boot package, handoff, or export using a small deterministic rule set and an explicit allowlist.

**Exact reusable-product paths**

- `tools/package_content_scan.py`
- `tests/test_package_content_scan.py`

**Commit maximum**

`1` reusable-product commit.

**Required tests**

- Known disallowed content in included files is detected.
- Explicit allowlist cases pass.
- Files outside the selected package, handoff, or export are not scanned.
- Findings are deterministic and concise.
- The full test suite passes.

**Explicit exclusions**

- No general DLP system.
- No entropy-analysis platform.
- No credential-management platform.
- No repository-security platform.

**Closeout requirement**

Record implementation and verification completion, obtain explicit administrator acceptance, propose and apply closeout as distinct commits, create the FS-08 draft inactive and unauthorized, and clear active authorization and repository writer.


### FS-08 — Boot-package Generation

**Objective**

Gather the manifest-required context files, run validation and the FS-07 scan, generate one checksum manifest, and produce one ZIP package.

**Exact reusable-product paths**

- `tools/boot_package.py`
- `tools/floppyctl.py`
- `tests/test_boot_package.py`

**Commit maximum**

`2` reusable-product commits.

**Required tests**

- The package contains exactly the manifest-required context files.
- Validation or scanning failure prevents package creation.
- One checksum manifest verifies every packaged file.
- Exactly one ZIP package is produced.
- The full test suite passes.

**Explicit exclusions**

- No signing infrastructure.
- No multiple archive formats.
- No upload service.
- No package registry.

**Closeout requirement**

Record implementation and verification completion, obtain explicit administrator acceptance, propose and apply closeout as distinct commits, create the FS-09 draft inactive and unauthorized, and clear active authorization and repository writer.


### FS-09 — Controlled Lifecycle Writes

**Objective**

Support only the lifecycle transitions defined by FS-01. Require dry-run output, exact authorized paths, a clean repository, pre-write validation, and atomic file replacement. Use Git commits as the recovery boundary.

**Exact reusable-product paths**

- `tools/lifecycle_write.py`
- `tools/floppyctl.py`
- `tests/test_lifecycle_write.py`

**Commit maximum**

`3` reusable-product commits.

**Required tests**

- Every supported FS-01 transition produces an exact dry-run before writing.
- Dirty repositories, unauthorized paths, or failed validation block writes.
- Atomic replacement leaves no partial file state on failure.
- Unsupported transitions are rejected.
- The full test suite passes.

**Explicit exclusions**

- No rollback engine.
- No recovery journal.
- No transaction coordinator.
- No automatic branch restoration.
- No generic mutation framework.

**Closeout requirement**

Record implementation and verification completion, obtain explicit administrator acceptance, propose and apply closeout as distinct commits, create the FS-10 draft inactive and unauthorized, and clear active authorization and repository writer.


### FS-10 — Migration Planning and Application

**Objective**

Support only actual prior Floppy formats proven to exist. Provide one-way plan and apply operations with validation before and after application. Require a real source-format fixture for every accepted migration path.

**Exact reusable-product paths**

- `tools/migrate_floppy.py`
- `tools/floppyctl.py`
- `tests/test_migration.py`
- The accepted FS-10 work package must add the exact path of each real source-format fixture before that migration path is authorized.

**Commit maximum**

`2 per accepted real migration path` reusable-product commits.

**Required tests**

- Every accepted migration path has a real source-format fixture added to the work package as an exact path.
- Planning makes no changes and identifies the exact one-way transformation.
- Application validates before and after migration.
- Unsupported or hypothetical source formats are rejected.
- The full test suite passes for each accepted path.

**Explicit exclusions**

- No generic migration framework.
- No migration language.
- No plugin architecture.
- No hypothetical version matrix.
- No separate rollback system.

**Closeout requirement**

Record implementation and verification completion, obtain explicit administrator acceptance, propose and apply closeout as distinct commits, create the FS-11 draft inactive and unauthorized, and clear active authorization and repository writer.


### FS-11 — Final-project Closure

**Objective**

Implement final closure as one validated operation using the existing semantic validator, CLI, and controlled-write functions.

**Exact reusable-product paths**

- `tools/validate_floppy.py`
- `tools/floppyctl.py`
- `tools/lifecycle_write.py`
- `tests/test_final_closure.py`

**Commit maximum**

`1` reusable-product commit.

**Required tests**

- A fully eligible project closes in one validated operation.
- Missing acceptance, closeout, integrity, or authorization evidence blocks closure.
- The operation reuses the existing validator, CLI, and controlled-write functions.
- The full test suite passes.

**Explicit exclusions**

- No separate final-closure engine.
- No duplicate transition implementation.
- No independent closure framework.

**Closeout requirement**

Record implementation and verification completion, obtain explicit administrator acceptance, propose and apply closeout as distinct commits, create the FS-12 draft inactive and unauthorized, and clear active authorization and repository writer.


### FS-12 — Export and Integrity

**Objective**

Export one portable ZIP containing the accepted context and one integrity manifest, and verify that package. Defer history compaction unless repository evidence proves a real size or performance problem.

**Exact reusable-product paths**

- `tools/export_floppy.py`
- `tools/floppyctl.py`
- `tests/test_export_integrity.py`

**Commit maximum**

`2` reusable-product commits.

**Required tests**

- The export contains the accepted context and one integrity manifest.
- Verification passes for an unchanged package.
- Verification fails for missing, added, or modified content.
- History compaction is not performed without recorded evidence.
- The full test suite passes.

**Explicit exclusions**

- No archival storage.
- No synchronization service.
- No package hosting.
- No signing infrastructure.
- No multiple export formats.

**Closeout requirement**

Record implementation and verification completion, obtain explicit administrator acceptance, and apply final FS-12 closeout without authorizing push, integration, merge, release, tag, migration, or production changes.


## Operating Rules for FS-03 through FS-12

1. A work package contains only:
   - objective;
   - exact reusable-product paths;
   - commit maximum;
   - required tests;
   - explicit exclusions;
   - closeout requirement.
2. Do not place full implementation scripts in a work package.
3. Routine implementation choices belong to the working model. Stop only for scope change, architecture change, security or production impact, a new dependency, a destructive operation, or failed acceptance criteria.
4. One start authorization may permit work-package acceptance recording, branch and worktree creation, activation recording, authorized implementation, validation, authorized product commits, and implementation and verification completion recording, stopping with administrator acceptance pending.
5. One later explicit administrator-acceptance authorization may permit acceptance recording, distinct closeout proposal and application commits, creation of the next inactive unauthorized draft, clearing active authorization and repository writer, and stopping without beginning the next section.
6. Do not return intermediate reports for review, staging, committing, closeout proposal, or closeout application when all guards pass.
7. Each section returns at most one implementation-completion report and one final closeout report.
8. A blocker report contains only the exact blocker, current branch and HEAD, whether files or commits changed, and the smallest required administrator decision.

## Fixed FS-01 Checkpoints

- Accepted implementation: `d03969aa93debb6b705098483c8b59bb9d37d58f`
- Acceptance recording: `5eeb3435644653534a6a430714a84b840ca497c0`
- Approved closeout proposal: `6355dcf9daf8a0bcb4c7cbe4b701cdc49c57d479`
- Product completion: `d907643874f9aa278f31311527f3e7ec907c6cb6`
- Source version: `0.4.1-dev`

## Fixed FS-02 Checkpoints

- Product P1: `0ec8da6c7cd2224b284fcff57c3b03a444c594e6`
- Product P2: `fc52c289a0d4816ad5e5c24d01cd4cbbd1ed74c6`
- Completion: `087a8c306f7348b67d12c134a610696f28471aaf`
- Administrator acceptance: `6a174dd0d6a220121b3ed0e14de281afdbd28273`
- Closeout proposal: `849c1fc2e70a76b834256050b4077c0f5096f925`
- Closeout application: `7e1a1ba985e802cadac6588b9425dedfae787ac2`
- Deferred FS-03 draft correction: `b9bdd0594b49eaf0606b28c30acda373fdc9d8b3`
- Source version: `0.4.1-dev`

## Continuation Boundary

FS-02 is closed.

FS-03 exists only as `DRAFT_NOT_AUTHORIZED`. It is inactive, unaccepted, and
unauthorized. Repository writer is `NONE`.

The next legal operation is preparation, revision, acceptance, or withholding
of the FS-03 work package—not implementation.
