STATUS: IMPLEMENTATION_IN_PROGRESS

# Floppy E - FS-07 Work Package

## Section

`FS-07 - Deterministic package-content scan`

## Authority state

```text
Work package: ACCEPTED AS PLANNING BASELINE
Activation: RECORDED
Implementation: IN PROGRESS
Verification: NOT STARTED
Administrator acceptance: PENDING
Closeout: NOT STARTED
Active authorization: FS_07_IMPLEMENTATION
Repository writer: FS_07_WORKING_MODEL
FS-08: INACTIVE / NOT AUTHORIZED
```

## Objective

Extend the existing read-only `floppyctl` architecture with one deterministic
logical package-content inventory command.

## Exact reusable-product scope

```text
tools/floppyctl.py
tests/test_package_content_scan.py
```

Maximum reusable-product paths: `2`

Maximum reusable-product commits: `1`

Exact reusable-product commit:

`feat(fs-07): add deterministic package-content scan`

## Command contract

```text
D:\A\Tools\Python313\python.exe -B tools\floppyctl.py --root <repository> scan <scan-root>
```

The command emits compact deterministic JSON containing the repository-relative
normalized scan root and a sorted list of `directory` and `file` entries.
Logical paths always use `/`. It rejects escaping roots, unsafe links or
reparse points, unsupported entry types, duplicate logical paths, and
case-colliding logical paths. It excludes timestamps, inode values, and
absolute checkout paths and performs no writes.

## Required verification

```text
Focused FS-07 tests: NOT RUN
FS-06 authorization/Git-integrity tests: NOT RUN
FS-05 closeout-completeness tests: NOT RUN
FS-04 CLI tests: NOT RUN
FS-03 semantic-validator tests: NOT RUN
FS-02 schema tests: NOT RUN
Complete repository suite: NOT RUN
Source validator: NOT RUN
floppyctl validation: NOT RUN
JSON parsing: NOT RUN
Lifecycle consistency: NOT RUN
Historical phase validation: NOT RUN
git diff --check: NOT RUN
```

## Authorized repository context

```text
Repository: TemperalTemplar/floppy-project-interaction-system
Branch: feature/fs-07-deterministic-package-content-scan
Worktree: D:\A\Floppy-FS-07
Authorization: FS_07_IMPLEMENTATION
Repository writer: FS_07_WORKING_MODEL
```

## Checkpoints

```text
Starting checkpoint: 53ad8cbd82932a40112f44142bfc1fe9efac5643
Work-package acceptance: dc454b7f9d1d1612f76a66f0ac5d3e95d13f19f1
Activation: THIS_COMMIT
Reusable-product commit: NOT YET CREATED
Implementation and verification completion: NOT YET CREATED
```

Push, merge, integration, tag, release, migration, packaging, export,
production changes, administrator-acceptance recording, closeout, and FS-08
remain unauthorized.
