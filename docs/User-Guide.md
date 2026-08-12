# User Guide

## Start here

You do not need to understand BCE, lifecycle states, Floppies A-E, work packages, the Continuity Overseer, Project Orchestrators, or succession before using Floppy.

For a first experience, use stable release/tag `v2.0.0`, open a new AI conversation, and describe your project in ordinary language.

Recommended starter prompt:

```text
I want to use the Floppy Project Interaction System to manage this project.

Canonical Floppy source:
https://github.com/TemperalTemplar/floppy-project-interaction-system

Use stable release/tag:
v2.0.0

Begin by reading `BOOTSTRAP.md`, `system-manifest.json`, and `docs/getting-started/README.md` from the Floppy source repository. Treat that repository as canonical read-only Floppy source.

I am a new Floppy user. Let me describe my project naturally. Determine whether I have only an idea, an existing project that has not adopted Floppy, or an existing project that already contains `.floppy` state.

Inspect repository evidence before asking questions the repository can already answer. Preserve existing accepted work. Do not treat my request to build or continue as implementation authority.

When formal onboarding is required, use Floppy 1E. When the V2 accepted project origin and Official Project Plan continuity are established, provide the paired Continuity Overseer and initial Project Orchestrator bootstrap for separate conversations bound to the same accepted checkpoint and authority state.
```

## What changed in V2

V2 introduces a persistent continuity layer around active project coordination.

The normal V2 role model is:

```text
Administrator / Project Authority
            |
            v
       Floppy 1E
project definition + roadmap
            |
            v
Accepted Project State + Official Project Plan
            |
            +-----------------------------+
            |                             |
            v                             v
  Continuity Overseer              Project Orchestrator
 persistent check valve              (Floppy Z)
                                          |
                                          v
                                  Section Working Model
```

The important point is that the **Continuity Overseer and Project Orchestrator are different conversations with different jobs**.

## The V2 roles in plain language

### Administrator / Project Authority

The human administrator remains the project authority. Floppy does not replace human acceptance or turn role assignment into implementation permission.

### Floppy 1E

Floppy 1E is used to define or formally onboard the project. It helps establish the desired outcome, evidence-backed starting state, constraints, roadmap, acceptance criteria, deferred work, and first proposed work package.

It does not authorize implementation.

### Continuity Overseer

The Continuity Overseer is the project's long-lived check valve.

Its job is to preserve accepted continuity across Project Orchestrator lifetimes. It verifies repository-backed accepted state, the current planning baseline, succession evidence, and authority state. It can surface stale handoffs or material scope drift.

It does not normally implement work, become repository writer, replace the Project Orchestrator, or silently change accepted project state.

### Project Orchestrator — Floppy Z

The Project Orchestrator is the active coordination conversation.

It reconstructs the current accepted project state, determines the next lawful operation, directs the responsible Section Working Model, and maintains the handoff between project authority and implementation.

The Project Orchestrator is not automatically the implementation model and does not gain writer authority merely because it coordinates the work.

### Section Working Model

The Section Working Model performs the currently authorized implementation or verification work.

Its authority comes from repository-backed lifecycle/work-authorization state. A roadmap, an Overseer message, an Orchestrator message, or a request from the user does not substitute for the required authorization.

## Accepted project state and Official Project Plan

V2 provides repository-backed continuity for accepted project origin and the Official Project Plan (OPP).

The OPP candidate must be reviewed and explicitly accepted before it becomes the accepted planning baseline. When the V2 accepted-origin transaction is established, the project identity, accepted-state record, OPP, Continuity Overseer identity, and initial Project Orchestrator identity are linked.

If the accepted-state and OPP revisions disagree, Floppy should stop instead of guessing which one is current.

## The paired V2 bootstrap

After the accepted origin required by V2 has been established, Floppy renders two prompts from the same exact repository checkpoint and authority state:

1. **Continuity Overseer prompt**
2. **Initial Project Orchestrator prompt**

Use them in two separate conversations.

```text
Conversation A
Continuity Overseer

Conversation B
Project Orchestrator
```

The two roles share the same accepted origin but do not share the same function.

Creating those conversations does not authorize implementation and does not create a repository writer.

## How Floppy chooses the starting route

A first-time user should not have to select an internal Floppy mode manually.

### I only have an idea

Describe the project naturally. Floppy can help clarify the outcome and establish the repository/working location needed to own project-specific `.floppy/` state.

Formal repository-backed onboarding begins only when there is a project location capable of owning that state.

### I already have a project or repository

If the AI can access the repository, it should inspect the existing project before asking questions the repository can already answer.

Do not redesign the project merely because Floppy is being adopted.

If `.floppy/` does not yet exist, provision the initial control state and continue with Floppy 1E onboarding.

### My project already contains `.floppy/`

Do not restart onboarding by default.

Read `.floppy/manifest.json` first and follow its required read order. Reconstruct the accepted lifecycle and authority state, accepted-state/OPP continuity when registered, Continuity Overseer state, Project Orchestrator registry/succession state, and exact checkpoint.

Continue from the next lawful operation.

## Provision the initial control state

For an existing local project that has not adopted Floppy, run a dry run first:

```bash
python tools/floppyctl.py initialize \
  --target /path/to/project \
  --project-name "Project Name" \
  --source-repository https://github.com/TemperalTemplar/floppy-project-interaction-system \
  --dry-run
```

