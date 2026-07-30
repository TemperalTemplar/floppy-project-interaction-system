# Draft Floppy E — FS-01

## Draft status

`DRAFT_NOT_AUTHORIZED`

This document is a proposed work package only. It is not the active Floppy E and
does not authorize implementation.

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

## Proposed files in scope

Product and specification files proposed for a later, separately authorized FS-01:

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

Exact filenames for new schema and fixture files must be fixed during work-package
acceptance before activation.

## Explicitly outside FS-01 scope

- `project-seed/.floppy/**`
- root `.floppy/**`, except a separately authorized closeout update after FS-01
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
- draft created ⇒ section active;
- implementation complete ⇒ accepted;
- accepted ⇒ closed without closeout;
- section closed ⇒ next section authorized;
- stale base checkpoint ⇒ write permitted;
- project closed ⇒ active authorization permitted;
- proposed closeout ⇒ applied closeout.

## Proposed implementation controls

Before any FS-01 write:

1. Reverify repository `TemperalTemplar/floppy-project-interaction-system`.
2. Reverify accepted base and source-development BCE state.
3. Create only the separately authorized FS-01 branch and worktree.
4. Confirm no active implementation authorization exists for another section.
5. Activate FS-01 only through an exact administrator statement.
6. Limit changes to the finally accepted FS-01 file list.
7. Run JSON parsing, fixture tests, source validation, and exact diff review.
8. Stop before merge, tag, release, FS-02, seed migration, or adopting-project work.

## Proposed completion criteria

FS-01 implementation may be reported complete only when:

- every lifecycle dimension and allowed state is defined;
- every allowed transition names prerequisites, authority, inputs, outputs, and
  forbidden side effects;
- invalid transitions are explicit;
- roadmap acceptance, authorization, implementation, verification, acceptance,
  closeout, migration, and final closure are demonstrably separate;
- all new JSON artifacts parse;
- all accepted tests pass;
- the final diff is limited to the accepted FS-01 scope;
- source version and format-version effects match the accepted versioning plan;
- no seed or adopting-project migration has occurred.

## Proposed acceptance criteria

Administrator acceptance must be separate from implementation completion and
verification. Acceptance does not itself authorize merge, release, FS-02, or
migration.

## Activation statement required

A future activation must explicitly authorize **FS-01 implementation**, name the
repository, accepted base commit, branch/worktree strategy, final file scope,
allowed validation, commit/push boundary, and all prohibited actions.

Until that separate statement is issued:

`NO_ACTIVE_WORK_AUTHORIZATION`
