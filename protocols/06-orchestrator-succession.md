# Protocol 06 — Project Orchestrator Succession

**Owner:** `V2-04`  
**Record family:** `.floppy/handoffs/orchestrator-succession-######.json`  
**Schema:** `schemas/bce/2.0.0/bce-orchestrator-succession.schema.json`

## 1. Purpose

This protocol transfers Project Orchestrator responsibility without restarting
the project, recreating accepted work, or silently changing authority.

Succession is administrative continuity. It is not implementation
authorization.

## 2. Preconditions

Before preparing succession:

1. validate `.floppy/accepted-state.json` when V2-03 is active;
2. validate `.floppy/continuity-overseer.json`;
3. validate `.floppy/orchestrator-registry.json`;
4. prove no more than one Project Orchestrator is `ACTIVE`;
5. record the exact repository checkpoint;
6. capture the exact seven-field authority projection;
7. calculate `authority_state_sha256`.

The authority projection is exactly:

- lifecycle state;
- active work authorization;
- active implementation authorization;
- active implementation section;
- current Section Working Model;
- repository writer;
- writer authorization reference.

## 3. Identity

Succession IDs are append-only:

`ORCH-SUCC-000001`, `ORCH-SUCC-000002`, ...

Generated successor Project Orchestrator IDs are:

`ORCH-<project_id>-<8-digit-sequence>`

Use the lowest positive never-used sequence. Never reuse a Project Orchestrator
ID after it appears in accepted project history.

A model/provider/conversation replacement does not itself create a new
Project Orchestrator ID. A real succession does.

## 4. Normal succession

1. predecessor remains `ACTIVE`;
2. prepare the succession record;
3. successor is `HANDOFF_PENDING`;
4. successor demonstrates readiness from repository-backed state;
5. Continuity Overseer verifies readiness and fingerprint invariance;
6. administrator explicitly accepts cutover;
7. application retires predecessor;
8. successor becomes the sole `ACTIVE` Project Orchestrator and sole current
   orchestrator assignment.

There is never a lawful two-active-orchestrator interval.

## 5. Repository-backed recovery succession

If the predecessor conversation is unavailable, use
`recovery_mode = REPOSITORY_BACKED`.

Recovery may reconstruct only committed accepted state, lifecycle, registry,
authorization, handoff/evidence, and exact checkpoint facts. It must not invent
conversation-only state.

Administrator cutover is still required.

## 6. Authority invariance

Succession cannot create, remove, replace, expand, or narrow authority.

Immediately before readiness/cutover/application, recalculate the authority
projection. If its canonical SHA-256 differs from the prepared
`authority_state_sha256`, stop:

`STALE_SUCCESSION_HANDOFF`

Prepare a new succession record from current state rather than mutating stale
evidence.

When active implementation authority exists, the administrator may separately
choose `CONTINUE_EXISTING_AUTHORIZATION_UNCHANGED` or perform another lawful
authority operation. Succession itself performs neither choice silently.

## 7. Scope drift

Ordinary technical adaptation within accepted bounds continues normally.
A committed, administrator-accepted V2-03 project revision is recognized as the
new accepted state. A material project-goal/fundamental-scope conflict without
such revision stops at:

`SCOPE_DRIFT_REVIEW_REQUIRED`

The Continuity Overseer reports evidence; it does not accept the revision.

## 8. Forbidden behavior

Succession must not:

- automatically create a conversation;
- automatically transfer authority;
- become a repository writer by role;
- rewrite `.floppy/accepted-state.json`;
- create a competing current-controller registry;
- infer missing predecessor conversation facts;
- perform migration, integration, merge, tag, or release work merely because a
  succession record exists.

<!-- V2_05_OPP_SUCCESSION_BEGIN -->
## V2-05 OPP continuity during succession

A successor Project Orchestrator reads the current accepted OPP alias together with accepted-state, Continuity Overseer, roadmap, lifecycle, authorization, and orchestrator-registry records. The OPP supplies accepted project intent/scope and roadmap context; it does not replace the current-controller registry and does not confer writer authority. Succession must preserve OPP plan id/revision and shared-origin linkage unless a separate accepted project revision lawfully changes them.
<!-- V2_05_OPP_SUCCESSION_END -->
