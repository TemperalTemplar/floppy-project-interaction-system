# Floppy D — Current Project Map

**Project:** {{PROJECT_NAME}}  
**Onboarding controller:** canonical `onboarding/Floppy_1E.md`  
**Roadmap status:** ONBOARDING REQUIRED  
**Rule:** The roadmap may preserve future ideas without authorizing them.

## Project purpose

[Define the accepted project outcome during Floppy 1E onboarding.]

## Roadmap authority

Detailed roadmap records:

```text
.floppy/roadmap/roadmap.json
.floppy/roadmap/roadmap.md
```

- `roadmap.json` is authoritative for machine-readable section identity, dependencies, status, and current authorization.
- `roadmap.md` is the user-readable explanation.
- Floppy D summarizes the current map and avoids duplicating the entire roadmap.
- Floppy E remains the only execution authorization.

## Current project state

- Project type: [new, existing, inherited, partially built, or recovery]
- Repository: [verify during onboarding]
- Development environment: [verify during onboarding]
- Production or distribution environment: [verify when relevant]
- Last accepted section: none
- Current authorized section: none
- Next proposed section: none

## Major systems and boundaries

[Identify architecture, data stores, external services, production boundaries, and explicit identity exceptions during onboarding.]

## Section summary

No roadmap sections have been accepted yet.

<!-- Section summary template
## Section 01 — Name
Status:
User-visible outcome:
Dependencies:
Acceptance evidence:
Safety boundary:
Next required decision:
-->

## Required section contract

Every roadmap section must define:

- Purpose and user-visible outcome
- Dependencies and required starting evidence
- Permitted and prohibited actions
- Files, systems, and services in and out of scope
- Deliverables
- Automated and manual validation
- Safety controls and stop conditions
- Recovery or safe-abort path
- Required user decisions
- Testable acceptance criteria
- Closeout artifacts
- Inactive next-section draft requirement

## Deferred backlog

[Record useful future ideas that are not part of the accepted current roadmap.]

## Explicitly out of scope

[Define boundaries during onboarding.]

## Scope-growth rule

A proposed feature, issue, cleanup, migration, or adjacent improvement becomes active work only when:

1. It is accepted into the roadmap or an approved roadmap revision.
2. Its dependencies are satisfied.
3. It is placed into the active Floppy E.
4. The user explicitly authorizes that Floppy E work package.

Visibility is not authorization. Roadmap acceptance is not implementation authorization.
