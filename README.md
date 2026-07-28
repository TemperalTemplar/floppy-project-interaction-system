# Floppy Project Interaction System

**Status:** development source, version `0.2.0-dev`

The Floppy Project Interaction System is a reusable Human-in-the-Loop project-control layer for AI-assisted development. This repository is the **source of the system**, not the active record for every project that uses it.

A project adopts the system by copying the project seed into that project's own repository. From that point forward, the project owns its Floppies, revisions, handoffs, and evidence. Normal project sessions must not write project data back to this source repository.

## Core model

- **Source repository:** defines the method, templates, bootstrap instructions, and initialization tooling.
- **Project repository:** contains the project code plus its own `.floppy/` control directory.
- **New conversation:** reads a small manifest first, then loads only the Floppies required for the active section.
- **Closeout:** creates a small revision packet and continuation handoff; it does not regenerate every Floppy.

## The five Floppies

| Floppy | Role | Normal maintenance |
|---|---|---|
| A | Human-in-the-Loop rules | Created and sealed during onboarding; not rewritten during ordinary work |
| B | Development issues | Add or revise individual issue records |
| C | Accepted project baseline | Append only after explicit user acceptance |
| D | Project map and section status | Apply small status, dependency, or roadmap revisions |
| E | Current authorized work section | Revise within the same section; replace only when a new section is authorized |

## Repository layout

```text
BOOTSTRAP.md                     Short startup instruction for a new model
system-manifest.json             Machine-readable source map
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

## Start a later conversation

Use the short instruction in `BOOTSTRAP.md`, substituting the source and project repository locations. The model should read the project manifest, produce a readiness report, and wait for explicit authorization.

## Close a session

Use `protocols/04-everyday-closeout.md`. The ordinary output is a revision packet under `.floppy/revisions/` plus a compact handoff under `.floppy/handoffs/`. Unchanged Floppies are not recreated.

## Source-repository boundary

This repository may change only when the Floppy system itself is deliberately developed. It is read-only during normal use of an adopting project. See `protocols/00-source-repository-policy.md`.

## Licensing

No license has been selected yet. Until the owner adds one, normal copyright rules apply.
