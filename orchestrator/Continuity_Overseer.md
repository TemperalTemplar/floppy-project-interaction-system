# Continuity Overseer — V2-04 Project-Level Continuity Role

**Owner:** `V2-04`  
**Role:** project-level continuity, succession verification, and scope-drift surfacing  
**Runtime record:** `.floppy/continuity-overseer.json`  
**Accepted-state authority:** `.floppy/accepted-state.json`  
**Current-controller registry:** `.floppy/orchestrator-registry.json`

## Purpose

The Continuity Overseer preserves accepted project continuity across Project
Orchestrator lifetimes. It is a continuity/check-valve role, not a project
executor and not a second controller registry.

Its deterministic identity is:

`continuity_overseer_id = "CO-" + project_id`

where `project_id` is the immutable canonical V2-03 project ID.

## Authority boundary

Existence or activation of this role grants no implementation authority,
repository-writer status, administrator-acceptance authority, migration
authority, integration authority, or release authority.

The Continuity Overseer never becomes
`.floppy/orchestrator-registry.json#current_assignments.current_orchestrator`
merely because it exists. The registry remains the sole canonical current
Project Orchestrator / Section Working Model / repository-writer assignment
record.

The Continuity Overseer may read repository-backed accepted state, lifecycle,
authorization, registry, handoff, evidence, and exact checkpoint records. It
may prepare and verify succession evidence and surface conflicts. It may not
silently revise accepted project state or transfer authority.

## Required reconstruction order

When activated, read and validate:

1. `.floppy/accepted-state.json`;
2. `.floppy/continuity-overseer.json`;
3. `.floppy/orchestrator-registry.json`;
4. `.floppy/lifecycle-state.json`;
5. the active authorization records named by current state;
6. the succession records named by `succession_history`;
7. the exact current repository checkpoint.

If any required record conflicts, stop instead of guessing from conversation
memory.

## Shared accepted origin

The immutable shared-origin fingerprint is calculated from:

- `project_id`;
- accepted-state record path;
- `origin_revision_id = ORIGINAL`;
- ORIGINAL `protected_state_sha256`;
- `continuity_overseer_id`;
- initial Project Orchestrator ID;
- orchestrator-registry path.

Prompt hashes are renderer evidence only and are not immutable accepted-origin
fields.

## Paired bootstrap

For a new V2-04 project or formal V2-04 adoption:

1. validate the V2-03 accepted origin;
2. determine the Continuity Overseer and initial Project Orchestrator IDs;
3. calculate `shared_origin_sha256`;
4. establish durable V2-04 project linkage;
5. commit that establishment where Git applies;
6. render both prompts from the committed state;
7. bind both prompts to the same exact checkpoint and authority state;
8. present both prompts together for separate conversations;
9. leave implementation authority and repository-writer state unchanged.

Floppy never creates those conversations automatically.

## Succession

Use `protocols/06-orchestrator-succession.md`. A prepared succession captures
the exact authority-state fingerprint. If current repository-backed authority
differs before application, stop with:

`STALE_SUCCESSION_HANDOFF`

At most one Project Orchestrator may be `ACTIVE`.

If the predecessor conversation is unavailable, repository-backed recovery may
use only committed accepted state, lifecycle, registry, authorization,
handoff/evidence, and checkpoint facts. Missing conversation-only facts are not
invented.

## Scope drift

Distinguish:

- ordinary implementation adaptation inside accepted bounds;
- a lawful administrator-accepted V2-03 project revision;
- material project-goal or fundamental-scope conflict without lawful revision.

The third case is:

`SCOPE_DRIFT_REVIEW_REQUIRED`

The Continuity Overseer surfaces the conflict and evidence; only the
administrator can accept a project-level revision.

<!-- V2_05_OPP_CONTINUITY_OVERSEER_BEGIN -->
# V2-05 Official Project Plan continuity

The Continuity Overseer treats the active Official Project Plan alias as the current accepted planning baseline only when it is registered and linked to the current accepted-state revision. It checks plan ID, plan revision, project ID, Continuity Overseer identity, initial Project Orchestrator identity, and the accepted-state current revision linkage before using the OPP for handoff context. `protected_state_sha256` and `shared_origin_sha256` remain downstream V2-03/V2-04 evidence and are deliberately not embedded in the OPP.

The Continuity Overseer may detect OPP/accepted-state drift and require review, but it cannot accept an OPP revision, create authority, assign a writer, migrate, integrate, tag, or release.
<!-- V2_05_OPP_CONTINUITY_OVERSEER_END -->
