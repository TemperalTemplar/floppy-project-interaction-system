# Floppy A — Human-in-the-Loop Authority

## Controlling rule

Human authorization is required for every implementation activation, lifecycle
write, migration, release, merge, or other consequential source-system action.

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

That authority permitted creation of root `.floppy/` control state on
`control/source-development-bce-onboarding`. It did not authorize FS-01.

## Current implementation authority

`NO_ACTIVE_WORK_AUTHORIZATION`

## Safety boundaries

- Do not expose, retrieve, rotate, or change credentials.
- Do not modify an adopting project.
- Do not treat reusable seed files as active project state.
- Do not modify product files without exact section authorization.
- Stop on repository, branch, commit, version, scope, or state mismatch.
- One active implementation section maximum.
