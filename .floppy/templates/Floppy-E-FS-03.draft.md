# Floppy E - FS-03 Active Work Package

## Section

`FS-03 - Semantic Validator`

## Status

```text
Work package: ACCEPTED AS PLANNING BASELINE
Activation: RECORDED
Implementation authority: FS_03_IMPLEMENTATION
Implementation: IN PROGRESS
Verification: NOT STARTED
Administrator acceptance: PENDING
Closeout: NOT STARTED
Repository writer: FS_03_WORKING_MODEL
Writer authorization reference: FS_03_IMPLEMENTATION
```

## Objective

Add cross-record semantic checks to the existing validator using the FS-02
normative schemas. Validate lifecycle state, work authorization, orchestrator
and working-model identities, repository-writer registration, transition
legality and preconditions, required evidence references, identifier
uniqueness, and exact authorized commit scope. Diagnostics must be concise and
deterministic. Validation must remain read-only.

## Exact reusable-product scope

```text
tests/test_bce_semantics.py
tools/validate_floppy.py
```

Maximum reusable-product paths: `2`

Maximum reusable-product commits: `1`

Exact reusable-product commit message:

`feat(fs-03): add BCE semantic validation`

## Explicit exclusions

- No new validation framework, domain layer, loader hierarchy, or package tree.
- No service layer or Git-integrity subsystem.
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
Accepted work-package checkpoint: cf235ef8884cf4f4a4bfde4055c2266c934a142d
Source version: 0.4.1-dev
```

Push, merge, integration, release, tag, migration, production changes,
administrator acceptance recording, closeout, and FS-04 remain unauthorized.
