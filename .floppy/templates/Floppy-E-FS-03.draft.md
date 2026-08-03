# Floppy E - FS-03 Draft

## Section

`FS-03`

## Draft state

```text
Status: DRAFT_NOT_AUTHORIZED
Accepted: NO
Activation authorized: NO
Implementation authorized: NO
Implementation started: NO
Active: NO
Repository writer: NONE
```

## Work package

### Objective

Add cross-record semantic checks to the existing validator. Reuse the FS-02 normative schemas. Validate lifecycle state, authorization consistency, orchestrator and writer references, transition legality, and required evidence references. Produce concise diagnostics.

### Exact reusable-product paths

- `tools/validate_floppy.py`
- `tests/test_bce_semantics.py`

### Commit maximum

`2` reusable-product commits.

### Required tests

- Valid lifecycle, authorization, orchestrator, writer, transition, and evidence references pass.
- Each inconsistent cross-record condition fails with one concise diagnostic.
- Existing FS-02 schema validation remains passing.
- The full test suite passes.

### Explicit exclusions

- No new validation framework.
- No domain layer.
- No loader hierarchy.
- No new package tree.

### Closeout requirement

Record implementation and verification completion, obtain explicit administrator acceptance, propose and apply closeout as distinct commits, create the FS-04 draft inactive and unauthorized, and clear active authorization and repository writer.
