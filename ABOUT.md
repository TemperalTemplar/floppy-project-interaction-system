# About the Floppy Project Interaction System

## Overview

The **Floppy Project Interaction System** is a reusable Human-in-the-Loop project-control system for AI-assisted work.

It was created to let a fresh AI conversation reconstruct a project's accepted knowledge, operating rules, roadmap, current authority, evidence, and continuation point without depending on the memory of an earlier conversation.

The system uses small, purpose-specific files called **Floppies**. The name comes from the operating discipline of earlier computing: limited working space, explicit load order, one task at a time, controlled inputs and outputs, operator approval, and durable state stored outside the processor.

The files do not need to live on physical 1.44 MB disks. In normal use, the canonical system and each project's state are stored in Git repositories. GitHub provides version history, commit identity, branch isolation, reviewable differences, and repeatable retrieval.

The result is a practical form of external, versioned context memory for AI-assisted projects.

---

## Why the system was created

Current AI models can reason across large amounts of information, but a long conversation is not automatically a reliable project record.

Conversations commonly contain:

- Repeated information
- Temporary reasoning
- Superseded plans
- Incorrect assumptions
- Abandoned ideas
- Unaccepted changes
- Stale instructions
- Missing acceptance boundaries
- Unclear authority to act
- Important facts buried inside thousands of messages

A new conversation may not know which information is current, which work was accepted, which files are authoritative, what remains unresolved, or whether it is permitted to act.

The Floppy Project Interaction System was created to separate durable project state from temporary conversation state.

Instead of asking an AI instance to remember an entire project conversation, the system gives it a controlled context package containing only the information needed to operate safely and continue efficiently.

---

## The problem it solves

The central problem is not simply lack of memory. It is lack of **controlled, repeatable project context**.

Without a structured external context system, an AI-assisted project may suffer from:

- Scope expansion without user approval
- Repeated rediscovery of already known facts
- Different conversations interpreting the project differently
- Accepted work being confused with proposed work
- Roadmap visibility being mistaken for authorization
- Models continuing into the next phase without approval
- Repository changes being made from stale assumptions
- Destructive commands being suggested without sufficient inspection
- Closeouts that record completion but do not prepare the next usable work package
- Users being forced to translate goals into implementation details themselves
- A project becoming dependent on one long conversation that cannot be reliably reproduced

The Floppy system addresses these failures by giving the AI a defined boot process, authority hierarchy, project map, accepted baseline, issue register, current work authorization, and closeout procedure.

---

## Bootable Context Environment

The larger architectural concept behind the system is the **BCE — Bootable Context Environment**.

A Bootable Context Environment is:

> A versioned, externally stored context package that allows a new AI instance to reconstruct a project's accepted knowledge, operating rules, current authority, and exact continuation state without relying on prior conversation memory.

A BCE does not preserve the original AI instance. It preserves enough controlled state to reproduce the instance's useful project understanding and operating behavior.

The boot sequence is conceptually:

```text
Fresh AI instance
        ↓
Read the BCE manifest
        ↓
Load canonical system controls
        ↓
Load project-specific Floppies
        ↓
Reconstruct accepted state
        ↓
Identify current authorization
        ↓
Inspect only the evidence required now
        ↓
Resume from the controlled continuation point
```

The BCE is repeatable because the same versioned files, load order, integrity information, and accepted checkpoints can be supplied to another compatible AI instance.

The BCE is inspectable because the context is stored as ordinary Markdown, text, and JSON rather than hidden inside a private model state.

The BCE is controllable because the user remains the authority and project execution is limited by the active authorization file.

---

## The relationship between the BCE and the Floppy system

The **BCE** is the architectural concept.

The **Floppy Project Interaction System** is a project-control implementation of that concept.

```text
BCE
└── Reproducible external AI context architecture

Floppy Project Interaction System
├── Canonical source-system controls
├── Project-owned Floppies A–E
├── Project roadmap
├── Manifest and load order
├── Revisions and closeouts
├── Evidence and handoffs
└── Human authorization gates
```

A project using the Floppy system has its own BCE stored in its repository. The canonical source repository supplies the method and read-only controllers; the project repository supplies the project's current state.

---

## Repository model

The system deliberately separates two kinds of repositories.

### 1. Canonical Floppy source repository

The source repository contains:

- The system method
- Canonical protocols
- Canonical Floppy 1E
- Canonical Floppy Z
- Bootstrap instructions
- Project seed files
- Initialization and validation tooling
- Schemas and documentation

