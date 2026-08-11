# Project Floppy Start Here

This `.floppy/` directory belongs to **{{PROJECT_NAME}}**. It was initialized from Floppy Project Interaction System version `0.4.1-dev`.

The Floppy Project Interaction System implements a **BCE — Bootable Context Environment** for AI-assisted projects. The canonical conceptual explanation is stored in the source repository at `ABOUT.md`.

## Current lifecycle state

```text
PROJECT ONBOARDING:
REQUIRED

ROADMAP:
NOT ACCEPTED

IMPLEMENTATION AUTHORIZATION:
NONE
```

## Initial-project startup

1. Read `manifest.json`.
2. Confirm the pinned source repository and system version.
3. Read source `ABOUT.md` when the model or user needs the BCE and system concepts explained.
4. Load canonical `onboarding/Floppy_1E.md` from the source repository.
5. Verify the Floppy 1E digest recorded in the source and project manifests when practical.
6. Read the onboarding protocol and local files in the manifest order.
7. Inspect available project evidence before asking the user questions.
8. Build and present the project definition and section roadmap.
9. Wait for explicit roadmap acceptance.
10. Finalize project-owned Floppies A–E and roadmap records.
11. Leave Floppy E closed and create the first section only as an inactive draft unless the user separately authorizes it.

Do not begin project implementation during onboarding.

## Roadmap files

```text
.floppy/roadmap/roadmap.json
.floppy/roadmap/roadmap.md
```

The JSON file provides machine-readable section identity, dependencies, statuses, and authorization. The Markdown file explains the roadmap to the user.

## Repository boundary

- Project-specific records belong here.
- The source repository is read-only during ordinary project work.
- Canonical Floppy 1E and Floppy Z are loaded from the pinned source; do not alter them for this project.
- The source `ABOUT.md` explains the architecture but is not project state or execution authorization.
- Do not copy project data back into the source.
- Do not store secret values here.

## Lifecycle

During initial onboarding, create or finalize complete Floppies A–E and accept the first roadmap version. After onboarding, ordinary sessions use delta revision packets and section closeouts. Do not regenerate all five Floppies or rerun Floppy 1E during routine work.

A material project redefinition requires explicit controlled re-onboarding and must preserve the earlier accepted roadmap as historical evidence.

<!-- V2_04_PROJECT_CONTINUITY_BEGIN -->
## Optional V2-04 project continuity records

A project that has explicitly adopted V2-04 may contain:

- `.floppy/continuity-overseer.json`;
- `.floppy/handoffs/orchestrator-succession-######.json`.

Do not create either merely because a V2-capable source is present. If
`.floppy/manifest.json#continuity_overseer` is `ACTIVE`, load and validate the
continuity record after the accepted-state record and before relying on
orchestrator succession. `.floppy/orchestrator-registry.json` remains the sole
current-controller/writer registry.
<!-- V2_04_PROJECT_CONTINUITY_END -->