Run the same command without `--dry-run` to provision the project.

The initializer creates the project-owned `.floppy/` control tree only when one does not already exist. Initial control-state provisioning grants no implementation authority.

After provisioning, validate the project:

```bash
python tools/floppyctl.py --root /path/to/project validate --mode project
```

Then continue into Floppy 1E onboarding.

## New-project onboarding

Floppy 1E guides the administrator and model through:

1. project identity and observable final outcome;
2. verified starting state;
3. assumptions, unknowns, and constraints;
4. bounded work-package/section roadmap;
5. dependencies and testable acceptance evidence;
6. first proposed work package;
7. deferred, excluded, and rejected work;
8. exact administrator decisions required.

Roadmap or Official Project Plan acceptance does not authorize implementation.

## Starting the Continuity Overseer conversation

Use the paired prompt generated from the accepted project origin. The Continuity Overseer should load `orchestrator/Continuity_Overseer.md` from the pinned Floppy source.

At startup it reconstructs the project using repository-backed state rather than relying on prior chat memory. It checks accepted-state, OPP linkage when registered, continuity state, Project Orchestrator registry, lifecycle/authority state, succession evidence, and exact checkpoint.

Its normal output is a continuity report: current accepted checkpoint, current Project Orchestrator, authority fingerprint, succession status, and any stop condition.

## Starting the Project Orchestrator conversation

Use the paired Project Orchestrator prompt generated from the same accepted project origin. The Project Orchestrator loads `orchestrator/Floppy_Z.md`.

It should reconstruct the current project and tell the administrator/Section Working Model what the next lawful action is. It should identify:

- current accepted checkpoint;
- active work package;
- lifecycle/authority state;
- current Section Working Model;
- repository writer;
- expected evidence;
- next required administrator decision.

The Project Orchestrator coordinates; it does not silently implement merely because it has enough context to do so.

## Starting a Section Working Model

A Section Working Model is used for the actual authorized work.

Before changing the repository, it must reconstruct the exact active authorization, including branch/worktree/checkpoint, file scope, required validation, writer assignment, and prohibited side effects.

It performs only that bounded work and returns exact evidence to the Project Orchestrator and administrator.

## Project Orchestrator succession

The Continuity Overseer is designed to remain available when the Project Orchestrator conversation eventually becomes too long, unavailable, or needs replacement.

Succession uses `protocols/06-orchestrator-succession.md`.

The handoff binds the replacement to the current repository-backed authority fingerprint. If authority changes after the handoff was prepared, the stale handoff must not be applied.

The stop condition is:

```text
STALE_SUCCESSION_HANDOFF
```

The Continuity Overseer verifies the succession boundary and helps ensure the new Project Orchestrator starts from the correct accepted state rather than reconstructing the project from old conversation memory.

## Continuing an existing V2 project

For an existing V2 project, a new conversation can begin with:

```text
Use the Floppy Project Interaction System from:
https://github.com/TemperalTemplar/floppy-project-interaction-system

Use release/tag v2.0.0.

My project repository is:
[PROJECT REPOSITORY]

Read `.floppy/manifest.json` first and follow its required read order. Reconstruct accepted project state, Official Project Plan linkage when registered, Continuity Overseer state, Project Orchestrator registry/succession state, lifecycle authority, current work package, current Section Working Model, repository writer, and exact checkpoint.

Continue only from the next lawful operation. Do not restart the project, redesign accepted work, infer authority from my request to continue, or collapse the Continuity Overseer, Project Orchestrator, and Section Working Model roles.
```

For a V2 project that already has its paired roles established, normally resume the existing Continuity Overseer and Project Orchestrator conversations rather than creating unnecessary replacements.

## Closeout

Implementation completion, verification, administrator acceptance, section closeout, and final project closure remain separate lifecycle operations.

A Section Working Model returns completion/verification evidence. The Project Orchestrator coordinates the next lawful lifecycle action. The Continuity Overseer preserves continuity across the larger project and succession boundary.

Closeout does not authorize the next work package automatically.

## Authority in plain language

Floppy deliberately separates intent from authority.

None of these alone authorizes implementation:

- wanting something built;
- accepting a roadmap or OPP;
- creating a Continuity Overseer conversation;
- creating a Project Orchestrator conversation;
- an Orchestrator directive;
- a draft work package;
- a completion report;
- a succession handoff;
- remembered conversation history.

Repository-backed accepted lifecycle/work authorization remains controlling.

## Source versus project repositories

The Floppy source repository contains the canonical method, controllers, protocols, schemas, and tooling.

Each adopting project stores its project-specific `.floppy/` records in the project's own repository. Normal project sessions must not write project-specific state into the Floppy source repository.

## Version and integrity

Use stable release/tag `v2.0.0` for the immutable V2 release source.

Canonical role controllers should be pinned to a version/tag/commit and verified against `system-manifest.json` where a digest is registered. If the content does not match the pinned source, stop instead of silently accepting the altered controller.

Post-release documentation corrections may appear on `main`; they do not rewrite the immutable `v2.0.0` release tag.

## Safety

Do not store passwords, tokens, private keys, recovery codes, or other secret values in Floppy records. Store only the non-secret metadata needed to identify the credential's role, owner, storage location, consumer relationship, and authorization status.
