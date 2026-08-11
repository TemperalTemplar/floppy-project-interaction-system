# Initial Project Roadmap Onboarding

This directory contains the canonical **Floppy 1E** onboarding controller.

## Purpose

Floppy 1E helps a user and a ChatGPT instance turn a project idea or an existing codebase into:

- A verified starting baseline
- A project outcome contract
- A bounded section roadmap
- Testable acceptance criteria
- A first proposed work package
- Project-owned Floppies A–E
- Machine-readable and user-readable roadmap files

It is used before project implementation begins.

## Canonical file

```text
onboarding/Floppy_1E.md
```

Load it from a pinned version, tag, or commit of this source repository. Verify its SHA-256 digest through `system-manifest.json` when practical.

## Read-only boundary

Floppy 1E is source-system infrastructure. It is not copied and edited for each project.

During onboarding:

- Read canonical Floppy 1E from this repository.
- Write all project facts, decisions, roadmap records, and acceptance evidence into the adopting project repository.
- Do not place project information in this source repository.
- Do not modify Floppy 1E to fit one project.
- Do not treat Floppy 1E as implementation authorization.

## Project-owned outputs

An initialized project receives roadmap templates under:

```text
.floppy/roadmap/roadmap.json
.floppy/roadmap/roadmap.md
```

After the user accepts the roadmap, the onboarding model also creates:

```text
.floppy/onboarding/initial-project-definition.md
.floppy/onboarding/roadmap-acceptance.md
.floppy/templates/Floppy-E-Section-01.draft.md
```

The first-section draft remains inactive until the user explicitly authorizes it through the active project Floppy E.

## Lifecycle

```text
ONBOARDING_REQUIRED
→ DISCOVERY
→ ROADMAP_DRAFTED
→ USER_REVIEW
→ ROADMAP_ACCEPTED
→ FIRST_SECTION_DRAFT_CREATED
→ NO_ACTIVE_WORK_AUTHORIZATION
```

After acceptance, ordinary project sessions do not reload Floppy 1E. The project manifest retains its source path and digest as provenance.

Floppy 1E is loaded again only for explicit controlled re-onboarding or project redefinition.

## Starting an onboarding conversation

```text
Use the Floppy Project Interaction System from [SOURCE_REPOSITORY] at version, tag, or commit [SOURCE_VERSION_OR_COMMIT].

Load `onboarding/Floppy_1E.md` as the canonical initial-project roadmap controller. Verify its digest through `system-manifest.json` and treat the source repository as read-only.

Open [PROJECT_REPOSITORY] and inspect the available project evidence. Read the project `.floppy/manifest.json` and onboarding files. Do not modify project code or begin implementation.

Guide me through project definition and roadmap creation. Ask only questions that materially change purpose, scope, architecture, security, cost, production behavior, acceptance criteria, or section order. Recommend routine technical choices instead of forcing me to design the implementation.

Present the project outcome contract, verified starting state, assumptions, risks, bounded section roadmap, first proposed section, deferred work, and exact decisions requiring my approval.

Roadmap acceptance must not authorize implementation. After acceptance, create or finalize the project-owned Floppies and roadmap records, leave the active Floppy E closed, create the first-section package as `DRAFT_NOT_AUTHORIZED`, and stop.
```

## Relationship to Floppy Z

- **Floppy 1E** constructs the initial project definition and roadmap.
- **Floppy Z** later reads the accepted project Floppies and tells the active project model what to do next.
- **Floppy E** remains the only project execution authorization.

These roles must not be silently combined.

<!-- V2_02_USER_ONBOARDING_BEGIN -->
## Boundary with V2 user onboarding

`docs/getting-started/README.md` performs user entry, capability recording, and Route A/B/C selection. `Floppy_1E.md` remains project onboarding: it defines and bounds the project from the verified starting state. Neither user onboarding nor Floppy 1E grants implementation authority.

<!-- V2_02_USER_ONBOARDING_END -->

<!-- V2_05_OPP_ONBOARDING_BEGIN -->
## V2-05 onboarding result

The accepted onboarding result is an Official Project Plan plus accepted-state/project-origin linkage. Review candidates have no `project_id`; accepted plans do. Initial CO/Project-Orchestrator prompts are paired only after the accepted-origin transaction completes. No onboarding route grants implementation, migration, integration, tag, release, or repository-writer authority.
<!-- V2_05_OPP_ONBOARDING_END -->
