STATUS: IMPLEMENTATION_IN_PROGRESS

# Floppy E - FS-05 Draft

## Section

`FS-05 - Closeout-completeness rules`

## Authority state

```text
Work package: ACCEPTED AS PLANNING BASELINE
Activation: RECORDED
Implementation: IN PROGRESS
Verification: NOT STARTED
Administrator acceptance: PENDING
Closeout: NOT STARTED
Active authorization: FS_05_IMPLEMENTATION
Repository writer: FS_05_WORKING_MODEL
FS-06: INACTIVE / NOT AUTHORIZED
```

## Objective

Add closeout-completeness rules to the existing validator and CLI.

## Boundary

- Maximum reusable-product paths: `3`
- Accepted exact reusable-product paths: `2`
- Maximum reusable-product commits: `1`
- Exact reusable-product commit message:
  `feat(fs-05): validate closeout completeness`
- `tools/floppyctl.py` is not a product-write path.
- No new dependency is authorized.
- No new closeout, validation, or CLI framework is authorized.
- No FS-06 implementation is authorized.

## Exact reusable-product paths

```text
tools/validate_floppy.py
tests/test_closeout_completeness.py
```

## Required verification

```text
Focused FS-05 tests: NOT RUN
Existing FS-04 CLI tests: NOT RUN
Existing FS-03 semantic tests: NOT RUN
Existing FS-02 schema tests: NOT RUN
Source validator: NOT RUN
Complete repository suite: NOT RUN
git diff --check: NOT RUN
```

## Authorized repository context

```text
Starting checkpoint: b8183030398dea3609d6efbc2c42fe619574ee48
Work-package acceptance: 5b3800e6bbec835dc412fcc98fe653fb36b4928e
Activation: THIS_COMMIT
Reusable-product commit: NOT YET CREATED
Completion and verification: NOT YET CREATED
Administrator acceptance: PENDING
Closeout: NOT STARTED
```

Push, merge, integration, release, tag, migration, production changes,
administrator acceptance recording, closeout, and FS-06 remain unauthorized.
