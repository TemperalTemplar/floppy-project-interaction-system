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
