# Bootstrap Instructions

The system supports distinct conversation roles. Do not silently combine them.

## 0. First-time user entry prompt

This is the recommended public starting point for someone who has never used Floppy. The user should not need to understand BCE, Floppies A-E, lifecycle states, work packages, or authority terminology before beginning.

Open a new ChatGPT conversation, paste the prompt below, and then describe the project naturally when asked.

```text
I want to use the Floppy Project Interaction System to manage this project.

Canonical Floppy source:
https://github.com/TemperalTemplar/floppy-project-interaction-system

Use stable release/tag:
v1.0.0

Begin by reading `BOOTSTRAP.md` and `system-manifest.json` from the Floppy source repository. Treat that repository as the canonical read-only Floppy system.

I am a new Floppy user. Do not assume I understand Floppy, BCE, lifecycle states, Floppies A-E, work packages, or its internal governance terminology.

First ask me to describe the project I want to build or continue. Let me explain it naturally.

Then determine whether:
- I only have an idea and no project repository yet;
- I have an existing project or repository that has not adopted Floppy; or
- my project already contains a `.floppy` control environment.

If I provide a repository and you can access it, inspect the existing project before asking questions the repository can already answer.

If I only have an idea, help me clarify the project and establish the project repository or working location required to own Floppy state. Do not pretend formal repository-backed onboarding has already occurred.

If I have an existing repository without `.floppy`, preserve existing valid work, inspect available evidence, and guide me through Floppy initialization before formal onboarding.

If the project already contains `.floppy`, do not restart onboarding by default. Read `.floppy/manifest.json` first, follow its required read order, reconstruct accepted lifecycle and authority state, and continue from the next legal operation.

When formal onboarding is required, load `onboarding/Floppy_1E.md` as the canonical initial-project definition and roadmap controller. Use it to establish the project outcome, verified starting state, requirements and constraints, assumptions and unknowns, bounded roadmap, acceptance criteria, deferred or excluded work, and first proposed work section.

Ask questions in ordinary language. Explain Floppy concepts only when I need them to make a decision. Recommend routine technical choices instead of making me design every implementation detail.

Do not treat my desire to build something as authorization to modify the project. Do not begin implementation during onboarding. Do not invent project facts that have not been established. Preserve existing accepted work.

When onboarding is complete, explain in plain language:
1. what Floppy learned about my project;
2. what roadmap it created;
3. what the first proposed work section is;
4. what requires my approval; and
5. exactly what I should do next.

From that point forward, use the Floppy Project Interaction System as the governing project-control and continuity system for this project.
```

After the first project-owned `.floppy/` environment exists, future conversations can use the shorter continuation prompt in `docs/User-Guide.md` or the role-specific instructions below.

## 1. Floppy 1E initial-project onboarding mode

Use this when a project is adopting the system for the first time or the user explicitly orders controlled re-onboarding.

Replace the bracketed values:

```text
Use the Floppy Project Interaction System from [SOURCE_REPOSITORY] at version, tag, or commit [SOURCE_VERSION_OR_COMMIT].

Load `onboarding/Floppy_1E.md` from the source repository as the canonical initial-project definition and roadmap controller. Verify it against the Floppy 1E digest in `system-manifest.json`. Treat the source repository as read-only.

Open [PROJECT_REPOSITORY]. Read `.floppy/manifest.json`, the onboarding source controls it names, and the project files in the required order. Inspect available project evidence before asking questions.

Remain in onboarding mode. Do not modify project code, contact production, access credentials, deploy, commit implementation changes, or begin the first work section.

Guide me through:
1. Project identity and observable final outcome.
2. Verified starting state, assumptions, unknowns, and constraints.
3. A bounded section roadmap with dependencies and testable acceptance evidence.
4. The first proposed work section.
5. Deferred, excluded, and rejected work.
6. The exact decisions that require my approval.

Ask only questions that materially change purpose, scope, architecture, security, cost, production behavior, acceptance criteria, or section order. Recommend routine technical choices rather than forcing me to design the implementation.

Roadmap acceptance must not authorize implementation. After I explicitly accept the roadmap, create or finalize the project-owned Floppies and roadmap records, leave active Floppy E at NO_ACTIVE_WORK_AUTHORIZATION, create the first-section package as DRAFT_NOT_AUTHORIZED, and stop with the onboarding completion report.
```

