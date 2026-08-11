# Project Orchestrator Handoff

STATUS: HANDOFF_PENDING

This record transfers administrative coordination context only. It does not
grant implementation authority, repository write authority, integration
authority, or permission to advance a lifecycle section.

## Transfer identity

- From orchestrator ID: `{{FROM_ORCHESTRATOR_ID}}`
- From status: `{{FROM_STATUS}}`
- To orchestrator ID: `{{TO_ORCHESTRATOR_ID}}`
- To status after acceptance: `{{TO_STATUS}}`
- Reporting relationship: `{{REPORTING_RELATIONSHIP}}`

## Exact repository checkpoint

- Repository: `{{REPOSITORY}}`
- Branch: `{{BRANCH}}`
- Worktree: `{{WORKTREE}}`
- Exact checkpoint: `{{CHECKPOINT}}`

## Current authority and responsibility

- Lifecycle state: `{{LIFECYCLE_STATE}}`
- Current authority: `{{CURRENT_AUTHORITY}}`
- Current section working model: `{{CURRENT_SECTION_WORKING_MODEL_OR_NONE}}`
- Repository writer: `{{REPOSITORY_WRITER_OR_NONE}}`
- Writer authorization reference: `{{WRITER_AUTHORIZATION_REFERENCE_OR_NONE}}`

A writer assignment is valid only when the exact authorization reference is
present. Orchestrator status and role never grant write authority.

## Completed work

{{COMPLETED_WORK}}

## Unresolved work

{{UNRESOLVED_WORK}}

## Next legal operation

{{NEXT_LEGAL_OPERATION}}

## Prohibited operations

{{PROHIBITED_OPERATIONS}}

## Verification evidence

{{VERIFICATION_EVIDENCE}}

## Acceptance

- Prepared by: `{{PREPARED_BY}}`
- Prepared on: `{{PREPARED_ON}}`
- Accepted by administrator: `{{YES_OR_NO}}`
- Acceptance reference: `{{ACCEPTANCE_REFERENCE_OR_NONE}}`

The receiving orchestrator must verify the exact checkpoint and registry before
changing status from `HANDOFF_PENDING`. Authority is never transferred
automatically.

<!-- V2_04_SUCCESSION_FIELDS_BEGIN -->
## V2-04 succession fields

When this handoff is used for Project Orchestrator succession, also record:

- Continuity Overseer ID:
- Succession ID:
- Predecessor Project Orchestrator ID:
- Predecessor availability (`AVAILABLE` / `UNAVAILABLE`):
- Recovery mode (`NORMAL` / `REPOSITORY_BACKED`):
- Successor Project Orchestrator ID:
- Exact authority-state projection:
- Authority state SHA-256:
- Successor readiness:
- Administrator cutover decision:
- Stale-handoff verification result:

The predecessor remains `ACTIVE` and the successor remains `HANDOFF_PENDING`
until administrator-accepted cutover. Succession does not itself change
implementation authority or repository-writer authority.
<!-- V2_04_SUCCESSION_FIELDS_END -->

<!-- V2_05_OPP_HANDOFF_TEMPLATE_BEGIN -->
## Official Project Plan continuity

- Plan ID: `NONE_OR_OPP-ID`
- Plan revision ID: `NONE_OR_REVISION-ID`
- Accepted-state revision ID: `NONE_OR_REVISION-ID`
- OPP substantive SHA-256: `NONE_OR_SHA256`
- Active OPP alias: `.floppy/project-plan/official-project-plan.json`

These fields carry accepted planning context only. Re-read current lifecycle, authorization, and orchestrator-registry records before any write.
<!-- V2_05_OPP_HANDOFF_TEMPLATE_END -->
