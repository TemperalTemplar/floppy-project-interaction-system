# Floppy E - FS-03 Draft

## Authority state

```text
Status: DRAFT_NOT_AUTHORIZED
Accepted: NO
Activation authorized: NO
Implementation authorized: NO
Implementation started: NO
Active: NO
Repository writer: NONE
```

## Objective

Add cross-record semantic checks to the existing validator using the FS-02 normative schemas. Validate lifecycle state, authorization consistency, orchestrator and writer references, transition legality, and required evidence references. Produce concise diagnostics.

## Exact reusable-product paths

```text
tools/validate_floppy.py
tests/test_bce_semantics.py
```

Maximum reusable-product paths: `2`

Maximum reusable-product commits: `1`

## Required tests

- Valid cross-record lifecycle and authorization relationships pass.
- Each inconsistent relationship fails with one concise diagnostic.
- Existing FS-02 schema tests and the full test suite pass.

## Explicit exclusions

- No new validation framework.
- No domain layer.
- No loader hierarchy.
- No new package tree.
- No product write, branch, worktree, commit, push, merge, integration, release, migration, production action, or FS-04 authorization is granted by this draft.

## Closeout rule

Use the common remaining-section closeout rule in `.floppy/roadmap/roadmap.json`: record completion and verification, obtain explicit administrator acceptance, propose and apply closeout as distinct commits, create the FS-04 draft inactive and unauthorized, and clear active authorization and repository writer.
