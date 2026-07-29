# Floppy E — Current Work Section

**Project:** {{PROJECT_NAME}}  
**Status:** ONBOARDING REQUIRED  
**Current section:** NONE AUTHORIZED

## Current execution state

```text
NO_ACTIVE_WORK_AUTHORIZATION
```

## Authorized objective

Project definition and roadmap onboarding only, under canonical Floppy 1E.

No implementation is authorized until:

1. The initial roadmap is explicitly accepted.
2. A proposed first-section work package exists.
3. The user separately authorizes that exact section through Floppy E.

Roadmap acceptance alone does not satisfy step 3.

## In scope

- Inspecting available project evidence
- Classifying verified facts, user requirements, assumptions, unknowns, deferred ideas, and exclusions
- Creating the project outcome contract
- Creating the machine-readable and user-readable roadmaps
- Drafting or finalizing project Floppies A–E
- Creating the first work package as an inactive draft
- Recording explicit roadmap acceptance

## Out of scope

- Project code modification
- Configuration or database changes
- Production contact or mutation
- Credential access
- Commits containing implementation changes
- Deployment, packaging, signing, tagging, or release
- Automatic activation of the first roadmap section
- Treating canonical Floppy 1E as project-specific state

## Completion conditions

- Canonical Floppy 1E was loaded from the pinned source version
- Available evidence was inspected before material questions were asked
- The project outcome contract was presented
- The bounded roadmap and dependencies were presented
- Acceptance criteria identify observable evidence
- Assumptions and unknowns were disclosed
- Deferred and excluded work was separated from the roadmap
- The user explicitly accepted or revised the final roadmap
- Project-owned Floppies A–E and roadmap records were created or finalized
- The first section draft was created with `STATUS: DRAFT_NOT_AUTHORIZED`
- Active Floppy E remained closed unless the user separately authorized Section 01

## Stop conditions

- Project repository cannot be identified
- The pinned source version or Floppy 1E digest cannot be verified
- Existing evidence materially conflicts and the roadmap depends on the conflict
- Required access is unavailable
- A requested action would modify the source repository with project data
- A requested action would begin implementation before separate authorization
- Acceptance criteria cannot be made observable with current information

## Exact continuation point

Run canonical Floppy 1E and the new-project onboarding protocol. Present the proposed project definition and roadmap for user review.

## Required onboarding closeout

After roadmap acceptance, create:

```text
.floppy/onboarding/initial-project-definition.md
.floppy/onboarding/roadmap-acceptance.md
.floppy/templates/Floppy-E-Section-01.draft.md
```

The first-section draft must remain inactive.

## Next model authorization

Not authorized to implement project work.
