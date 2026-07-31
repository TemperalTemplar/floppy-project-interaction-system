# Root Source-Development BCE

This directory is the active project-control state for development of the canonical
Floppy source system itself.

## Identity

- Project: **Floppy Project Interaction System — BCE Control Layer**
- Repository: `TemperalTemplar/floppy-project-interaction-system`
- Role: `canonical_source_system_development`
- Self-hosted control state: `TRUE`
- Source-system version: `0.4.1-dev`
- Accepted starting checkpoint: `main` at `3efc15a9c232669ddcd3b49cee3ff99f9459dbc3`
- Accepted onboarding checkpoint: `05cc098699b51b1018d729126042270fd6451eda`
- Accepted FS-01 work-package checkpoint: `6f79872fa563a7a9c4820bad10ab86edc13782cd`
- Accepted FS-01 pre-activation BCE checkpoint: `b12928e7365149813c00c65c1e409fe2a5d0d36f`
- FS-01 reusable-product completion checkpoint: `d907643874f9aa278f31311527f3e7ec907c6cb6`
- Implementation branch: `feature/fs-01-lifecycle-specification`
- Authorized FS-01 worktree: `D:\A\Floppy\floppy-fs-01-lifecycle-specification`

## Separation boundary

This root `.floppy/` directory is distinct from `project-seed/.floppy/`.

`project-seed/.floppy/` is reusable initialization media. It is not active project
state for this source-development project and must not be interpreted, updated, or
migrated as part of this BCE.

Existing adopting projects remain independent and unchanged.

## Permanent clean-source integration policy

Root `.floppy/` is control-branch-only project state for development of the Floppy
Project Interaction System. It is not reusable source product and must not be:

- merged into canonical `main`;
- copied into `project-seed/.floppy/`;
- included in source packages or release archives;
- installed into adopting projects;
- treated as reusable project-seed content; or
- embedded in BCE exports intended for other projects.

Newly initialized projects receive only the generic `project-seed/.floppy/`. They
must never receive this source system's development roadmap, authorizations,
revisions, handoffs, evidence, or closeouts.

## Development and integration model

A source-development branch may contain both root `.floppy/` control records and
authorized reusable source-product changes, but a commit must never mix them.

- Control commits contain only root `.floppy/` state.
- Product commits contain only reusable source-system files.
- Product commits must remain independently reviewable and transferable.
- Canonical integration begins from clean `main` and applies only accepted product
  commits.
- Root `.floppy/` commits are excluded from integration.
- The final integration comparison must contain no root `.floppy/` path.
- Integration, merge, tagging, and release require separate administrator
  authorization.
- `control/source-development-bce-onboarding` must not be merged wholesale into
  `main`.

## Current lifecycle state

- Development roadmap: `ACCEPTED`
- FS-01 work package: `ACCEPTED AS PLANNING BASELINE`
- FS-01 activation: `AUTHORIZED`
- Active implementation section: `FS-01`
- FS-01 implementation: `COMPLETE`
- FS-01 verification: `COMPLETE`
- Administrator acceptance: `PENDING`
- Active authorization record: `FS_01_IMPLEMENTATION`
- Additional product writes: `NOT AUTHORIZED`
- Section closeout: `NOT AUTHORIZED`
- Integration: `NOT AUTHORIZED`
- FS-02: `NOT AUTHORIZED`

The exact FS-01 product commits P1 through P5 are complete at
`d907643874f9aa278f31311527f3e7ec907c6cb6`. Required source validation and test
suites passed before C2 recorded completion.

The authorization record remains attached to FS-01 while administrator acceptance
is pending, but it does not permit additional product-file changes. Final
post-C2 validation, the authorized feature-branch push, remote equality
verification, and presentation for administrator acceptance remain.

No acceptance, closeout, integration, merge, tag, release, migration, adopting-
project change, FS-02, FS-03, or later-section authority is implied.

Read `.floppy/START-HERE.md` before using this BCE.