This repository is read-only during normal project work.

Project-specific facts, credentials, code, evidence, closeouts, and active Floppies must not be written back into the source repository.

### 2. Project repository

Each adopting project contains its own `.floppy/` directory alongside the project code.

The project repository owns:

- Its Floppies A–E
- Its accepted roadmap
- Its project definition
- Its issue records
- Its accepted baseline
- Its current authorization
- Its revisions
- Its closeouts
- Its evidence
- Its handoffs
- Its inactive next-section work package

This separation prevents one project's state from modifying the canonical system or leaking into another project.

---

## How the AI interacts with the repositories

The AI does not treat every file in every repository as equally authoritative.

It first reads the project manifest, which identifies:

- The source-system version or commit
- Required file locations
- Required load order
- Current lifecycle state
- Current authorization state
- Roadmap paths
- Controller provenance
- Last accepted revision or handoff

The AI then loads only the files needed for the current task.

During normal operation:

```text
Canonical source repository
→ supplies read-only system behavior

Project repository
→ supplies project-specific state

AI conversation
→ temporarily interprets and applies that state

User
→ approves roadmap, scope, execution, acceptance, and transitions
```

The conversation is temporary. The accepted project state remains in the repository.

When the conversation ends, a later conversation can reconstruct the state from the repository rather than relying on a summary copied from memory.

---

## The project Floppies

The project-owned state is divided into five principal Floppies.

### Floppy A — Human-in-the-Loop rules

Floppy A records durable interaction and safety requirements, including:

- User authority
- Communication expectations
- Approval gates
- Evidence requirements
- Repository safety
- Production safety
- Secret-handling boundaries
- Completion and acceptance rules

Floppy A is normally created and sealed during onboarding. It should not be casually rewritten during ordinary project work.

### Floppy B — Development issues

Floppy B records unresolved obligations, defects, risks, limitations, and deferred work.

Items in Floppy B are visible but not automatically authorized.

Each issue should have a stable identity, evidence, impact, status, and relationship to the roadmap.

### Floppy C — Accepted project baseline

Floppy C records what is verified, working, and explicitly accepted.

It protects completed work from being repeatedly redesigned or treated as unfinished.

A proposal does not enter Floppy C until the user accepts it or it is otherwise established as verified baseline evidence.

### Floppy D — Project map and roadmap state

Floppy D records the project structure, major components, environments, dependencies, section status, roadmap relationships, and important boundaries.

It gives a model a navigational map without forcing every conversation to inspect the entire repository.

### Floppy E — Current execution authorization

Floppy E controls what may be done now.

It contains either:

```text
NO_ACTIVE_WORK_AUTHORIZATION
```

or exactly one explicitly authorized work section.

Floppy E is the execution gate. A roadmap, backlog, issue, future template, or model recommendation does not authorize work.

---

## Canonical source-system controllers

Two additional controls support the project Floppies but are not themselves project-state Floppies.

### Floppy 1E — Initial project definition and roadmap builder

Floppy 1E is used when a project first adopts the system or undergoes explicit controlled re-onboarding.

It helps the user and AI:

- Define the observable project outcome
- Inspect and classify the starting evidence
- Establish constraints and non-goals
- Separate requirements, defects, ideas, and implementation detail
- Divide the project into bounded sections
- Order section dependencies
- Define testable acceptance evidence
- Prepare the first inactive work package
- Create or finalize the initial Floppies A–E

Floppy 1E does not authorize implementation.

Its normal sequence is:

```text
DISCOVER
→ DEFINE
→ BOUND
→ DECOMPOSE
→ SEQUENCE
→ VERIFY
→ PRESENT
→ ACCEPT
→ HAND OFF
```

### Floppy Z — Project-model orchestrator

Floppy Z is used when one conversation must understand the project and tell another active project conversation what to do.

It:

- Reads the system and project Floppies
- Reconstructs accepted state
- Identifies the responsible model or conversation
- Creates the exact instruction the user should provide
- Explains the expected result and acceptance check

By default, Floppy Z coordinates; it does not perform repository writes or project implementation itself.

This prevents the coordinator from silently replacing the project model.

---

## Roadmap concept

The roadmap is not merely a feature list. It is a sequence of acceptance-bounded work packages.

Every section should define:

