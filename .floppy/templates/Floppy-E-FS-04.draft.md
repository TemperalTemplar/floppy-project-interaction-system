# Floppy E - FS-04 Work Package

## Section

`FS-04 - Read-only floppyctl`

## Status

```text
Work package: ACCEPTED AS PLANNING BASELINE
Activation: RECORDED
Implementation: COMPLETE
Verification: COMPLETE
Administrator acceptance: PENDING
Closeout: NOT STARTED
Active authorization: NONE
Repository writer: NONE
```

## Objective

Create a thin read-only CLI over the existing validator and registered-record
model. The only supported commands are `status`, `validate`, and `inspect`.

## Exact reusable-product scope

```text
tools/floppyctl.py
tests/test_floppyctl.py
```

Maximum reusable-product paths: `2`

Maximum reusable-product commits: `1`

Exact reusable-product commit message:

`feat(fs-04): add read-only floppyctl`

## Command behavior

- `status` reads lifecycle and authority values from the controlling registered
  records and performs no product or control writes.
- `validate` invokes the existing `tools/validate_floppy.py` validator and
  preserves its result and diagnostics.
- `inspect` accepts one registered-record selection and displays only that
  registered record. It is not an arbitrary-file reader.
- Unknown commands, missing arguments, invalid selections, and validation
  failures return deterministic diagnostics and non-success status.

## Required verification

```text
Focused floppyctl tests: 13 PASSED
Existing FS-03 semantic tests: 18 PASSED
Existing FS-02 schema tests: 6 PASSED
Source validator: PASSED
Complete repository suite: 62 PASSED
git diff --check: PASSED
```

## Authorized repository context

```text
Repository: TemperalTemplar/floppy-project-interaction-system
Branch: feature/fs-04-read-only-floppyctl
Worktree: D:\A\Floppy-FS-04
Base checkpoint: 6afcf6b5766c4b0d7bc02daf4107c0051ebdc715
Source version: 0.4.1-dev
Work-package acceptance commit: fb9b3b26f8023b0f2912bbd918dca2178063fe20
Activation commit: 841707c6544e2fbddaf4bb3c88d5d7e1626cf6c1
Reusable-product commit: 88d0642f62db17502cf2b3c6f64f24303c1be2b1
Completion and verification commit: THIS_COMMIT
```

## Explicit exclusions

No plugin system, command framework, service layer, repository abstraction,
domain layer, loader hierarchy, new package tree, second validator, dependency,
lifecycle write, dry-run/write command, packaging/export, push, merge,
integration, release, tag, migration, production action, or FS-05 work is
authorized.

Administrator acceptance and closeout remain pending and are not performed by
this Phase-1 operation.
