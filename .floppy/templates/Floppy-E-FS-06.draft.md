STATUS: VERIFICATION_COMPLETE_ACCEPTANCE_PENDING

# Floppy E - FS-06 Work Package

## Section

`FS-06 - Read-only authorization and Git-integrity checks`

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