## 2. Floppy Z coordinator mode

Use this when the administrator wants a coordinator to reconstruct accepted project state and tell the active project model what to do.

```text
Use the Floppy Project Interaction System from [SOURCE_REPOSITORY] at version, tag, or commit [SOURCE_VERSION_OR_COMMIT].

Load `orchestrator/Floppy_Z.md` from the source repository as the canonical Project Floppy coordinator. Verify it against the orchestrator digest in `system-manifest.json`. Treat the source repository as read-only.

Open [PROJECT_REPOSITORY]. Read `.floppy/manifest.json` first, then read the project files in its required order exactly as listed. Reconstruct the accepted project state, current Floppy E authorization, closeout status, and next required decision.

Remain in coordinator mode. Do not implement project work, edit either repository, create commits, perform closeouts, contact production, access credentials, or advance sections.

Tell me:
1. Which model or existing project conversation is responsible for the next action.
2. Exactly what I should paste into that project conversation.
3. What result that model should return.
4. How I can verify that it followed the Floppy system correctly.
```

Floppy Z may perform direct work only after the administrator gives an explicit, named execution override as defined in `orchestrator/Floppy_Z.md`.

## 3. Direct project-model mode

Use this only when the current conversation is intended to perform the explicitly authorized project work.

```text
Use the Floppy Project Interaction System from [SOURCE_REPOSITORY] at version [SOURCE_VERSION].

Open [PROJECT_REPOSITORY]. Read `.floppy/manifest.json` first, then read the files in its `required_read_order` exactly as listed. Treat the source repository as read-only and the project repository as the only location for project-specific Floppies, roadmap records, revisions, handoffs, and evidence.

Produce the intake readiness report required by the project protocol. Do not begin implementation, edit files, create commits, or advance sections until I explicitly authorize the current Floppy E section.

When I request closeout, load the closeout protocol named in the project manifest and produce delta revisions only. Do not recreate unchanged Floppies. Create the next section's work package only as an inactive draft unless I explicitly authorize that section.
```

## Role boundaries

- Floppy 1E creates the initial project definition and roadmap.
- Floppy Z tells the responsible project model what to do next.
- The direct project model performs the currently authorized Floppy E work.
- Project Floppy E is the only execution authorization.

The project manifest is the authority for project-file locations, onboarding state, roadmap paths, and read order. Do not scan or load the entire repository when the manifest and lifecycle state identify a smaller sufficient set.

## 4. Project orchestrator registration and handoff mode

Use this before delegating ongoing project coordination to a project
orchestrator or transferring that responsibility to another model or
conversation.

The administrator must create or load:

```text
.floppy/orchestrator-registry.json
```

Use the source template:

```text
project-seed/.floppy/orchestrator-registry.json
```

The registry must identify the current orchestrator, current section working
model or `NONE`, repository writer or `NONE`, exact repository, branch,
worktree, checkpoint, reporting relationship, and one of these administrative
statuses:

```text
ACTIVE
PAUSED
HANDOFF_PENDING
RETIRED
```

Before responsibility changes, create a handoff from:

```text
.floppy/templates/orchestrator-handoff.md
```

The handoff must preserve the exact repository checkpoint, lifecycle and
authority state, current model, writer, completed and unresolved work, next
legal operation, and prohibited operations.

At most one orchestrator may be `ACTIVE`. At most one repository writer may be
assigned. A writer requires an exact authorization reference. Orchestrator
status and role never grant write authority.

These records are administrative state, not runtime detection. Do not add
monitoring, heartbeats, automatic conversation creation, automatic authority
transfer, private-conversation inspection, or hidden-context inference.
