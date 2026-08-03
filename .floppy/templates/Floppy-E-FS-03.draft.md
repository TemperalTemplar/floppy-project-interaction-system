# Floppy E - FS-03 Accepted Work Package

## Section

`FS-03 — Semantic Validator`

## Status

```text
Work package: ACCEPTED AS PLANNING BASELINE
Activation: NOT YET RECORDED
Implementation authority: NOT YET RECORDED
Implementation: NOT STARTED
Verification: NOT STARTED
Administrator acceptance: PENDING
Closeout: NOT STARTED
Repository writer: NONE
```

## Objective

Add cross-record semantic checks to the existing validator using the FS-02 normative schemas. Validate lifecycle state, authorization consistency, orchestrator and writer references, transition legality, required evidence references, and exact authorized commit scope. Produce concise deterministic diagnostics.

## Exact reusable-product scope

```text
tests/test_bce_semantics.py
tools/validate_floppy.py
```

Maximum reusable-product paths: `2`

Maximum reusable-product commits: `1`

Exact reusable-product commit message:

`feat(fs-03): add BCE semantic validation`

## Required tests

- Valid cross-record lifecycle and authorization relationships pass.
- Each inconsistent relationship fails with one concise diagnostic.
- Existing FS-02 schema tests pass.
- The complete repository test suite passes.

## Explicit exclusions

- No new validation framework.
- No domain layer.
- No loader hierarchy.
- No package tree.
- No service layer.
- No Git-integrity subsystem.
- No lifecycle writes or transition execution.
- No repository mutation by the validator.
- No new dependency.
- No schema or system-manifest change.
- No FS-04 functionality.

## Authorized repository context

```text
Repository: TemperalTemplar/floppy-project-interaction-system
Branch: feature/fs-03-semantic-validator
Worktree: D:\A\Floppy-FS-03
Base checkpoint: 92b4e08477ac44b6d5ac50f213e444203a6762f2
Source version: 0.4.1-dev
```

Acceptance does not itself authorize push, merge, integration, release, tag,
migration, production changes, FS-04 work, or any reusable-product path outside
the exact two-file scope.
