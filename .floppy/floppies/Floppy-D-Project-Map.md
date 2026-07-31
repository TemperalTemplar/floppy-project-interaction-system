# Floppy D — Project Map

## Roadmap status

`ACCEPTED`

## Ordered development sections

1. **FS-01 — Formal Lifecycle and State-Transition Specification**
2. **FS-02 — Normative Machine-Readable BCE Schemas**
3. **FS-03 — Semantic Validator 2.0 Engine**
4. **FS-04 — Read-Only floppyctl Core**
5. **FS-05 — Closeout-Completeness Validator**
6. **FS-06 — Structured Authorization, Work-Package Integrity, and Git Checkpoints**
7. **FS-07 — Secret and Unsafe-Content Scanning**
8. **FS-08 — Boot-Package Generation and Verification**
9. **FS-09 — Controlled Lifecycle Write Commands**
10. **FS-10 — Migration Planning and Application**
11. **FS-11 — Final-Project Closure**
12. **FS-12 — BCE Export, Integrity, and History Compaction**

## Current position

- Active implementation section: `FS-01`
- FS-01 work package: `ACCEPTED AS PLANNING BASELINE`
- FS-01 activation: `AUTHORIZED`
- Active work authorization: `FS_01_IMPLEMENTATION`
- FS-01 implementation: `IN PROGRESS`
- Accepted FS-01 work-package checkpoint: `6f79872fa563a7a9c4820bad10ab86edc13782cd`
- Authorization base checkpoint: `b12928e7365149813c00c65c1e409fe2a5d0d36f`
- Implementation branch: `feature/fs-01-lifecycle-specification`
- Implementation worktree: `D:\A\Floppy\floppy-fs-01-lifecycle-specification`

## Permanent development and integration path

For every FS section, source-development control state and reusable source product
follow separate commit and integration paths.

### Control-state path

- Root `.floppy/` commits record authorization, progress, acceptance, and closeout.
- Control commits contain only root `.floppy/` paths.
- Root `.floppy/` remains on source-development control branches.
- Root `.floppy/` commits are never integrated into canonical `main`.

### Reusable product path

- Product commits contain only reusable source-system files.
- Product commits must be independently reviewable and transferable.
- Canonical integration begins from clean `main`.
- Only accepted product commits may be applied to the clean integration branch.
- The final integration comparison must show no root `.floppy/` path.

The onboarding branch must not be merged wholesale. Integration, merge, tagging,
and release each require separate administrator authorization.

New projects receive only generic `project-seed/.floppy/` content and never receive
this source-development project's control records.

## Ordering and authority control

Sections are executed in order unless a later accepted roadmap revision explicitly
changes dependencies. No section becomes active merely because its work package,
predecessor, implementation, verification, acceptance, or closeout is complete.

FS-01 is active only under the exact `FS_01_IMPLEMENTATION` authorization.
Implementation completion, verification, administrator acceptance, closeout,
integration, and FS-02 remain separate states and decisions.
