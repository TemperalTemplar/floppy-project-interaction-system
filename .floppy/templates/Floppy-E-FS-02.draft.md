STATUS: ACCEPTED AS PLANNING BASELINE
ACTIVATION_STATE: AUTHORIZED_NOT_STARTED
IMPLEMENTATION_AUTHORITY: NOT AUTHORIZED

# Floppy E - FS-02 Accepted Work Package

## Objective

Produce normative, versioned contracts from the three FS-01 draft schema
candidates, register them in `system-manifest.json`, add only the read-only
validator support needed to load and validate them, and add focused tests proving
each schema accepts one valid record and rejects one invalid record.

## Exact reusable-product scope

```text
schemas/bce/1.0.0/bce-lifecycle-state.schema.json
schemas/bce/1.0.0/bce-work-authorization.schema.json
schemas/bce/1.0.0/bce-lifecycle-transition.schema.json
tools/validate_floppy.py
system-manifest.json
tests/test_bce_schemas.py
tests/fixtures/bce-schemas/1.0.0/valid/lifecycle-state.json
tests/fixtures/bce-schemas/1.0.0/invalid/lifecycle-state.json
tests/fixtures/bce-schemas/1.0.0/valid/work-authorization.json
tests/fixtures/bce-schemas/1.0.0/invalid/work-authorization.json
tests/fixtures/bce-schemas/1.0.0/valid/lifecycle-transition.json
tests/fixtures/bce-schemas/1.0.0/invalid/lifecycle-transition.json
```

Exactly twelve reusable-product paths are accepted.

## Reusable-product commit limit

No more than two reusable-product commits are permitted:

```text
feat(fs-02): add normative BCE schema contracts
test(fs-02): register and validate normative BCE schemas
```

Reusable-product changed-path verification must inspect the P1 and P2 commit
objects directly. Root `.floppy/**` control commits are excluded.

## Accepted validation set

```text
Verify Draft 2020-12 jsonschema support.
Run tests/test_bce_schemas.py.
Run full test_*.py discovery.
Run git diff --check.
Verify the twelve reusable-product paths and preserved artifacts.
```

## Preserved artifacts

```text
VERSION
schemas/drafts/bce-lifecycle-state.schema.json
schemas/drafts/bce-work-authorization.schema.json
schemas/drafts/bce-lifecycle-transition.schema.json
CTRL-01 artifacts
project-seed/.floppy/**
```

`VERSION` remains `0.4.1-dev`.

## Authorized repository context

```text
Repository:
TemperalTemplar/floppy-project-interaction-system

Branch:
feature/fs-02-normative-bce-schemas

Worktree:
D:\A\Floppy\floppy-fs-02-normative-bce-schemas

Base checkpoint:
e10c4a04ca7f1bee546767f60247c4aaf66eabf8
```

## Current authority boundary

The work package is accepted as the planning baseline.

The activation state is `AUTHORIZED_NOT_STARTED`.

P1 and P2 reusable-product implementation are not authorized.

Repository writer remains `NONE`.

Push, integration, merge, release, migration, production changes, and FS-03 are
not authorized.
