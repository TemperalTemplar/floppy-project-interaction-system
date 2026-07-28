# Source Repository Policy

## Purpose

This repository is the canonical source from which projects adopt the Floppy Project Interaction System. It is not a shared database of active projects.

## Normal project use

During work on an adopting project:

- Read this repository only to obtain the system version, protocols, templates, or tooling.
- Write project-specific information only inside the adopting project's repository.
- Never place a project's code, credentials, Floppies, revision packets, handoffs, evidence, or session history in this source repository.
- Never update this source repository during project intake, implementation, testing, acceptance, or closeout.
- Never treat a source-template file as the active Floppy for a project.

## Deliberate system development

This source repository may be changed only when the user explicitly authorizes development of the Floppy system itself. Such changes should:

1. Preserve earlier released versions or tags.
2. Update `VERSION` and `system-manifest.json` deliberately.
3. Describe migration impact on existing projects.
4. Avoid silently changing already-initialized project repositories.

Existing projects do not automatically inherit later source changes. Migration is a separate, user-authorized operation.

## Authority boundary

A model's authority to modify a project repository does not imply authority to modify this source repository. Authorization must name the source system itself when source changes are intended.
