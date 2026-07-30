# Start Here — Canonical Source-System Development

This BCE controls development of the canonical Floppy Project Interaction System.

## Required read order

1. `.floppy/START-HERE.md`
2. `.floppy/floppies/Floppy-A-HITL.md`
3. `.floppy/floppies/Floppy-E-Current-Section.md`
4. `.floppy/floppies/Floppy-D-Project-Map.md`
5. `.floppy/floppies/Floppy-C-Project-Baseline.md`
6. `.floppy/floppies/Floppy-B-Development-Issues.md`
7. `.floppy/roadmap/roadmap.md`
8. `.floppy/onboarding/roadmap-acceptance.md`

## Present state

```text
Development roadmap:
ACCEPTED

FS-01:
DRAFT_NOT_AUTHORIZED

Active implementation section:
NONE

FS-01 implementation:
NOT STARTED

Active work authorization:
NO_ACTIVE_WORK_AUTHORIZATION
```

## Authority boundary

The accepted operation was only `SOURCE_DEVELOPMENT_BCE_ONBOARDING`.

No implementation may begin from roadmap acceptance, draft creation, branch
existence, or this onboarding record. Implementation requires a separate,
exact, administrator-issued authorization naming the section and permitted scope.

## Repository boundary

- Active source-development BCE: root `.floppy/`
- Reusable seed media: `project-seed/.floppy/`
- Adopting-project BCEs: owned by their respective project repositories

Do not treat `project-seed/.floppy/` as active state.

## Clean-source integration gate

Root `.floppy/` is control-branch-only state. It must not enter canonical `main`,
source packages, release archives, adopting projects, reusable seed content, or
cross-project BCE exports.

New projects receive only `project-seed/.floppy/`. They never receive this source
system's roadmap, authorizations, revisions, handoffs, evidence, or closeouts.

For every FS section:

1. Commit root `.floppy/` control-state changes separately.
2. Commit reusable source-product changes separately.
3. Never mix control-state and product files in one commit.
4. Keep product commits independently reviewable and transferable.
5. Begin canonical integration from clean `main`.
6. Apply only accepted product commits to the integration branch.
7. Exclude all root `.floppy/` commits and require a final comparison with no
   `.floppy/` path.
8. Obtain separate administrator authorization for integration, merge, tag, or
   release.

Never merge `control/source-development-bce-onboarding` wholesale into `main`.

## Exact continuation point

Review `.floppy/templates/Floppy-E-FS-01.draft.md`.

The next administrator decision is to **accept, revise, or reject the FS-01
draft**. Acceptance of that draft must remain separate from implementation
authorization.
