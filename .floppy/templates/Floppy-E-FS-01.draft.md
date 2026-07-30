# FS-01 Work Package — Accepted Planning Baseline

## Work-package status

`ACCEPTED AS PLANNING BASELINE`

## Activation and implementation state

```text
FS-01 activation:
NOT AUTHORIZED

FS-01 implementation:
NOT STARTED

Active implementation section:
NONE

Active work authorization:
NO_ACTIVE_WORK_AUTHORIZATION
```

The administrator accepted this document's definition, scope, controls, completion
criteria, and acceptance criteria at source-development BCE checkpoint:

`6f79872fa563a7a9c4820bad10ab86edc13782cd`

The `.draft.md` filename is retained for provenance. This document is not the active
Floppy E, does not replace `.floppy/floppies/Floppy-E-Current-Section.md`, and does
not authorize implementation.

## Section

`FS-01 — Formal Lifecycle and State-Transition Specification`

## Objective

Define a complete, reviewable, implementation-neutral lifecycle and
state-transition specification for BCE-controlled projects before schemas,
validator expansion, CLI behavior, or lifecycle write commands are developed.

The specification must separate orthogonal state dimensions rather than overload
one status field:

- project lifecycle;
- onboarding and roadmap state;
- section state;
- authorization state;
- implementation and verification state;
- acceptance state;
- closeout state;
- migration state;
- final-project state.

## Accepted planning scope

Product and specification files accepted as the planning scope for a later,
separately authorized FS-01 implementation:

- `VERSION`
- `README.md`
- `system-manifest.json`
- `docs/Architecture.md`
- `docs/Migration-Notes.md`
- `schemas/floppy-fields.md`
- `specs/lifecycle-state-model.md` — new
- `specs/lifecycle-transition-table.json` — new
- new draft lifecycle, authorization, and transition schema files
- new valid and invalid lifecycle fixtures
- new lifecycle fixture tests
- minimal `tools/validate_floppy.py` changes only when required to register,
  parse, or integrity-check the new canonical specification artifacts

Exact filenames for new schema and fixture files must be fixed in the future exact
implementation authorization before activation. Work-package acceptance does not
satisfy that requirement.

Root `.floppy/` control records are not reusable FS-01 product files. Any separately
authorized control-state update made during FS-01 must use a root `.floppy/`-only
commit and must not be mixed with product commits.

## Explicitly outside FS-01 product scope

- `project-seed/.floppy/**`
- root `.floppy/**`, except a separately authorized control-state write made in a
  separate root `.floppy/`-only commit
- adopting project repositories
- `tools/initialize_project.py`
- `floppyctl` implementation
- lifecycle write commands
- migrations
- deployment, production operations, credentials, secrets, tags, and releases
- FS-02 or later functionality
- controller or protocol changes unless a verified contradiction is documented
  and separately accepted into the FS-01 work package

## Required lifecycle prohibitions

The specification must make these implications invalid:

- roadmap accepted ⇒ section authorized;
- work package accepted ⇒ section authorized;
- draft created ⇒ section active;
- implementation complete ⇒ accepted;
- accepted ⇒ closed without closeout;
- section closed ⇒ next section authorized;
- stale base checkpoint ⇒ write permitted;
- project closed ⇒ active authorization permitted;
- proposed closeout ⇒ applied closeout.

## Permanent clean-source integration controls

FS-01 and every later source-development section must preserve this model:

1. Root `.floppy/` commits record authorization, progress, acceptance, and
   closeout and contain no reusable product path.
2. Product commits contain only reusable source-system files and contain no root
   `.floppy/` path.
3. A commit must never mix root `.floppy/` changes with product changes.
4. Product commits must be independently reviewable and transferable.
5. Canonical integration must begin from clean `main`.
6. Only accepted product commits may be applied to the clean integration branch.
7. Root `.floppy/` commits must be excluded, and the final integration comparison
   must contain no root `.floppy/` path.
8. Integration, merge, tagging, and release require separate administrator
   authorization.
9. The source-development or onboarding branch must not be merged wholesale into
   `main`.

Root `.floppy/` must not be copied into `project-seed/.floppy/`, included in source
packages or release archives, installed into adopting projects, treated as reusable
seed content, or embedded in BCE exports intended for other projects.

New projects receive only the generic `project-seed/.floppy/` and never receive the
source system's own development roadmap, authorizations, revisions, handoffs,
evidence, or closeouts.

## Accepted implementation controls

Before any FS-01 write:

1. Reverify repository `TemperalTemplar/floppy-project-interaction-system`.
2. Reverify the exact accepted source-development BCE checkpoint and source version.
3. Fix and authorize the exact FS-01 product-file list, including every new schema,
   fixture, and test filename.
4. Create only the separately authorized FS-01 branch and worktree.
5. Confirm no active implementation authorization exists for another section.
6. Activate FS-01 only through an exact administrator statement.
7. Limit changes to the finally authorized FS-01 file list.
8. Separate every root `.floppy/` control commit from every reusable product
   commit.
9. Reject any commit that mixes control and product paths.
10. Run JSON parsing, fixture tests, source validation, and exact diff review.
11. Stop before integration, merge, tag, release, FS-02, seed migration, or
    adopting-project work.

## Accepted completion criteria

FS-01 implementation may be reported complete only when:

- every lifecycle dimension and allowed state is defined;
- every allowed transition names prerequisites, authority, inputs, outputs, and
  forbidden side effects;
- invalid transitions are explicit;
- roadmap acceptance, work-package acceptance, authorization, implementation,
  verification, acceptance, closeout, migration, and final closure are
  demonstrably separate;
- all new JSON artifacts parse;
- all accepted tests pass;
- the final product diff is limited to the authorized FS-01 product scope;
- root control-state and product commits remain separate;
- each product commit is independently reviewable and transferable;
- source version and format-version effects match the accepted versioning plan;
- no seed or adopting-project migration has occurred; and
- no integration, merge, tag, or release has occurred without separate authority.

## Accepted acceptance criteria

Administrator acceptance must be separate from implementation completion and
verification. Acceptance does not itself authorize integration, merge, release,
FS-02, or migration.

Any later integration plan must start from clean `main`, identify the exact accepted
product commits to transfer, exclude root `.floppy/` commits, and prove through the
final comparison that no root `.floppy/` path is present.

## Separate activation statement required

A future activation must explicitly authorize **FS-01 implementation** and name:

- the repository;
- the accepted source-development BCE checkpoint;
- the source version;
- the exact FS-01 branch and worktree;
- the exact product-file list, including every new filename;
- any separately permitted root `.floppy/` control writes;
- allowed validation;
- control/product commit separation;
- commit and push boundaries; and
- all prohibited actions.

Until that separate exact statement is issued:

`NO_ACTIVE_WORK_AUTHORIZATION`
