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
- FS-01: `DRAFT_NOT_AUTHORIZED`
- Active implementation section: `NONE`
- FS-01 implementation: `NOT STARTED`
- Active work authorization: `NO_ACTIVE_WORK_AUTHORIZATION`

Read `.floppy/START-HERE.md` before using this BCE.
