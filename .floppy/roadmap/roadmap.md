# BCE Control Layer Development Roadmap

```text
Development roadmap:
ACCEPTED

Lifecycle state:
LC-VERIFICATION-COMPLETE-ACCEPTANCE-PENDING

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
CLOSED

FS-04:
CLOSED

FS-05:
DRAFT_NOT_AUTHORIZED / INACTIVE / NOT ACCEPTED / NOT AUTHORIZED

Repository writer:
NONE

Integration:
NOT AUTHORIZED
```

## Remaining package boundaries

Only the current next section may have exact product paths, exact tests, and a complete work-package draft. Later sections remain bounded capability objectives until their own drafts are prepared from the repository state that exists at that time.

| Section | Capability | Product-path cap | Product-commit cap |
|---|---|---:|---:|
| FS-03 | Add cross-record semantics to the existing validator. | **2 exact paths** | **1** |
| FS-04 | Add thin read-only `status`, `validate`, and `inspect` CLI commands. | **2** | **1** |
| FS-05 | Add closeout-completeness rules to the existing validator and CLI. | **3** | **1** |
| FS-06 | Add read-only authorization and Git-integrity checks. | **3** | **1** |
| FS-07 | Add a small package-content scan reused by packaging and export. | **2** | **1** |
| FS-08 | Produce one validated boot-package ZIP with one checksum manifest. | **3** | **1** |
| FS-09 | Add dry-run and controlled writes for FS-01 lifecycle transitions. | **3** | **2** |
| FS-10 | Implement only proven real migrations; no migration may be invented. | **4 per real path** | **1 per real path** |
| FS-11 | Add final-project closure using the existing validator, CLI, and write code. | **4** | **1** |
| FS-12 | Export and verify one portable ZIP and integrity manifest. | **3** | **1** |

### FS-03 exact product scope

```text
tools/validate_floppy.py
tests/test_bce_semantics.py
```

FS-03 must reuse the FS-02 normative schemas and the existing validator. It must not create a new validation framework, domain layer, loader hierarchy, or package tree.

### Explicit scope limits

- FS-04 through FS-12 do not receive exact filenames or detailed test inventories until their own work-package drafts are prepared.
- FS-05 extends the validator and CLI; it is not a separate closeout engine.
- FS-06 uses Git directly; it does not create a Git abstraction, transaction layer, lock manager, or custom work-package hashing.
- FS-07 is a small deterministic package-content scan, not a DLP or repository-security platform.
- FS-08 and FS-12 reuse the same packaging foundation.
- FS-09 uses Git commits as the recovery boundary; no rollback engine, recovery journal, transaction coordinator, or automatic branch restoration is permitted.
- FS-10 supports only real source formats proven by fixtures and may close with no product changes when no migration is required.
- FS-11 is one validated operation, not a separate closure engine.
- FS-12 excludes history compaction, signing infrastructure, hosting, synchronization, and multiple export formats.

## Common operating rules

1. One start authorization may cover acceptance recording, worktree creation, activation, implementation, validation, authorized product commits, and completion/verification recording.
2. One later administrator-acceptance authorization may cover acceptance recording, distinct closeout proposal and application commits, creation of the next inactive draft, and clearing the writer.
3. Each section returns at most one implementation-completion report and one final closeout report.
4. Do not stop for staging, commit mechanics, or successful routine validation.
5. Stop only for scope or architecture change, a new dependency, security or production impact, destructive action, or failed acceptance criteria.
6. Every closeout creates the next section draft as inactive, unaccepted, unauthorized, and with repository writer `NONE`.
7. Work-package files must not contain full implementation scripts.

## Fixed FS-01 checkpoints

- Accepted implementation: `d03969aa93debb6b705098483c8b59bb9d37d58f`
- Acceptance recording: `5eeb3435644653534a6a430714a84b840ca497c0`
- Approved closeout proposal: `6355dcf9daf8a0bcb4c7cbe4b701cdc49c57d479`
- Product completion: `d907643874f9aa278f31311527f3e7ec907c6cb6`
- Source version: `0.4.1-dev`

## Fixed FS-02 checkpoints

- Product P1: `0ec8da6c7cd2224b284fcff57c3b03a444c594e6`
- Product P2: `fc52c289a0d4816ad5e5c24d01cd4cbbd1ed74c6`
- Completion: `087a8c306f7348b67d12c134a610696f28471aaf`
- Administrator acceptance: `6a174dd0d6a220121b3ed0e14de281afdbd28273`
- Closeout proposal: `849c1fc2e70a76b834256050b4077c0f5096f925`
- Closeout application: `7e1a1ba985e802cadac6588b9425dedfae787ac2`
- Deferred FS-03 draft correction: `b9bdd0594b49eaf0606b28c30acda373fdc9d8b3`
- Remaining-roadmap correction: `a9bae496b7835ebd05ce4d06008ffe0aed25ef7a`
- Source version: `0.4.1-dev`

