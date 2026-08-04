# Floppy E - FS-04 Work Package

## Section

`FS-04 - Read-only floppyctl`

## Status

```text
Work package: ACCEPTED AS PLANNING BASELINE
Activation: RECORDED
Implementation authority: ACTIVE
Implementation: IN PROGRESS
Verification: NOT STARTED
Administrator acceptance: PENDING
Closeout: NOT STARTED
Active authorization: FS_04_IMPLEMENTATION
Repository writer: FS_04_WORKING_MODEL
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
Focused floppyctl tests: NOT RUN
Existing FS-03 semantic tests: NOT RUN
Existing FS-02 schema tests: NOT RUN
Source validator: NOT RUN
Complete repository suite: NOT RUN
```

## Authorized repository context

```text
Repository: TemperalTemplar/floppy-project-interaction-system
Branch: feature/fs-04-read-only-floppyctl
Worktree: D:\A\Floppy-FS-04
Base checkpoint: 6afcf6b5766c4b0d7bc02daf4107c0051ebdc715
Source version: 0.4.1-dev
Work-package acceptance commit: fb9b3b26f8023b0f2912bbd918dca2178063fe20
Activation commit: NOT YET RECORDED
Reusable-product commit: NOT YET CREATED
Completion and verification commit: NOT YET CREATED
```

## Explicit exclusions

No plugin system, command framework, service layer, repository abstraction,
domain layer, loader hierarchy, new package tree, second validator, dependency,
lifecycle write, dry-run/write command, packaging/export, push, merge,
integration, release, tag, migration, production action, or FS-05 work is
authorized.

Administrator acceptance and closeout remain pending and are not performed by
this Phase-1 operation.
