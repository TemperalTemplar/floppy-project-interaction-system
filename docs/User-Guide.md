# User Guide

## Start here

You do not need to understand Floppies A-E, BCE lifecycle states, work packages, or the internal governance model before using Floppy.

For a first experience, open a new ChatGPT conversation, paste the prompt below, and then describe your project in ordinary language. Floppy should determine the correct starting route from what you tell it and from any repository evidence it can inspect.

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

If Floppy has not yet been initialized for the project, guide me through the required repository and `.floppy` initialization without beginning implementation.

When the project is ready for formal onboarding, load the canonical Floppy 1E onboarding controller and use it to establish the project outcome, verified starting state, requirements and constraints, assumptions and unknowns, bounded roadmap, acceptance criteria, deferred or excluded work, and first proposed work section.

Ask questions in ordinary language. Explain Floppy concepts only when I need them to make a decision. Recommend routine technical choices instead of making me design every implementation detail.

Do not treat my desire to build something as authorization to modify the project. Do not begin implementation during onboarding. Preserve existing valid work if this is an established project.

When onboarding is complete, explain in plain language:
1. what Floppy learned about my project;
2. what roadmap it created;
3. what the first proposed work section is;
4. what requires my approval; and
5. exactly what I should do next.

From that point forward, use the Floppy Project Interaction System as the governing project-control and continuity system for this project.
```

## How Floppy chooses the starting route

A first-time user should not have to choose the internal Floppy mode manually.

### I only have an idea

Describe the project naturally. Floppy can help clarify the intended outcome, major constraints, and what repository needs to exist. Formal Floppy onboarding begins only after there is a project location that can own the project-specific `.floppy/` control state.

### I already have a project or repository

If the model can access the repository, it should inspect existing evidence before asking questions. The existing project is not to be redesigned merely because Floppy is being adopted.

If the project does not yet contain `.floppy/`, provision the initial control state and then continue into Floppy 1E onboarding.

### My project already contains `.floppy/`

Do not restart onboarding by default. Read `.floppy/manifest.json` first, follow its `required_read_order`, reconstruct the accepted lifecycle and authority state, and continue from the next legal operation.

## What the system does

The Floppy system keeps AI-assisted project work organized across conversations by separating five kinds of information: Human-in-the-Loop rules, development issues, accepted project state, the roadmap, and the current authorized section.

A BCE - Bootable Context Environment - allows a fresh model or conversation to reconstruct the project's accepted operating context from repository state rather than depending on old chat memory.

## Source versus project repositories

The Floppy source repository provides the method and a clean project seed. Each adopting project keeps its own `.floppy/` directory in the same repository as the project's code. Project sessions read the Floppy source as canonical read-only infrastructure but write project-specific state only to the adopting project repository.

## Provision the initial control state

For an existing local project repository that has not yet adopted Floppy, run a dry run before creating its `.floppy` directory:

```bash
python tools/floppyctl.py initialize --target /path/to/project --project-name "Project Name" --source-repository https://github.com/TemperalTemplar/floppy-project-interaction-system --dry-run
```

Run the same command without `--dry-run` to provision the project.

The operation creates the entire `.floppy` directory only when no `.floppy` directory already exists. It records a canonical `lifecycle-state.json`, a checkpoint-bound `orchestrator-registry.json`, and the matching manifest projection. The initial state is onboarding-only and grants no implementation authority or repository writer.

Provisioning is deterministic for the same project path, project name, source version, source repository identity, and Git checkpoint. A failure removes the staging directory and any newly installed `.floppy` tree, so the project is not left partially initialized. Symlinks, reparse points, path escapes, stale stage paths, and overwrite attempts are stop conditions.

After provisioning, validate the project:

```bash
python tools/floppyctl.py --root /path/to/project validate --mode project
```

A successful initialization still does not authorize implementation. Continue with Floppy 1E onboarding and obtain the required administrator decisions for the first work package and section activation.

## New-project onboarding

Floppy 1E guides the model and administrator through:

1. project identity and observable final outcome;
2. verified starting state, assumptions, unknowns, and constraints;
3. a bounded section roadmap with dependencies and testable acceptance evidence;
4. the first proposed work section;
5. deferred, excluded, and rejected work; and
6. the exact decisions requiring administrator approval.

Roadmap acceptance does not authorize implementation. The first work section starts only after separate explicit authorization through Floppy E.

## Future conversations

Once the project already contains a valid `.floppy/` environment, a new conversation can start with a much shorter prompt:

```text
Use the Floppy Project Interaction System from:
https://github.com/TemperalTemplar/floppy-project-interaction-system

Use release/tag v1.0.0.

My project repository is:
[PROJECT REPOSITORY]

Read the project's `.floppy/manifest.json` first, follow its required read order, reconstruct the accepted project state, and continue from the next legal Floppy action.

Do not restart the project, redesign completed accepted work, or infer implementation authority from my request to continue.
```

The point of the BCE model is that the conversation can be new while the project context remains recoverable from the repository.

## Coordinator conversations

When a project uses Floppy Z, the coordinator reads accepted project state and tells the administrator which model or existing project conversation is responsible for the next action, what instruction to give it, what result it should return, and how to verify that result.

Coordinator status does not itself grant repository write authority.

## Existing project session

1. Give the model the continuation instruction from `BOOTSTRAP.md` or the shorter prompt above.
2. Review its readiness report.
3. Authorize the current section only when you intend implementation to begin.
4. Keep future ideas in Floppy D and unrelated defects in Floppy B.
5. Request closeout when the session should end.

## Closeout

Closeout does not rebuild the five Floppies. It produces a compact handoff and a revision packet describing only what changed. Floppy A remains sealed. Floppy C changes only after acceptance. Floppy E is replaced only for a newly authorized section.

## Applying revisions

Review the packet first. After acceptance, allow the model or administrator to apply only the listed changes to the project-owned Floppies. Git history then records the exact control-state change.

## Authority in plain language

Floppy deliberately separates intent from authority.

Wanting something built does not by itself authorize repository changes. Accepting a roadmap does not authorize implementation. Completing implementation does not create administrator acceptance. Accepting a section does not automatically authorize the next one.

The model should explain these boundaries when they matter, but a first-time user should not need to memorize the lifecycle vocabulary before beginning.

## Safety

Do not store passwords, tokens, private keys, recovery codes, or secret values in Floppies. Record only a credential's name, role, owner, storage location, consumer relationship, and authorization status.

<!-- V2_02_USER_ONBOARDING_BEGIN -->
## Provider-independent first use

The maintained Getting Started guides are under `docs/getting-started/`. All providers share one canonical starter prompt. Provider brand never selects Class A/B/C; the four actual session capabilities do. Route B preserves existing non-Floppy projects before adoption, while Route C resumes an existing Floppy project from its accepted control state.

<!-- V2_02_USER_ONBOARDING_END -->

<!-- V2_05_OPP_USER_GUIDE_BEGIN -->
## Using the Official Project Plan

Review the OPP candidate before acceptance. No project UUID or accepted OPP exists during candidate review. After explicit acceptance, use the active OPP aliases as the current planning baseline and keep immutable history. If accepted-state and OPP revisions disagree, stop rather than guessing. Continue to obtain separate authorization before implementation, migration, integration, tag, or release.
<!-- V2_05_OPP_USER_GUIDE_END -->
