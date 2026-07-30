# Floppy A — Human-in-the-Loop Authority

## Controlling rule

Human authorization is required for every implementation activation, lifecycle
write, migration, integration, release, merge, tag, or other consequential
source-system action.

No authorization may be inferred from:

- roadmap acceptance;
- a draft work package;
- branch or worktree existence;
- prior authorization for a different operation;
- implementation completion;
- verification completion;
- silence or continuation of a conversation.

## Current accepted authority

The administrator authorized only:

`SOURCE_DEVELOPMENT_BCE_ONBOARDING`

That authority permitted creation and amendment of root `.floppy/` control state
on `control/source-development-bce-onboarding`. It did not authorize FS-01.

## Current implementation authority

`NO_ACTIVE_WORK_AUTHORIZATION`

## Clean-source integration authority boundary

Root `.floppy/` is control-branch-only project state. It is not reusable source
product and must not be merged into `main`, copied into `project-seed/.floppy/`,
packaged, released, installed into adopting projects, or included in BCE exports
for other projects.

New projects receive only the generic `project-seed/.floppy/` initialization
media. They must not receive this source-development project's roadmap,
authorizations, revisions, handoffs, evidence, or closeouts.

A source-development branch may contain control-state changes and authorized
product changes, subject to all of these controls:

1. Root `.floppy/` changes and reusable product changes must use separate commits.
2. No commit may mix root `.floppy/` paths with reusable source-product paths.
3. Product commits must be independently reviewable and transferable.
4. Canonical integration must begin from clean `main`.
5. Only accepted product commits may be applied to the clean integration branch.
6. Root `.floppy/` commits must be excluded.
7. The final integration comparison must contain no root `.floppy/` path.
8. Integration, merge, tagging, and release require separate administrator
   authorization.
9. The onboarding branch must not be merged wholesale into `main`.

No authorization to implement a section authorizes integration or release unless
those actions are separately and explicitly named.

## Safety boundaries

- Do not expose, retrieve, rotate, or change credentials.
- Do not modify an adopting project.
- Do not treat reusable seed files as active project state.
- Do not modify product files without exact section authorization.
- Do not mix control-state and product files in a commit.
- Stop on repository, branch, commit, version, scope, or state mismatch.
- One active implementation section maximum.
