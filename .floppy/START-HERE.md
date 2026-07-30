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

## Exact continuation point

Review `.floppy/templates/Floppy-E-FS-01.draft.md`.

The next administrator decision is to **accept, revise, or reject the FS-01
draft**. Acceptance of that draft must remain separate from implementation
authorization.
