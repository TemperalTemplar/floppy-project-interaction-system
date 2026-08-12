# Floppy Project Interaction System

**Latest stable release:** `v2.0.0`  
**Current `main` status:** post-V2 forward integration / pre-V3 development state  
**V3 status:** candidate planning only; not yet an accepted or released V3 product

> `main` is not identical to the immutable `v2.0.0` release. Users who need the exact released V2 source should use tag `v2.0.0`. See [`MAINLINE_STATUS.md`](MAINLINE_STATUS.md) for the repository-state boundary.

Floppy is a provider-independent AI project orchestration and continuity system that preserves accepted project state, project intent, human authority, and development history across AI sessions, model changes, and Project Orchestrator handoffs.

The source repository defines the Floppy method. An adopting project keeps its own project-specific `.floppy/` control state in that project's repository.

## How Floppy V2 works

V2 is not a single coordinator conversation. It separates project definition, long-lived continuity, active coordination, and implementation into distinct roles:

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
            |                             |
            |                             v
            |                     Section Working Model
            |                             |
            |                             v
            +------ continuity ------ Project Repository
```

### Floppy 1E — initial project definition and roadmap

`onboarding/Floppy_1E.md` is used for a new project or explicit controlled re-onboarding. It helps establish the project outcome, verified starting state, requirements, constraints, bounded roadmap, acceptance criteria, deferred work, and first proposed work package.

Floppy 1E does not authorize implementation.

### Accepted state and Official Project Plan

V2 protects accepted project origin and planning state in repository-backed records. When the V2 accepted-origin transaction is established, accepted state, the Official Project Plan, the Continuity Overseer identity, and the initial Project Orchestrator identity are linked to the same project origin.

The Official Project Plan is the accepted planning baseline. A candidate plan is not accepted merely because it was generated. Accepted-state or OPP conflicts are stop conditions rather than permission to reconstruct or guess.

### Continuity Overseer — persistent project continuity

`orchestrator/Continuity_Overseer.md` defines the project-level continuity/check-valve role.

The Continuity Overseer:

- persists across Project Orchestrator lifetimes;
- reconstructs and verifies accepted project state;
- checks continuity and succession evidence;
- surfaces stale handoffs and scope drift;
- verifies that a replacement Project Orchestrator begins from the correct checkpoint and authority state.

The Continuity Overseer does **not** implement project work, become the repository writer by role, silently revise accepted state, or automatically transfer authority.

### Project Orchestrator — active project coordination

`orchestrator/Floppy_Z.md` is the V2 Project Orchestrator role.

The Project Orchestrator reconstructs current project state, determines the next lawful operation, coordinates the responsible Section Working Model, and maintains the handoff/authority boundary. By default it does not silently become the implementation model merely because it can describe the work.

Only one Project Orchestrator may be active at a time.

### Section Working Model — authorized implementation

The Section Working Model performs the currently authorized implementation and verification work. Its authority comes from the project's accepted lifecycle/work-authorization records, not from its role name, a roadmap position, an Overseer instruction, or an Orchestrator instruction by itself.

## Paired V2 bootstrap

After the required accepted project origin exists, V2 renders the **Continuity Overseer** and **initial Project Orchestrator** prompts from the same exact repository checkpoint and authority state.

They are presented together but used as **separate conversations**:

```text
Conversation 1: Continuity Overseer
Conversation 2: Project Orchestrator
```

Floppy does not automatically create either conversation. Creating or activating either role grants no implementation authority and no repository-writer status.

Project Orchestrator replacement is governed by `protocols/06-orchestrator-succession.md`. The Continuity Overseer verifies the succession boundary and rejects stale authority fingerprints instead of reconstructing authority from conversation memory.

## New to Floppy? Start here

You do not need to understand BCE, lifecycle states, Floppies A-E, work packages, the Continuity Overseer, or Project Orchestrator succession before starting.

Use the stable release/tag `v2.0.0` and begin with the provider-independent Getting Started guide:

[`docs/getting-started/README.md`](docs/getting-started/README.md)

A simple starter prompt is:

```text
I want to use the Floppy Project Interaction System to manage this project.

Canonical Floppy source:
https://github.com/TemperalTemplar/floppy-project-interaction-system

Use stable release/tag:
v2.0.0

Begin by reading `BOOTSTRAP.md`, `system-manifest.json`, and `docs/getting-started/README.md` from the Floppy source repository. Treat that repository as canonical read-only Floppy source.

I am a new Floppy user. Let me describe my project naturally. Determine whether I have only an idea, an existing non-Floppy project, or an existing project that already contains `.floppy` state.

Inspect repository evidence before asking questions the repository can already answer. Preserve existing accepted work. Do not treat my request to build or continue as implementation authority.

When onboarding is required, use Floppy 1E. When V2 accepted project origin and Official Project Plan continuity are established, explain and provide the paired Continuity Overseer and Project Orchestrator bootstrap for separate conversations. Do not collapse those roles into one conversation.
```

For the complete first-use and continuation procedures, read [`docs/User-Guide.md`](docs/User-Guide.md) and [`BOOTSTRAP.md`](BOOTSTRAP.md).

## Starting routes

Floppy chooses the route from actual project evidence and session capabilities rather than provider brand.

### New idea / no project repository

Clarify the project and establish a repository or working location capable of owning project-specific `.floppy/` state. Formal repository-backed onboarding begins only when such a project location exists.

### Existing project without Floppy

Inspect the project first, preserve valid existing work, provision the initial `.floppy/` control state, then use Floppy 1E for formal onboarding.

### Existing Floppy project

Do not restart onboarding by default. Read `.floppy/manifest.json` first, follow its required read order, reconstruct accepted lifecycle/authority/accepted-state/OPP/continuity state, and continue from the next legal operation.

## Project Orchestrator succession

The Continuity Overseer is deliberately longer-lived than an individual Project Orchestrator conversation.

When a Project Orchestrator is replaced:

```text
Current accepted repository state
            |
            v
