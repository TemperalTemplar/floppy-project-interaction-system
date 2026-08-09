# Floppy V2 Project Plan Revision R1

## Paired Continuity Overseer and Initial Project Orchestrator Bootstrap

**Status:** ACCEPTED — ADMINISTRATOR-DIRECTED CLARIFICATION  
**Revision:** R1  
**Decision date:** 2026-08-09  
**Administrator:** Alva Roberts  
**Base V2 project plan:** `.floppy/roadmap/Floppy-V2-Project-Plan.md`  
**Base plan version:** `2.0`  
**V2-01 closed checkpoint:** `5dfa36a3632b0910f29ecd69a5ad2aafc950a8b9`  
**V2-01 locally reported tree:** `346fd515af0316c08bc4024bd53aa7839f22affa`

---

# 1. Purpose

This revision makes explicit a continuity behavior already implicit in the accepted V2 architecture:

**When a new project is accepted into Floppy-controlled operation, or when an existing non-Floppy project is formally adopted into Floppy, the Continuity Overseer prompt and the initial Project Orchestrator / Floppy Z prompt must be issued together.**

They are separate conversations with separate responsibilities, but they must begin from the same accepted project origin.

This revision does not create a new work package. The V2 roadmap remains exactly five work packages, V2-01 through V2-05.

This revision does not authorize V2-02 implementation or any later implementation.

---

# 2. Paired project-genesis / adoption bootstrap

At the completion of project onboarding and formal project acceptance/adoption into Floppy, before orchestrated implementation begins, Floppy must produce or issue both:

1. a **Continuity Overseer prompt**; and
2. an **initial Project Orchestrator / Floppy Z prompt**.

The prompts must be presented together as the two project-level conversations required to begin controlled project operation.

The prompts must not be collapsed into one conversation.

The administrator should not need to create the Project Orchestrator first and later reconstruct a Continuity Overseer after project history has accumulated.

---

# 3. Shared project origin

The Continuity Overseer and initial Project Orchestrator must be bound to one shared accepted project-origin record.

That shared origin must include, at minimum:

- project identity;
- original intended observable project outcome;
- accepted project scope;
- accepted exclusions;
- major project constraints;
- verified starting state;
- accepted project plan and roadmap;
- exact repository checkpoint where applicable;
- current authority state;
- Continuity Overseer identity; and
- initial Project Orchestrator identity.

V2-04 and V2-05 may define additional machine-readable identifiers, digests, linkage records, or validation rules, but they may not weaken this shared-origin requirement.

---

# 4. Role lifetime and responsibility

## Continuity Overseer

The Continuity Overseer is the comparatively stable project-lifetime continuity role.

Its purpose is to preserve project direction and continuity across Project Orchestrator lifetimes.

It must retain visibility of:

- the original accepted project goal;
- the accepted project scope and exclusions;
- the current accepted project plan;
- accepted revisions;
- current and historical orchestrator identity;
- accepted work;
- unresolved matters;
- exact repository checkpoints;
- authority state; and
- the next lawful project operation.

It does not become the implementation worker, repository writer, or administrator.

## Project Orchestrator / Floppy Z

The Project Orchestrator is the replaceable operational project-coordination conversation.

A Project Orchestrator may be retired or replaced because of context saturation, model replacement, project phase change, or another lawful continuity reason.

A replacement orchestrator must inherit the same project-origin chain and remain accountable to the accepted project outcome and current lawful project plan.

## Section Working Models

Section Working Models remain separate bounded working conversations under project-orchestrator coordination.

The existence of the Continuity Overseer does not collapse the existing separation among Overseer, Orchestrator, Working Model, and Repository Writer.

---

# 5. Original-goal and scope protection

The Continuity Overseer must protect the project against gradual silent drift away from its original accepted purpose.

It must distinguish among:

1. **ordinary implementation adaptation** — technical choices may change while remaining within accepted project outcome and scope;
2. **lawful project-plan revision** — the administrator may explicitly revise accepted plans when new facts require it; and
3. **material project-goal or fundamental-scope change** — this must be surfaced to the administrator as an explicit project-level revision rather than being accumulated through ordinary orchestrator decisions.

