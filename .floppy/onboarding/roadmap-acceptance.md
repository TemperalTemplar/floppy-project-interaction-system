# Roadmap Acceptance Record

## Accepted roadmap

The administrator accepted the twelve-section BCE Control Layer development
roadmap as the planning baseline on 2026-07-30.

The accepted sections are exactly FS-01 through FS-12 as recorded in:

- `.floppy/roadmap/roadmap.json`
- `.floppy/roadmap/roadmap.md`
- `.floppy/floppies/Floppy-D-Project-Map.md`

## Accepted self-hosted model

The administrator accepted a root `.floppy/` for canonical source-system
development, separate from reusable `project-seed/.floppy/` initialization media.

## Accepted clean-source integration policy

The root source-development `.floppy/` is project-control state only. It remains
on source-development control branches and must not be:

- merged into canonical `main`;
- copied into `project-seed/.floppy/`;
- included in source packages or release archives;
- installed into adopting projects;
- treated as reusable project-seed content; or
- embedded in BCE exports intended for other projects.

The canonical reusable source remains clean and contains reusable system product
files plus the generic `project-seed/.floppy/` only.

Newly initialized projects receive only `project-seed/.floppy/`. They never receive
the Floppy system's source-development roadmap, authorizations, revisions,
handoffs, evidence, or closeouts.

Source-development branches may contain root control records and authorized
product changes, but the accepted integration controls require:

1. Separate root `.floppy/` control commits and reusable product commits.
2. No commit mixing control-state and product paths.
3. Independently reviewable and transferable product commits.
4. Canonical integration beginning from clean `main`.
5. Application of accepted product commits only.
6. Exclusion of every root `.floppy/` commit.
7. A final integration comparison containing no root `.floppy/` path.
8. Separate administrator authorization for integration, merge, tag, and release.

`control/source-development-bce-onboarding` must not be merged wholesale into
`main`.

## Acceptance boundary

```text
Roadmap acceptance does not authorize FS-01 implementation.
FS-01 remains DRAFT_NOT_AUTHORIZED.
Active implementation section remains NONE.
Active work authorization remains NO_ACTIVE_WORK_AUTHORIZATION.
```

## Accepted checkpoint

- Repository: `TemperalTemplar/floppy-project-interaction-system`
- Starting branch: `main`
- Starting commit: `3efc15a9c232669ddcd3b49cee3ff99f9459dbc3`
- Source version: `0.4.1-dev`
- Accepted onboarding checkpoint: `05cc098699b51b1018d729126042270fd6451eda`

## Next administrator decision

Accept, revise, or reject the FS-01 draft. A separate exact implementation
authorization remains mandatory after work-package acceptance.
