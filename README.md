# Floppy Project Interaction System

**Status:** development source, version `0.3.0-dev`

The Floppy Project Interaction System is a reusable Human-in-the-Loop project-control layer for AI-assisted development. This repository is the **source of the system**, not the active record for every project that uses it.

A project adopts the system by copying the project seed into that project's own repository. From that point forward, the project owns its Floppies, revisions, handoffs, and evidence. Normal project sessions must not write project data back to this source repository.

## Core model

- **Source repository:** defines the method, canonical orchestrator, templates, bootstrap instructions, and initialization tooling.
- **Floppy Z coordinator:** reads the canonical source plus a project's Floppies and tells Alva exactly what to send to the active project model. It does not perform project writes by default.
- **Project repository:** contains the project code plus its own `.floppy/` control directory.
- **New conversation:** reads a small manifest first, then loads only the Floppies required for the active section.
- **Closeout:** creates a small revision packet and continuation handoff; it does not regenerate every Floppy.

## Project Floppies and system orchestrator

The five project Floppies remain A–E:

| Floppy | Role | Normal maintenance |
|---|---|---|
| A | Human-in-the-Loop rules | Created and sealed during onboarding; not rewritten during ordinary work |
| B | Development issues | Add or revise individual issue records |
| C | Accepted project baseline | Append only after explicit user acceptance |
| D | Project map and section status | Apply small status, dependency, or roadmap revisions |
| E | Current authorized work section | Revise within the same section; replace only when a new section is authorized |

**Floppy Z is not a sixth project-state Floppy.** It is the source-system orchestrator. It reads A–E, reconstructs the accepted state, determines which project model is responsible, and produces the exact instruction Alva should give that model.

Canonical orchestrator files:

```text
orchestrator/Floppy_Z.md
orchestrator/README.md
```

Load them read-only from a pinned source version or commit. Do not alter Floppy Z per project or store project-specific data in this source repository.

## Repository layout

```text
BOOTSTRAP.md                     Startup instructions for coordinator and direct project modes
system-manifest.json             Machine-readable source map
orchestrator/                    Canonical Floppy Z and replication instructions
protocols/                       Canonical operating rules
project-seed/.floppy/            Files copied into an adopting project
schemas/                         Human-readable field requirements
tools/                           Initialization and validation scripts
docs/                            User and design documentation
legacy/prototype-v0/             Original supplied prototype, preserved unchanged
tests/                           Standard-library tests for the tooling
```

## Initialize a project

Run a dry run first:

```bash
python tools/initialize_project.py --target /path/to/project --project-name "Project Name" --dry-run
```

Then initialize:

```bash
python tools/initialize_project.py --target /path/to/project --project-name "Project Name"
```

The initializer creates only `/path/to/project/.floppy`. It refuses to overwrite an existing `.floppy` directory unless the user deliberately chooses a separate migration process.

After scaffolding, use `protocols/01-new-project-onboarding.md` to create the project's first complete Floppy set. Full-file creation is normal only during onboarding of a new project.

## Start a coordinator conversation

Use the coordinator instruction in `BOOTSTRAP.md`. The coordinator loads `orchestrator/Floppy_Z.md` from this source repository, treats this repository as read-only, reads the adopting project's manifest and Floppies, and tells Alva exactly what to send to the active project model.

The coordinator does not modify either repository unless Alva gives a separate, explicit, named execution override.

## Start a direct project-model conversation

Use the direct-project instruction in `BOOTSTRAP.md`. The project model reads the project manifest, produces a readiness report, and waits for explicit authorization from Floppy E.

## Close a session

Use `protocols/04-everyday-closeout.md`. The ordinary output is a revision packet under `.floppy/revisions/` plus a compact handoff under `.floppy/handoffs/`. Unchanged Floppies are not recreated.

When Floppy Z is coordinating, it prepares the closeout directive for the active project model. It does not perform the closeout writes itself by default.

## Source-repository boundary

This repository may change only when the Floppy system itself is deliberately developed. It is read-only during normal use of an adopting project. Canonical Floppy Z must not be edited for an individual project. See `protocols/00-source-repository-policy.md` and `orchestrator/README.md`.

## Version and integrity

The canonical orchestrator must be pinned to a source version, tag, or commit. `system-manifest.json` records the orchestrator path and expected SHA-256 digest. A mismatch is a stop condition, not permission to silently use an altered copy.

## Licensing

No license has been selected yet. Until the owner adds one, normal copyright rules apply.
