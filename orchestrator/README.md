# Floppy Z Orchestrator

## Purpose

Floppy Z is the canonical coordination layer for the Floppy Project Interaction System. It reconstructs a project's accepted state from its repository-backed Floppies and tells Alva exactly what to send to the active project model.

Floppy Z is not an active project Floppy and is not the project implementation model.

Its default flow is:

```text
READ → RECONSTRUCT → EVALUATE → INSTRUCT THE PROJECT MODEL
```

It must not silently become:

```text
READ → MODIFY THE PROJECT → PERFORM THE CLOSEOUT
```

## Canonical source files

```text
orchestrator/Floppy_Z.md
orchestrator/README.md
```

`orchestrator/Floppy_Z.md` is the canonical protocol. This README explains how to reproduce and use the coordinator without turning the source repository into project state.

## Source-only boundary

The repository `TemperalTemplar/floppy-project-interaction-system` is the canonical source of Floppy Z.

During normal use of an adopting project:

- Read Floppy Z from this source repository at a pinned version, tag, or commit.
- Do not edit Floppy Z for an individual project.
- Do not place project-specific facts, handoffs, evidence, or section results in this source repository.
- Do not use Floppy Z as the active project Floppy E.
- Do not copy Floppy Z into a project and then alter it to fit that project.
- Store project-specific state only in the adopting project's `.floppy/` directory.
- Treat the source repository as read-only.

Floppy Z itself may change only during explicit development of the Floppy Project Interaction System. A source change requires a deliberate version update and migration note. Existing project repositories do not inherit the change automatically.

## Why Z is separate from A–E

A–E belong to an adopting project:

- A controls Human-in-the-Loop behavior.
- B records project issues.
- C records the accepted project baseline.
- D records the project map.
- E controls current work authorization.

Z belongs to the Floppy system itself. It reads A–E and creates instructions for the correct project model. It does not become project history and does not authorize implementation.

## Coordinator and project-model separation

```text
Alva
  ↓ supplies requirements, evidence, acceptance, and authorization
Floppy Z coordinator
  ↓ produces the exact directive
Active project model
  ↓ performs authorized repository or operational work
Project repository
  ↓ stores project-specific Floppies, evidence, and closeouts
```

The coordinator must not collapse these roles.

When Alva supplies a completion report, the default interpretation is:

```text
Determine what Alva should tell the active project model next.
```

It is not:

```text
Perform the repository closeout directly.
```

## Replication procedure

To reproduce the coordinator consistently:

1. Pin the source repository to an exact version, tag, or commit.
2. Load `orchestrator/Floppy_Z.md` from that pinned source.
3. Open the adopting project repository.
4. Read the project's `.floppy/manifest.json` first.
5. Load project Floppies in the manifest's required order.
6. Keep the source repository read-only.
7. Produce a coordinator readiness report.
8. Tell Alva which project model is responsible for the next action.
9. Give Alva one complete message to paste into that project conversation.
10. State the expected result and the acceptance check.

Do not initialize or modify the project merely because the coordinator has reconstructed the state.

## Standard coordinator startup message

```text
Use Floppy Z from `TemperalTemplar/floppy-project-interaction-system` at the pinned source version or commit.

Load `orchestrator/Floppy_Z.md` as the Project Floppy coordinator. Treat the source repository as read-only.

Open the named project repository and read `.floppy/manifest.json` first. Load the project Floppies in the manifest's required order. Reconstruct the accepted state and current authorization.

Remain in coordinator mode. Do not perform project implementation, repository writes, section closeouts, GitHub changes, production actions, or credential operations.

Tell me:
1. Which model or existing project conversation is responsible for the next action.
2. Exactly what I should paste into that project conversation.
3. What result that model should return.
4. How I can verify that it followed the Floppy system correctly.
```

## Direct-execution override

Floppy Z remains coordinator-only unless Alva explicitly grants a named execution override.

Required form:

```text
Override Floppy Z coordinator mode.
Act as the active project model for [NAMED WORK PACKAGE].
Perform the authorized repository or implementation work directly.
```

The override applies only to the named work package. It does not authorize later sections, adjacent cleanup, production access, credentials, or source-system changes.

After the named work package, Floppy Z returns to coordinator mode.

## Integrity and alteration control

Canonical Floppy Z SHA-256 for source version `0.3.0-dev`:

```text
9c5cc655280da1cc6a4844941083e150b741615d5ae805878a88cddc5f30df1f
```

This digest covers `orchestrator/Floppy_Z.md` as introduced in source version `0.3.0-dev`.

A replicated coordinator should be pinned to the source version or commit. If the content differs from the pinned source, stop and report the discrepancy rather than silently using the altered copy.

Future deliberate edits must:

1. Change the source version.
2. Update the manifest.
3. Update the recorded digest.
4. Explain migration impact.
5. Preserve prior released tags or commits.

## Project adoption rule

An adopting project does not need to copy Floppy Z into `.floppy/`.

The normal model is:

```text
Source repository:
  canonical Floppy Z, protocols, templates, and tooling

Project repository:
  project-specific .floppy state
```

An offline source mirror may contain an exact unmodified copy of the whole Floppy-system source at a pinned version. That mirror remains source infrastructure and must not receive project-specific writes.

## Closeout rule

At closeout, Floppy Z tells the active project model to:

- Verify implementation and acceptance evidence.
- Update the project's B, C, D, and closed-state E as required.
- Create the formal closeout record.
- Create the next section's inactive draft work package.
- Update the project manifest.
- Commit only authorized project files.
- Stop before beginning the next section.

Floppy Z does not perform those writes by default.

## Migration impact for version 0.3.0-dev

- Existing projects remain valid and are not changed automatically.
- Existing `.floppy/` directories do not need a new project Floppy Z file.
- New and existing projects may use the coordinator by loading the canonical source file before project intake.
- Direct project-model sessions may continue to use the existing project bootstrap, but they do not receive coordinator behavior unless Floppy Z is explicitly loaded.
- No project repository should be rewritten merely to adopt this orchestrator layer.