- Purpose
- User-visible outcome
- Dependencies
- Required starting evidence
- Permitted actions
- Prohibited actions
- Files, systems, or services in scope
- Files, systems, or services out of scope
- Deliverables
- Automated validation
- Manual validation
- Acceptance criteria
- Safety controls
- Stop conditions
- Recovery or safe-abort path
- Required user decisions
- Closeout artifacts
- Next-section draft requirement

This structure helps the user understand what is being accomplished while giving the AI enough detail to implement safely.

The roadmap keeps future work visible without making it active.

---

## How the system is applied to a project

### Phase 1 — Initialize

The project seed creates the initial `.floppy/` structure in the project repository.

Initialization does not authorize code changes.

### Phase 2 — Build the initial BCE

Floppy 1E guides the AI and user through project definition, evidence inspection, roadmap creation, and initial Floppy construction.

The result is the first accepted project BCE.

### Phase 3 — Authorize one section

The user reviews the proposed work package.

Only after explicit approval is that section placed into active Floppy E.

### Phase 4 — Implement

The active project model:

- Verifies repository and worktree state
- Reads the authorized scope
- Makes the smallest required changes
- Runs defined tests
- Preserves unrelated work
- Reports evidence and blockers
- Stops at authorization boundaries

### Phase 5 — Accept and close

The user accepts the completed section only after the required evidence is available.

Closeout then:

- Records the accepted result
- Updates the accepted baseline
- Updates the project map and issues where needed
- Closes active authorization
- Creates the next work package as an inactive draft
- Records the exact continuation state

Closeout does not automatically begin the next section.

### Phase 6 — Reboot in a new conversation

A new AI instance reads the manifest and required Floppies, reconstructs the accepted state, identifies the current authorization, and continues from the recorded checkpoint.

This is the BCE boot process in practice.

---

## Append-only context and revisions

The system favors small accepted revisions rather than constant wholesale rewriting.

Conceptually:

```text
Accepted base state
+ accepted revision
+ accepted revision
+ current authorization
= reproducible current context
```

Git provides commit history and diffs. The Floppy files provide semantic meaning: what changed, why it changed, whether it was accepted, and what may happen next.

This makes the context both machine-readable and reviewable by the user.

---

## Human-in-the-Loop design

The user is not expected to become the programmer in order to use the system.

The AI should resolve routine implementation choices, inspect available evidence before asking questions, recommend the safest approach, and request user decisions only when they materially affect:

- Project purpose
- Scope
- Architecture
- Security
- Cost
- Production behavior
- Credentials
- Destructive operations
- Acceptance criteria
- Release or publication

The user remains responsible for acceptance and authorization. The model remains responsible for translating that authority into precise technical execution.

---

## Why the floppy metaphor matters

The metaphor is not about returning to obsolete hardware.

It represents useful operating discipline:

- Small, bounded context packages
- Explicit load order
- Known authority
- One active work package
- Durable external state
- Controlled transitions
- Operator approval
- Recoverable checkpoints
- Clear separation between system media and project data

Modern Git repositories remove the physical capacity limit while preserving the discipline.

The result combines older computing's explicit state management with current AI's ability to interpret natural language, repositories, evidence, and project requirements.

---

## What the system is not

The Floppy Project Interaction System is not:

- Permanent biological-style memory for an AI
- A replacement for source control
- A replacement for testing
- A license for autonomous production changes
- A guarantee that every model will behave identically
- A reason to store secrets in Markdown or Git
- A reason to load an entire repository into every conversation
- A system that automatically authorizes the next roadmap section

It is a controlled method for reconstructing project context, authority, and continuation.

---

## Core design principles

```text
The conversation is temporary.
The project state is durable.

The roadmap provides visibility.
Floppy E provides authority.

The source repository defines the method.
The project repository owns the project state.

The AI recommends and implements.
The user authorizes and accepts.

Closeout records completion.
It does not silently start the next section.

A fresh AI instance does not need the old conversation.
It boots the accepted context environment.
```

---

## Summary

The Floppy Project Interaction System turns a Git repository into more than a code store. It becomes a **Bootable Context Environment** for AI-assisted project work.

By combining canonical controls, project-owned state, manifests, roadmaps, explicit authorization, evidence, revisions, and closeouts, the system allows a new AI instance to reconstruct the project's working context and continue from a controlled checkpoint.

Its purpose is not to make AI unlimited. Its purpose is to make AI-assisted work more repeatable, understandable, efficient, reviewable, and safe.