The Continuity Overseer must not reject lawful administrator-approved changes merely because they differ from the original plan.

The Continuity Overseer must not silently permit a chain of individually small changes to transform the project into a materially different project without explicit administrator recognition.

The controlling intent is:

**Preserve the original project goal and remain as close to accepted scope as practical unless a real, explicit project-level change is required and lawfully accepted.**

---

# 6. Authority boundary

Paired issuance does not create implementation authority.

Neither the Continuity Overseer nor the Project Orchestrator gains repository-write authority merely because its prompt is issued.

The hierarchy remains a responsibility and continuity structure, not an automatic authority-transfer structure.

Floppy E and the accepted lifecycle/authorization model remain controlling unless separately and lawfully revised.

---

# 7. Work-package placement

This revision clarifies the existing five-package roadmap as follows.

## V2-02 — User Onboarding and Provider-Independent Adoption

V2-02 must define the user-facing trigger and onboarding/adoption handoff for the paired bootstrap.

A user completing a new-project acceptance or formal Floppy adoption must understand that controlled project operation uses two project-level conversations issued together:

- Continuity Overseer; and
- initial Project Orchestrator.

V2-02 must not prematurely implement V2-04 succession/runtime behavior.

## V2-03 — Accepted-State Continuity Protection

V2-03 must protect the project-origin record, original accepted goal, accepted scope, exclusions, constraints, and accepted project-plan state from silent reconstruction, replacement, or drift.

Lawful revision/supersession remains allowed.

## V2-04 — Continuity Overseer and Orchestrator Succession

V2-04 must implement:

- paired Continuity Overseer / initial Project Orchestrator bootstrap;
- separate prompt/conversation generation or issuance;
- durable shared-origin linkage;
- Continuity Overseer persistence across orchestrator replacement;
- replacement-orchestrator linkage to the same project-origin chain;
- scope-drift detection/surfacing sufficient to protect the original accepted project intent; and
- normal orchestrator succession without project restart or authority mutation.

## V2-05 — Official Project Plan, Integration, Compatibility Validation, and V2 Release

V2-05 must bind the Official Project Plan to the same accepted project origin used by the paired Continuity Overseer and initial Project Orchestrator.

The end-to-end new-project and existing-project adoption proofs must demonstrate that both project-level prompts are issued together before orchestrated implementation begins.

---

# 8. Acceptance impact

The V2-02 acceptance boundary now includes proof that onboarding/adoption reaches the paired-bootstrap handoff without pretending that V2-02 itself implements V2-04.

The V2-03 acceptance boundary now includes protection of original project-intent and project-origin records.

The V2-04 acceptance boundary now includes paired initial issuance, durable shared-origin linkage, project-intent preservation, and succession of replaceable orchestrators under one stable Continuity Overseer.

The V2-05 end-to-end proof must show the Official Project Plan, Continuity Overseer, and initial Project Orchestrator bound to the same project origin.

---

# 9. Preserved boundaries

This revision:

- does not reopen V2-01;
- does not add V2-06;
- does not authorize V2-02 work-package acceptance;
- does not authorize V2-02 activation or implementation;
- does not create a repository writer;
- does not authorize migration;
- does not authorize `main` modification;
- does not authorize integration, merge, tag, or release;
- does not modify frozen V1 schemas;
- does not modify `project-seed/.floppy/*`; and
- does not change the closed V2-01 historical disposition.

Current authority remains:

- active work authorization: **NONE**;
- active implementation authorization: **NONE**;
- repository writer: **NONE**; and
- V2-02 through V2-05: **PLANNED / NOT AUTHORIZED**.

---

# 10. Controlling effect

This R1 record is an accepted administrator-directed clarification of the existing Version 2.0 Project Plan.

The original accepted project plan remains authoritative historical evidence.

For the paired Continuity Overseer / Project Orchestrator bootstrap and project-intent preservation topics addressed here, this revision is the controlling clarification wherever the original plan was silent or less explicit.

**Context loss is not authority to reconstruct accepted work.**
