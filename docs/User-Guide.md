# User Guide

## What the system does

The Floppy system keeps AI-assisted project work organized across conversations by separating five kinds of information: Human-in-the-Loop rules, development issues, accepted project state, the roadmap, and the current authorized section.

## Source versus project repositories

The Floppy source repository provides the method and a clean project seed. Each adopting project keeps its own `.floppy/` directory in the same repository as the project's code. Project sessions read the source but write only to the project repository.

## New project

1. Copy the seed with `tools/initialize_project.py`.
2. Run the new-project onboarding protocol.
3. Review the proposed A–E Floppies.
4. Accept the initial control set.
5. Request an intake readiness report.
6. Explicitly authorize the first Floppy E section.

This is the normal time to create every Floppy as a complete file.

## Existing project session

1. Give the model the short instruction from `BOOTSTRAP.md`.
2. Review its readiness report.
3. Authorize the current section.
4. Keep future ideas in Floppy D and unrelated defects in Floppy B.
5. Request closeout when the session should end.

## Closeout

Closeout does not rebuild the five Floppies. It produces a compact handoff and a revision packet describing only what changed. Floppy A remains sealed. Floppy C changes only after acceptance. Floppy E is replaced only for a newly authorized section.

## Applying revisions

Review the packet first. After acceptance, allow the model or user to apply only the listed changes to the project-owned Floppies. Git history then records the exact control-state change.

## Safety

Do not store passwords, tokens, private keys, recovery codes, or secret values in Floppies. Record only a credential's name, role, owner, storage location, consumer relationship, and authorization status.

## Provision the initial control state

Run a dry run before creating a project's `.floppy` directory:

```bash
python tools/floppyctl.py initialize --target /path/to/project --project-name "Project Name" --source-repository owner/floppy-source --dry-run
```

Run the same command without `--dry-run` to provision the project. The operation
creates the entire `.floppy` directory only when no `.floppy` directory already
exists. It records a canonical `lifecycle-state.json`, a checkpoint-bound
`orchestrator-registry.json`, and the matching manifest projection. The initial
state is onboarding-only and grants no implementation authority or repository
writer.

Provisioning is deterministic for the same project path, project name, source
version, source repository identity, and Git checkpoint. A failure removes the
staging directory and any newly installed `.floppy` tree, so the project is not
left partially initialized. Symlinks, reparse points, path escapes, stale stage
paths, and overwrite attempts are stop conditions.

After provisioning, validate the project:

```bash
python tools/floppyctl.py --root /path/to/project validate --mode project
```

A successful initialization still does not authorize implementation. Continue
with Floppy 1E onboarding and obtain the required administrator decisions for
the first work package and section activation.
