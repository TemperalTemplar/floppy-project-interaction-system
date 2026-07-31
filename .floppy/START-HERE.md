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

FS-01 work package:
ACCEPTED AS PLANNING BASELINE

FS-01 activation:
AUTHORIZED

Active implementation section:
FS-01

FS-01 implementation:
IN PROGRESS

Active work authorization:
FS_01_IMPLEMENTATION

Authorization base checkpoint:
b12928e7365149813c00c65c1e409fe2a5d0d36f
```

## Authority boundary

The administrator issued the exact `FS_01_IMPLEMENTATION` authorization against
the accepted source-development BCE checkpoint:

`b12928e7365149813c00c65c1e409fe2a5d0d36f`

The authorized implementation branch and worktree are:

```text
Branch:
feature/fs-01-lifecycle-specification

Worktree:
D:\A\Floppy\floppy-fs-01-lifecycle-specification

Source version:
0.4.1-dev
```

Authority is limited to the exact named root-control files, reusable product files,
commit sequence, validator scope, tests, validation operations, push boundary, and
prohibited actions recorded by the active Floppy E and manifest.

No state or decision silently implies administrator acceptance, section closeout,
integration, merge, release, migration authority, FS-02 authority, or later work.

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

FS-01 implementation is active under `FS_01_IMPLEMENTATION`.

After the separate C1 activation commit, continue only through the authorized
product commits P1 through P5, required parsing and validation, and the separate
C2 implementation-completion control commit.

Implementation completion will remain distinct from administrator acceptance.