<!-- FS-05-DRAFT-BOUNDARY:BEGIN -->
### FS-05 — Closed

```text
Status: CLOSED
Implementation: COMPLETE
Verification: COMPLETE
Administrator acceptance: ACCEPTED
Administrator-acceptance commit: 81fd397010bde5d840936af2aed90447dd7f9dfd
Closeout proposal: 0510e5054222711a23903843130369a186e95bc5
Closeout application: THIS_COMMIT
Active authorization: NONE
Repository writer: NONE
```

### FS-06 — Read-only authorization and Git-integrity checks

## Authority state

```text
Work package: ACCEPTED AS PLANNING BASELINE
Activation: RECORDED
Implementation: COMPLETE
Verification: COMPLETE
Administrator acceptance: PENDING
Closeout: NOT STARTED
Active authorization: NONE
Repository writer: NONE
FS-07: INACTIVE / NOT AUTHORIZED
```

## Objective

Add direct, read-only checks for exact branch, exact HEAD, worktree cleanliness, authorization reference, registered repository writer, and exact authorized file scope to the existing validator. Preserve the same result, diagnostics, and exit status through the existing read-only CLI validation path.

## Exact reusable-product paths

```text
tools/validate_floppy.py
tests/test_authorization_git_integrity.py
```

Accepted exact reusable-product paths: `2`
Maximum reusable-product paths: `3`
Maximum reusable-product commits: `1`
Exact product commit message: `feat(fs-06): validate authorization and Git integrity`
`tools/floppyctl.py` is not a product-write path.

## Runtime operation context

```text
FLOPPY_AUTHORIZATION_REFERENCE=<exact active authorization identifier>
FLOPPY_REPOSITORY_WRITER=<exact registered working-model identity>
FLOPPY_EXPECTED_HEAD=<exact checkpoint required by the operation>
FLOPPY_SCOPE_COMMIT=<applicable commit whose paths must match scope>
```

The variables identify the already-authorized operation; they do not assign authority, a writer, a checkpoint, or file scope.

## Focused FS-06 verification inventory

1. exact branch, HEAD, clean worktree, authorization reference, registered writer, and exact authorized file scope pass together.
2. branch mismatch fails with the exact violated condition.
3. detached HEAD fails when an exact branch is required.
4. HEAD mismatch fails with the exact violated condition.
5. dirty tracked, staged, and relevant untracked state fail concisely.
6. missing or mismatched authorization reference fails concisely.
7. missing or mismatched registered writer fails concisely.
8. unauthorized changed paths and missing required paths fail concisely.
9. an exact authorized path set passes.
10. Git-integrity checking performs no repository mutation.
11. CLI validation preserves validator result, diagnostics, and exit status.

## Required regression verification

```text
Focused FS-06 tests: 11 PASSED
Existing FS-05 closeout-completeness tests: 11 PASSED
Existing FS-04 CLI tests: 13 PASSED
Existing FS-03 semantic tests: 18 PASSED
Existing FS-02 schema tests: 6 PASSED
Source validator: PASSED
floppyctl validate: PASSED
Complete repository suite: 84 PASSED
git diff --check: PASSED
```

## Authorized repository context

```text
Starting checkpoint: 3e9758f6b7b9a3ee92c34ac1f3936e3295187a8f
Work-package acceptance: d6c89fc156ddcec9fe3e3a5a7c1f3c9d3851c82a
Activation: 065826bd7743bf6d98cbf98cfe97a20b9bf4d3fb
Reusable-product commit: f323659185cb36705ca2209dfab650bf7bc628a0
Completion and verification: THIS_COMMIT
Administrator acceptance: PENDING
Closeout: NOT STARTED
```

## Architecture and behavior boundary

- Extend `tools/validate_floppy.py` directly and minimally.
- Use Git directly through read-only subprocess calls.
- Preserve existing `floppyctl validate` behavior without a CLI edit.
- Use one focused test path and temporary Git repositories.
- Do not create a Git abstraction, transaction, lock, branch, worktree, recovery, rollback, or custom diff framework.
- Do not add a dependency or custom work-package hash.
- Product validation must not write repository or lifecycle state.
- No FS-07 package-content scanning is authorized.

FS-06 implementation and verification are complete. Administrator acceptance is pending. Active authorization and repository writer are NONE.

Push, merge, integration, release, tag, migration, production changes, administrator acceptance recording, closeout, and FS-07 remain unauthorized.

## Continuation boundary

FS-06 implementation and verification are complete. Administrator acceptance is pending. Active authorization and repository writer are NONE. FS-07 remains inactive and unauthorized.

Push, merge, integration, release, tag, migration, production changes, administrator acceptance recording, closeout, and FS-07 remain unauthorized.
