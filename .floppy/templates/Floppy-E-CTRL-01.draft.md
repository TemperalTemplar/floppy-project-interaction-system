STATUS: ACCEPTED AS PLANNING BASELINE

# CTRL-01 Work Package — Project Orchestrator Registration and Handoff

## Accepted objective

CTRL-01 adds only:

1. Startup instructions in `BOOTSTRAP.md` and canonical Floppy Z requiring the
   administrator to create or load a project orchestrator.
2. One project registry containing the current orchestrator, current section
   working model or `NONE`, repository writer or `NONE`, repository context,
   reporting relationship, and status.
3. One orchestrator handoff template transferring repository state, current work,
   unresolved work, next legal operation, and prohibited operations.
4. One focused test enforcing one active orchestrator, one repository writer,
   exact authorization for writer authority, and separation of role from write
   authority.

## Exact reusable-product scope

```text
BOOTSTRAP.md
orchestrator/Floppy_Z.md
project-seed/.floppy/orchestrator-registry.json
project-seed/.floppy/templates/orchestrator-handoff.md
project-seed/.floppy/manifest.json
tests/test_orchestrator_registry.py
system-manifest.json
```

Exactly one reusable-product commit is accepted:

`feat(ctrl-01): add orchestrator registration and handoff`

No additional reusable-product file is accepted.

## Required boundaries

- At most one orchestrator may be `ACTIVE`.
- At most one repository writer may be current.
- Writer authority requires a separately issued exact authorization reference.
- Role, registration, reporting relationship, or status never grants write
  authority.
- `ACTIVE` means administratively current, not online or runtime-detected.
- Runtime monitoring, heartbeat logic, private-conversation inspection,
  automatic conversation creation, and automatic authority transfer are out of
  scope.

## Preserved project state

- FS-01 remains closed.
- FS-02 remains paused in `READ_ONLY_FS_02_WORK_PACKAGE_PREPARATION`.
- Repository writer remains `NONE`.
- The preserved FS-02 continuation checkpoint remains
  `cec7e0c16b8a2a15fbcc9b0ff5ab13c47901d149`.

## Acceptance boundary

This work package is accepted as a planning baseline only. CTRL-01 activation,
implementation, branch creation, worktree creation, product modification, push,
integration, merge, release, migration, and FS-02 resumption remain unauthorized.

Any future CTRL-01 implementation branch and worktree must be created from the
Git commit containing this accepted work-package record and only after separate
exact `CTRL_01_IMPLEMENTATION` authorization.
