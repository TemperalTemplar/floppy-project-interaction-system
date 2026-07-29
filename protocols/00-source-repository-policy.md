# Source Repository Policy

## Purpose

This repository is the canonical source from which projects adopt the Floppy Project Interaction System. It is not a shared database of active projects.

It also contains the canonical Floppy Z orchestrator, which coordinates project-model instructions without becoming project state.

## Normal project use

During work on an adopting project:

- Read this repository only to obtain the system version, Floppy Z, protocols, templates, or tooling.
- Write project-specific information only inside the adopting project's repository.
- Never place a project's code, credentials, Floppies, revision packets, handoffs, evidence, or session history in this source repository.
- Never update this source repository during project intake, implementation, testing, acceptance, or closeout.
- Never treat a source-template file as the active Floppy for a project.
- Never edit canonical Floppy Z to fit an individual project.
- Never treat Floppy Z as Floppy E or as project execution authorization.

## Floppy Z orchestrator boundary

Canonical files:

```text
orchestrator/Floppy_Z.md
orchestrator/README.md
```

During normal use:

- Load Floppy Z from a pinned source version, tag, or commit.
- Verify its digest through `system-manifest.json` when practical.
- Treat the canonical file and any exact offline source mirror as read-only.
- Keep all project facts and active work authorization in the project's `.floppy/` directory.
- Use Floppy Z to prepare instructions for the active project model, not to perform that model's work by default.
- Stop and report a source-version or digest mismatch instead of silently using an altered copy.

An adopting project does not automatically receive a mutable copy of Floppy Z. Existing project repositories do not need modification to use the orchestrator.

## Deliberate system development

This source repository may be changed only when the user explicitly authorizes development of the Floppy system itself. Such changes should:

1. Preserve earlier released versions or tags.
2. Update `VERSION` and `system-manifest.json` deliberately.
3. Update the Floppy Z digest when its canonical content changes.
4. Describe migration impact on existing projects.
5. Avoid silently changing already-initialized project repositories.

Existing projects do not automatically inherit later source changes. Migration is a separate, user-authorized operation.

## Authority boundary

A model's authority to modify a project repository does not imply authority to modify this source repository. Authorization must name the source system itself when source changes are intended.

Likewise, permission to read or coordinate through Floppy Z does not grant permission to alter Floppy Z, the source repository, the project repository, or production systems.
