STATUS: ACCEPTED_NOT_ACTIVE

# Floppy E - FS-08 Accepted Work Package

## Section

`FS-08 - Validated boot-package ZIP and checksum manifest`

## Accepted authority boundary

```text
Work package: ACCEPTED AS PLANNING BASELINE
Status: ACCEPTED_NOT_ACTIVE
Active: NO
Implementation authorized: NO
Active authorization: NONE
Repository writer: NONE
Branch: feature/fs-08-validated-boot-package
Worktree: D:\A\Floppy-FS-08
Base checkpoint: 38b7e8166f3b1a40631e5f12929855d14b06a631
```

## Exact reusable-product scope

```text
tools/floppyctl.py
tests/test_validated_boot_package.py
```

Maximum reusable-product paths: 3
Maximum reusable-product commits: 1

The implementation must create one deterministic ZIP and one adjacent
SHA-256 checksum manifest, provide controlled verification, preserve the FS-07
scan behavior, add no dependencies, and keep generated artifacts outside the
repository under `C:\Users\alvar.TERMINAL1\Downloads`.

This acceptance commit does not activate implementation. FS-09, push, merge,
integration, tag, release, migration, installer creation, runtime bundling, and
production action remain unauthorized.
