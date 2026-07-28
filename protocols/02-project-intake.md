# Project Intake Protocol

You are entering an active project that uses the Floppy Project Interaction System.

## Repository sequence

1. Read the project's `.floppy/manifest.json`.
2. Confirm that the manifest identifies a source-system version and five project-owned Floppies.
3. Read only the files in `required_read_order` first.
4. Load additional issue, evidence, code, or handoff files only when the active section requires them.
5. Never write project data to the source repository.

## Floppy roles

- **A — HITL Data:** governs interaction, authority, safety, and communication.
- **B — Development Issues:** records problems and uncertainty; an issue is not automatically in scope.
- **C — Project Baseline:** records accepted and verified project state through the last accepted section.
- **D — Project Map:** locates the current section within the bounded roadmap.
- **E — Current Work:** defines the only currently authorized execution scope.

## Priority

Apply A for Human-in-the-Loop behavior, E for execution authority, D for scope location and dependencies, C for preserved baseline, and B for relevant issues. Reconcile all applicable instructions rather than ignoring lower-priority files.

## Intake behavior

- Preserve accepted work.
- Distinguish facts, user reports, assumptions, and proposals.
- Do not treat file presence as proof of runtime use.
- Do not expand scope because adjacent work appears useful.
- Do not begin a later section automatically.
- Stop before destructive or state-changing work when the Floppies conflict.

## Required readiness report

Report:

- Project and source-system version
- Last accepted section
- Current section and status
- Authorized objective
- Relevant baseline
- Relevant issue identifiers
- In-scope and prohibited actions
- Required approvals and stop conditions
- Missing or conflicting information
- First safe action

Do not implement, edit, commit, deploy, or advance sections until the user explicitly authorizes the current section.

## Closeout notice

This project uses a separate closeout protocol identified in `.floppy/manifest.json`. Do not close automatically. When the user requests closeout, load that protocol, stop new implementation, and prepare delta revisions rather than regenerated Floppies.
