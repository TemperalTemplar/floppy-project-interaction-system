# Floppy Project Interaction System

**Status:** development source, version `0.4.0-dev`

The Floppy Project Interaction System is a reusable Human-in-the-Loop project-control layer for AI-assisted development. This repository is the **source of the system**, not the active record for every project that uses it.

A project adopts the system by copying the project seed into that project's own repository. From that point forward, the project owns its Floppies, roadmap, revisions, handoffs, and evidence. Normal project sessions must not write project data back to this source repository.

## Core model

- **Source repository:** defines the method, canonical controllers, templates, bootstrap instructions, and initialization tooling.
- **Floppy 1E onboarding controller:** helps the user and model define the project outcome, inspect the starting state, build an evidence-driven section roadmap, and prepare the first inactive work package. It never authorizes implementation.
- **Floppy Z coordinator:** reads the canonical source plus a project's accepted Floppies and tells Alva exactly what to send to the active project model. It does not perform project writes by default.
- **Project repository:** contains the project code plus its own `.floppy/` control directory and roadmap records.
- **New conversation:** reads a small manifest first, then loads only the controls and project records required for the current lifecycle state.
- **Closeout:** creates a small revision packet, accepted-section record, and inactive next-section draft; it does not regenerate every Floppy.

## Project Floppies and source-system controllers

The five project Floppies remain A–E:

| Floppy | Role | Normal maintenance |
|---|---|---|
| A | Human-in-the-Loop rules | Created and sealed during onboarding; not rewritten during ordinary work |
| B | Development issues | Add or revise individual issue records |
| C | Accepted project baseline | Append only after explicit user acceptance |
| D | Project map and section status | Apply small status, dependency, or roadmap revisions |
| E | Current authorized work section | Revise within the same section; replace only when a new section is authorized |

Two canonical source-system controllers support them:

### Floppy 1E

Floppy 1E is the initial-project definition and roadmap builder. It is loaded only during new-project onboarding or explicit controlled re-onboarding. It produces:

- The project outcome contract
- Verified starting-state classification
- Machine-readable and user-readable roadmap files
- Initial Floppies A–E
- A closed active Floppy E
- An inactive first-section draft

Canonical files:

```text
onboarding/Floppy_1E.md
onboarding/README.md
```

### Floppy Z

Floppy Z is the project-model orchestrator. It reads accepted project state, determines which project model is responsible, and produces the exact instruction Alva should give that model.

Canonical files:

```text
orchestrator/Floppy_Z.md
orchestrator/README.md
```

Neither Floppy 1E nor Floppy Z is a sixth project-state Floppy. Load them read-only from a pinned source version or commit. Do not alter them per project or store project-specific data in this source repository.

## Repository layout

```text
BOOTSTRAP.md                     Startup instructions for onboarding, coordinator, and direct project modes
system-manifest.json             Machine-readable source map and controller digests
onboarding/                      Canonical Floppy 1E and onboarding replication instructions
orchestrator/                    Canonical Floppy Z and coordination instructions
protocols/                       Canonical operating rules
project-seed/.floppy/            Files copied into an adopting project
project-seed/.floppy/roadmap/    Initial roadmap JSON and Markdown templates
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

## Build the initial roadmap

After initialization, load canonical `onboarding/Floppy_1E.md` and follow `protocols/01-new-project-onboarding.md`.

Floppy 1E guides the user and model through:

1. Evidence inspection
2. Project definition
3. Scope and constraint boundaries
4. Section decomposition
5. Dependency ordering
6. Acceptance-evidence design
7. Roadmap review and explicit acceptance
8. Project-owned Floppy creation
9. First inactive work-package creation

Roadmap acceptance does not authorize implementation. The first section begins only after the user separately authorizes it through project Floppy E.

## Start a coordinator conversation

Use the coordinator instruction in `BOOTSTRAP.md`. The coordinator loads `orchestrator/Floppy_Z.md` from this source repository, treats this repository as read-only, reads the adopting project's manifest and Floppies, and tells Alva exactly what to send to the active project model.

The coordinator does not modify either repository unless Alva gives a separate, explicit, named execution override.

## Start a direct project-model conversation

Use the direct-project instruction in `BOOTSTRAP.md`. The project model reads the project manifest, produces a readiness report, and waits for explicit authorization from Floppy E.

## Close a session

Use `protocols/04-everyday-closeout.md`. The ordinary output is a revision packet under `.floppy/revisions/` plus a compact handoff under `.floppy/handoffs/`. Unchanged Floppies are not recreated.

Every accepted section closeout should create the next section's work package as an inactive draft. It must not authorize the next section automatically.

When Floppy Z is coordinating, it prepares the closeout directive for the active project model. It does not perform the closeout writes itself by default.

## Source-repository boundary

This repository may change only when the Floppy system itself is deliberately developed. It is read-only during normal use of an adopting project. Canonical Floppy 1E and Floppy Z must not be edited for an individual project. See `protocols/00-source-repository-policy.md`, `onboarding/README.md`, and `orchestrator/README.md`.

## Version and integrity

Canonical source-system controllers must be pinned to a source version, tag, or commit. `system-manifest.json` records their paths and expected SHA-256 digests. A mismatch is a stop condition, not permission to silently use an altered copy.

## Licensing

No license has been selected yet. Until the owner adds one, normal copyright rules apply.
