# Source Repository Policy

## Purpose

This repository is the canonical source from which projects adopt the Floppy Project Interaction System. It is not a shared database of active projects.

It contains two canonical source-system controllers:

- **Floppy 1E** builds the initial project definition and evidence-driven roadmap.
- **Floppy Z** coordinates later project-model instructions without becoming project state.

Neither controller grants project implementation authority.

## Normal project use

During work on an adopting project:

- Read this repository only to obtain the system version, canonical controllers, protocols, templates, or tooling.
- Write project-specific information only inside the adopting project's repository.
- Never place a project's code, credentials, Floppies, roadmap records, revision packets, handoffs, evidence, or session history in this source repository.
- Never update this source repository during project intake, roadmap construction, implementation, testing, acceptance, or closeout.
- Never treat a source-template or source-controller file as the active Floppy for a project.
- Never edit canonical Floppy 1E or Floppy Z to fit an individual project.
- Never treat Floppy 1E as implementation authorization.
- Never treat Floppy Z as Floppy E or as project execution authorization.

## Floppy 1E onboarding boundary

Canonical files:

```text
onboarding/Floppy_1E.md
onboarding/README.md
```

During initial-project onboarding:

- Load Floppy 1E from a pinned source version, tag, or commit.
- Verify its digest through `system-manifest.json` when practical.
- Treat the canonical file and any exact offline source mirror as read-only.
- Inspect project evidence and write all project-specific outputs into the project's `.floppy/` directory.
- Use Floppy 1E to define the project outcome, roadmap, acceptance evidence, and first inactive work package.
- Leave active project Floppy E closed unless the user separately authorizes the first section.
- Remove Floppy 1E from normal session loading after onboarding acceptance while retaining its source path and digest as provenance.
- Stop and report a source-version or digest mismatch instead of silently using an altered copy.

Ordinary section work and closeout must not rerun Floppy 1E. Controlled re-onboarding requires explicit user authorization and must preserve the earlier accepted roadmap as history.

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

An adopting project does not automatically receive mutable copies of Floppy 1E or Floppy Z. Existing project repositories do not need modification merely to read the canonical controllers.

## Deliberate system development

This source repository may be changed only when the user explicitly authorizes development of the Floppy system itself. Such changes should:

1. Preserve earlier released versions or tags.
2. Update `VERSION` and `system-manifest.json` deliberately.
3. Update canonical controller digests when their content changes.
4. Update initialization and validation tooling when seed requirements change.
5. Describe migration impact on existing projects.
6. Avoid silently changing already-initialized project repositories.

Existing projects do not automatically inherit later source changes. Migration is a separate, user-authorized operation.

## Authority boundary

A model's authority to modify a project repository does not imply authority to modify this source repository. Authorization must name the source system itself when source changes are intended.

Likewise, permission to read or coordinate through Floppy 1E or Floppy Z does not grant permission to alter either controller, the source repository, the project repository, or production systems.