Continuity Overseer verification
            |
            v
Succession handoff + authority fingerprint
            |
            v
New Project Orchestrator
```

The new Project Orchestrator must inherit the exact accepted checkpoint and authority state. Conversation age, missing chat history, or model replacement is not authority to reconstruct accepted work.

## Core authority rule

Floppy separates intent, planning, authority, implementation, verification, acceptance, closeout, migration, integration, and release.

In particular:

- accepting a roadmap or Official Project Plan does not authorize implementation;
- activating the Continuity Overseer does not authorize implementation;
- activating a Project Orchestrator does not make it repository writer;
- a draft work package does not authorize work;
- implementation completion does not create verification or administrator acceptance;
- section acceptance does not automatically authorize the next section;
- a succession handoff does not silently transfer stale authority;
- final-closure proposal and final-closure application remain distinct operations.

Project authority remains Human-in-the-Loop.

## Repository model

```text
Floppy source repository
  canonical method
  onboarding controller
  Continuity Overseer role
  Project Orchestrator role
  protocols
  schemas
  tools
  project seed

Adopting project repository
  project code
  .floppy/ accepted project state
  .floppy/ Official Project Plan records
  .floppy/ lifecycle and authorization state
  .floppy/ Continuity Overseer state
  .floppy/ Project Orchestrator registry
  .floppy/ handoffs, evidence, revisions, closeouts
```

Normal project work must not write project-specific state back into this source repository.

## Repository layout

```text
MAINLINE_STATUS.md                Released-version versus forward-main boundary
ABOUT.md                          Conceptual overview and BCE architecture
BOOTSTRAP.md                      V2 role bootstrap and startup instructions
system-manifest.json              Machine-readable source map and controller digests
docs/getting-started/             Provider-independent first-use guidance
docs/User-Guide.md                Human-facing V2 operating guide
docs/v3/                          Candidate V3 planning material; not accepted V3 by presence alone
onboarding/Floppy_1E.md           Initial project definition and roadmap controller
orchestrator/Continuity_Overseer.md
                                   Persistent project continuity/check-valve role
orchestrator/Floppy_Z.md           Project Orchestrator protocol
protocols/06-orchestrator-succession.md
                                   Project Orchestrator succession protocol
specs/accepted-state-continuity.md
                                   Accepted-state continuity contract
specs/official-project-plan.md     Official Project Plan contract
project-seed/.floppy/              Project-owned control-state seed
analytics/github-traffic/          Repository traffic history and snapshots
schemas/                          BCE and V2 contracts
tools/                            Initialization, validation, CLI and repository-support tooling
tests/                            Repository verification suite
legacy/prototype-v0/              Preserved original prototype
```

## Initialize a project

Run a dry run first:

```bash
python tools/floppyctl.py initialize \
  --target /path/to/project \
  --project-name "Project Name" \
  --source-repository https://github.com/TemperalTemplar/floppy-project-interaction-system \
  --dry-run
```

Then run the same command without `--dry-run` to provision the project-owned `.floppy/` state.

Initialization alone does not authorize implementation.

## Release and mainline boundary

The canonical released V2 source is tag `v2.0.0` at commit:

```text
88a0fa646973c4cb8e693cc4e7c512b537825fd2
```

The GitHub release provides:

- the complete V2 source distribution;
- the deterministic validated 67-file boot package;
- SHA-256 checksums;
- release notes.

The released tag is immutable and remains the exact released V2 product.

The `main` branch is the forward integration branch. After the V2 release it may contain post-release documentation corrections, repository maintenance, legal/provenance records, analytics support, and candidate planning for a future version. Those forward changes do **not** rewrite `v2.0.0` and do **not** become a released V3 product merely by existing on `main`.

The repository's `VERSION` file remains `2.0.0` until a later accepted version transition changes it. That value identifies the latest accepted product version; it does not assert that every commit currently on `main` is byte-for-byte identical to the `v2.0.0` tag.

For the explicit branch/release interpretation, read [`MAINLINE_STATUS.md`](MAINLINE_STATUS.md).

## Version and integrity

For exact released V2 behavior, use tag `v2.0.0`. For forward development or repository maintenance, use an explicitly identified `main` checkpoint or later accepted development branch/checkpoint as applicable.

Canonical controllers should be loaded from a pinned source version, tag, or commit and verified against `system-manifest.json` where a digest is registered. A mismatch is a stop condition, not permission to silently use an altered controller.

## Safety

Do not store passwords, tokens, private keys, recovery codes, or secret values in Floppy records. Record only non-secret credential metadata required for project control.

## Licensing

Floppy Project Interaction System version 2.0.0 is licensed under the Apache License, Version 2.0 (`Apache-2.0`). The license permits use, modification, and redistribution, including commercial use, subject to its terms, and includes the Apache patent grant.

Current forward `main` remains distributed under the repository's Apache-2.0 licensing and attribution files unless a later explicit licensing decision lawfully changes future distribution terms. Existing released rights are not rewritten by forward-main documentation.

See the root [`LICENSE`](LICENSE), [`NOTICE`](NOTICE), [`AUTHORS.md`](AUTHORS.md), [`PROVENANCE.md`](PROVENANCE.md), and [`TRADEMARKS.md`](TRADEMARKS.md) for current licensing, attribution, provenance, and project-identity information.
