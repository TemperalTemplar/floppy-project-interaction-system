STATUS: ACTIVE

# Floppy E - FS-08 Active Work Package

## Section

`FS-08 - Validated boot-package ZIP and checksum manifest`

## Active authorization

```text
Authorization: FS_08_IMPLEMENTATION
Repository writer: FS_08_WORKING_MODEL
Branch: feature/fs-08-validated-boot-package
Worktree: D:\A\Floppy-FS-08
Accepted work-package commit: e7543b8165cf86ab7f59b2773badb19cc64c0063
Activation commit: THIS_COMMIT
Base checkpoint: 38b7e8166f3b1a40631e5f12929855d14b06a631
```

## Exact reusable-product scope

```text
tools/floppyctl.py
tests/test_validated_boot_package.py
```

Only one reusable-product commit is authorized:

`feat(fs-08): add validated boot-package generation`

The implementation may create and verify the one ZIP and one checksum manifest
under `C:\Users\alvar.TERMINAL1\Downloads`. It must not alter source content during artifact generation,
add dependencies, implement lifecycle writes, begin FS-09, or perform push,
merge, integration, tag, release, migration, installer, runtime-bundle, or
production actions.
