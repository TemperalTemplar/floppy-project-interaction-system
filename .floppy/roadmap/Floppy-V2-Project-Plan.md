# Floppy Project Interaction System

# Version 2.0 Project Plan

**Plan status:** ACCEPTED — ADMINISTRATOR ACCEPTED 2026-08-08
**Implementation authority:** NONE
**Repository:** `TemperalTemplar/floppy-project-interaction-system`
**Published v1 release:** `v1.0.0`
**V2 development base:** `main` at `c8b40bb248336990da9112dd1b6b20de154572c5`
**Target release:** `v2.0.0`

---

# 1. Purpose

Floppy Project Interaction System version 2.0 will extend the completed v1 system in three primary directions:

1. improve continuity across long-running AI-assisted projects;
2. make Floppy substantially easier for first-time users to adopt across multiple AI providers; and
3. formalize the transition from project discovery/design into an official project plan without falsely freezing implementation details that cannot yet be known.

Version 2 is an expansion of the existing Floppy/BCE architecture.

It is not a redesign of v1.

Version 1 remains the accepted architectural foundation for:

- Human-in-the-Loop authority;
- Floppies A-E;
- Floppy 1E onboarding;
- Floppy Z project coordination;
- BCE repository-resident context;
- lifecycle separation;
- work-package acceptance;
- implementation authorization;
- repository-writer control;
- deterministic provisioning;
- validation;
- portable context export;
- section closeout;
- final-project closure; and
- source/project repository separation.

V2 may extend those mechanisms where required by the new capabilities, but it must not rebuild working v1 behavior merely because a new implementation would be possible.

---

# 2. Controlling V2 Principles

## 2.1 V1 is a closed baseline

FS-01 through FS-13 are historical v1 work.

V2 must not reopen, reinterpret, regenerate, or renumber those completed sections.

The published `v1.0.0` tag remains immutable.

V2 development begins from the current public `main` so that the post-release newcomer documentation already added to the repository is retained.

---

## 2.2 Context loss is not revision authority

A new model, orchestrator, or conversation may reconstruct accepted project state.

It may not replace accepted state merely because it did not personally participate in the decision.

The governing principle is:

**Context loss is not authority to reconstruct accepted work.**

Accepted work remains authoritative until an explicit, lawful revision or supersession process changes it.

---

## 2.3 Continuity does not create implementation authority

The Continuity Overseer, project orchestrator, Floppy Z, handoff system, and BCE records may determine:

- what has happened;
- what has been accepted;
- what remains unresolved;
- which model is responsible;
- what operation is legally next; and
- what instruction should be transferred.

None of those facts automatically authorize implementation.

Floppy E remains the execution-authority boundary unless an explicitly accepted v2 design lawfully changes that model.

---

## 2.4 AI-provider capability is separate from project authority

Floppy must function whether an AI can:

- read and write a repository directly;
- read the repository but cannot write it; or
- work only through uploaded files, pasted evidence, generated files, and administrator-applied changes.

Provider capability controls **how** an authorized operation is performed.

It does not control **whether** the operation is authorized.

---

## 2.5 Human-facing simplicity, machine-facing rigor

A first-time user should not be required to understand:

- BCE;
- Floppies A-E;
- lifecycle states;
- work packages;
- repository writers;
- transition identifiers; or
- orchestrator hierarchy

before using Floppy.

The user should be able to:

1. open an AI conversation;
2. paste one Floppy starter prompt;
3. describe the project naturally; and
4. let Floppy determine the correct onboarding route.

Internally, the same lifecycle, authority, validation, and evidence rigor remains in force.

---

# 3. Target V2 Architecture

The intended long-running project hierarchy is:

```
Administrator
     │
     ▼
Continuity Overseer
     │
     ▼
Project Orchestrator / Floppy Z
     │
     ▼
Section Working Model
     │
     ▼
Repository Writer

```

This hierarchy represents responsibility and reporting relationships.

It does not imply automatic authority transfer.

---

# 4. Continuity Overseer

V2 introduces a Continuity Overseer as a project-level continuity control.

## Purpose

The Continuity Overseer exists primarily to manage transitions between project orchestrators when an orchestrator conversation reaches practical context limits, is retired, or must otherwise be replaced.

It is a continuity and handoff authority-control mechanism, not an implementation worker.

## Responsibilities

The Continuity Overseer must be able to reconstruct and preserve:

- project identity;
- accepted project outcome;
- current roadmap;
- completed sections;
- active or inactive section;
- accepted decisions;
- protected accepted state;
- active authorization or absence of authority;
- current project orchestrator;
- current working model;
- repository writer;
- unresolved matters;
- next legal operation;
- exact repository checkpoint;
- branch and worktree identity where applicable;
- required handoff evidence; and
- prohibited actions.

## Handoff responsibility

Before a project orchestrator is replaced, the Continuity Overseer must ensure a bounded handoff exists.

A replacement orchestrator must receive sufficient repository-backed information to continue from the accepted project state without reconstructing the project from conversation history.

## Boundaries

The Continuity Overseer must not automatically:

- implement project features;
- become repository writer;
- activate a work package;
- authorize a section;
- accept work for the administrator;
- rewrite historical state;
- inspect private conversations that have not been supplied to it;
- infer hidden context;
- create invisible authority transfers; or
- bypass Floppy E.

---

# 5. Accepted-State Continuity Protection

V2 will formalize protection for administrator-accepted project state.

The exact schema representation will be determined during V2-03, but the semantic requirement is fixed:

An accepted project fact, decision, disposition, roadmap result, section result, or other protected record may not be silently regenerated or replaced because a subsequent model lacks conversational context.

## Required behaviors

A model may:

- read accepted state;
- validate accepted state;
- cite accepted evidence;
- identify conflicts;
- propose a revision;
- identify that a prior decision is no longer suitable.

A model may not:

- silently rewrite the accepted record;
- change historical dispositions;
- translate an accepted state into a different state merely for convenience;
- re-run an already accepted design process as if it never occurred;
- downgrade accepted evidence to an assumption;
- upgrade an unresolved matter into an accepted fact; or
- use context-window loss as justification for reconstruction.

## Revision route

When accepted state genuinely needs to change, V2 must provide or reuse an explicit revision/supersession route.

The historical record must show:

- what was previously authoritative;
- why revision was proposed;
- who authorized revision;
- what replaced the old state;
- when it became authoritative; and
- whether historical dispositions remain separately authoritative.

---

# 6. Formal User Onboarding Layer

V2 distinguishes:

```
USER ONBOARDING
        ↓
PROJECT ONBOARDING

```

User onboarding teaches a newcomer how to enter the Floppy environment.

Project onboarding remains the Floppy 1E process that defines the actual project.

They must not be treated as the same operation.

---

# 7. Universal First-Use Experience

A new user should be able to begin with a universal prompt equivalent to:

```
I want to use the Floppy Project Interaction System.

Load the canonical stable Floppy source.

I am new to Floppy.

First let me describe what I want to build or continue in ordinary language.

Determine whether I have:
- only a project idea;
- an existing project that has not adopted Floppy; or
- an existing Floppy-controlled project.

Guide me into the correct Floppy process.

Do not assume that wanting to build the project authorizes implementation.

```

The complete canonical prompt will be maintained by Floppy rather than independently rewritten for each AI provider.

---

# 8. Provider-Independent Capability Model

V2 will define generic AI access/capability classes.

The implementation may refine the names, but it must preserve these semantic classes.

## Class A — Repository read/write

The AI environment can inspect repository state and, when separately authorized, perform repository writes.

Example workflow:

```
AI reads project
→ Floppy validates authority
→ authorized working model performs bounded change
→ validation
→ Git evidence

```

## Class B — Repository read / administrator-applied writes

The AI can inspect the repository but cannot directly perform repository mutations.

Example workflow:

```
AI reads project
→ Floppy validates authority
→ AI produces exact change
→ administrator applies change
→ AI/repository validates result

```

## Class C — Manual evidence/file exchange

The AI cannot directly access some or all repository state.

Project evidence is supplied through:

- file upload;
- pasted text;
- repository snapshots;
- public repository URLs where supported;
- exported BCE/context packages; or
- other administrator-controlled exchange.

Example workflow:

```
administrator supplies evidence
→ AI reconstructs bounded state
→ Floppy validates authority
→ AI prepares files/instructions
→ administrator applies
→ result returned for validation

```

All three classes remain valid Floppy operating environments.

No class receives weaker or stronger lifecycle authority merely because of tool access.

---

# 9. Provider-Specific User Guides

V2 will maintain platform-facing onboarding documentation separately from the canonical Floppy behavior.

Proposed structure:

```
docs/
  getting-started/
    README.md
    ChatGPT.md
    Gemini.md
    Grok.md
    DeepSeek.md
    Other-AI.md

```

## Maintained guides

### ChatGPT

Explain:

- how a user prepares GitHub access when available;
- how to identify the canonical Floppy repository and version;
- how to paste the universal starter prompt;
- how to describe a new or existing project naturally;
- how Floppy determines project state;
- how read-only versus repository-writing environments affect execution; and
- how future conversations resume from `.floppy`.

### Gemini

Explain:

- supported project/file/workspace access methods current at the time of release;
- repository or local-workspace preparation;
- use of the universal Floppy prompt;
- onboarding behavior; and
- manual administrator steps where direct repository operations are unavailable.

### Grok

Explain:

- normal conversational use;
- public repository/file workflows;
- API/developer workflows when applicable;
- use of the canonical prompt;
- repository preparation; and
- manual write/application boundaries.

### DeepSeek

Explicitly support manual and partially connected workflows.

The guide must explain how users can provide:

- public repository references where available;
- uploaded files;
- source files;
- configuration;
- directory descriptions;
- `.floppy` state; and
- BCE exports.

DeepSeek or an equivalent provider does not need direct repository-write capability to be considered compatible with Floppy.

### Other AI

Provide a generic compatibility guide based on capability class rather than provider brand.

The guide should help the user determine:

```
Can this model read my project directly?
Can it write?
Can it receive uploaded project files?
Can it return files or exact changes?
Can it follow Floppy's authority boundaries?

```

If those questions can be answered sufficiently, Floppy should be usable without requiring a provider-specific implementation.

## Claude / Anthropic

V2 will not provide a maintainer-specific Claude/Anthropic onboarding guide.

The technical documentation should state neutrally that no maintainer-tested provider-specific onboarding is supplied.

A user who independently chooses that platform may use the generic `Other-AI` compatibility instructions.

No personal account dispute or provider-policy history belongs in the normative technical documentation.

---

# 10. Provider Documentation Freshness

AI-provider interfaces change independently of Floppy.

Therefore provider documentation must not become normative lifecycle law.

At implementation and release time, provider-specific UI paths and capabilities must be checked against currently available official provider documentation where practical.

The canonical Floppy prompt and authority model must remain provider-neutral.

Provider documentation describes transport and access.

It does not redefine Floppy.

---

# 11. Official Project Plan Artifact

V2 will introduce a formal project-plan deliverable at the end of accepted project design/onboarding.

The purpose is to create a stable project-level plan without pretending all future implementation details are knowable.

The official project plan should contain at minimum:

- project identity;
- intended observable final outcome;
- accepted scope;
- exclusions;
- major constraints;
- verified starting state;
- important assumptions;
- known unknowns;
- architectural decisions already accepted;
- section roadmap;
- section dependencies;
- acceptance evidence expected from each section;
- deferred work;
- explicitly rejected work;
- migration/deployment considerations where applicable;
- project-level risks;
- authority model; and
- first proposed work section.

## Adaptability rule

The official project plan defines:

**what must be accomplished and how completion will be demonstrated.**

It does not need to dictate every implementation technique for sections that have not begun.

Later implementation may adapt to newly discovered technical facts provided that:

- the accepted project outcome is preserved;
- scope changes are explicitly handled;
- accepted-state rules are respected;
- section acceptance criteria remain satisfied or are lawfully revised; and
- hidden scope expansion does not occur.

---

# 12. V2 Work-Package Plan

V2 is intentionally bounded to five major work packages.

No V2-06 or later package is assumed by this plan.

Additional work requires explicit administrator revision of the project plan.

---

## V2-01 — V2 Architecture and Compatibility Contract

### Objective

Define the exact legal relationship between v1 and v2 before implementation begins.

### Required deliverables

- V2 architecture specification.
- V1 compatibility contract.
- V1→V2 migration/adoption rules.
- Confirmation of which v1 lifecycle concepts remain unchanged.
- Definition of new v2 record families required by later sections.
- Defined provider-capability semantics.
- Defined accepted-state protection semantics.
- Defined Continuity Overseer authority boundaries.
- Defined official project-plan artifact semantics.
- Exact schema/version strategy.
- Exact validation impact assessment.
- Exact package-profile impact assessment.

### Required compatibility decisions

V2-01 must determine:

- whether a v1 project can continue without migration;
- when migration is required;
- whether migration may be deferred;
- how old accepted state remains authoritative;
- how newly introduced v2 records are initialized;
- whether schema versions remain mixed or are upgraded as a coherent bundle; and
- how a v1 BCE is recognized by v2 tooling.

### Acceptance evidence

- no implementation ambiguity remains for V2-02 through V2-05;
- no silent v1 state conversion is required;
- no accepted v1 disposition is rewritten;
- all proposed new state has an explicit owner and lifecycle role;
- exact version/schema compatibility rules are reviewable.

### Dependency

None.

V2-01 must close before implementation of later v2 capabilities begins.

---

## V2-02 — User Onboarding and Provider-Independent Adoption

### Objective

Make Floppy usable by a person who has never seen the system before and make that entry path independent of any single AI provider.

### Required deliverables

- canonical universal starter prompt;
- formal user-onboarding flow;
- automatic route determination for:
  - idea only;
  - existing non-Floppy project;
  - existing Floppy project;
- capability-class model;
- ChatGPT guide;
- Gemini guide;
- Grok guide;
- DeepSeek guide;
- generic Other-AI guide;
- public Getting Started landing page;
- clear separation between user onboarding and Floppy 1E project onboarding;
- tests or validation sufficient to prove canonical prompt/reference integrity where appropriate.

### Required user experience

A first-time user must be able to:

```
find Floppy
→ copy one prompt
→ open an AI conversation
→ describe project normally
→ be routed to the correct starting process

```

The user must not need to study Floppy internals first.

### Acceptance evidence

- all maintained provider guides use the same canonical Floppy semantics;
- provider-specific access instructions do not create provider-specific authority rules;
- Class A/B/C workflows are documented;
- existing-project preservation is explicit;
- onboarding never silently authorizes implementation.

### Dependency

V2-01.

---

## V2-03 — Accepted-State Continuity Protection

### Objective

Prevent context loss, model replacement, or re-onboarding from silently destroying or reconstructing accepted state.

### Required deliverables

- normative accepted-state protection semantics;
- revision/supersession pathway;
- required historical evidence model;
- validator enforcement;
- tests for illegal reconstruction;
- tests for lawful revision;
- tests preserving historical dispositions;
- compatibility behavior for v1 accepted records.

### Required rejection cases

Validation must reject or otherwise stop unauthorized attempts to:

- overwrite protected accepted records;
- reinterpret accepted historical dispositions;
- restart completed onboarding as if no acceptance exists;
- silently replace accepted roadmaps;
- silently regenerate closed work;
- infer acceptance from implementation completion;
- infer implementation authority from acceptance;
- use missing conversation context as revision authority.

### Acceptance evidence

A fresh model must be able to read protected accepted state but must be unable to replace it without the lawful revision pathway.

### Dependency

V2-01.

---

## V2-04 — Continuity Overseer and Orchestrator Succession

### Objective

Add project-level continuity across project-orchestrator lifetimes.

### Required deliverables

- Continuity Overseer specification;
- machine-readable Continuity Overseer state/registry as required by V2-01;
- orchestrator succession protocol;
- outgoing-orchestrator handoff requirements;
- incoming-orchestrator readiness protocol;
- exact checkpoint preservation;
- unresolved-work preservation;
- accepted-state linkage;
- administrator decision points;
- validator enforcement;
- working examples/tests.

### Required invariants

- at most one active Continuity Overseer where that role is enabled;
- at most one active project orchestrator unless an explicitly defined transition state allows otherwise;
- orchestrator replacement does not create implementation authority;
- a replacement orchestrator cannot silently reinterpret accepted state;
- repository writer remains separately controlled;
- handoff preserves exact repository checkpoint and authority state;
- Continuity Overseer may identify next legal action but may not impersonate administrator acceptance.

### Context-window handoff

V2 must support the ordinary case in which an orchestrator is replaced simply because its useful conversation context has become saturated.

That must be treated as an expected continuity event, not a project restart.

### Acceptance evidence

A test project must be able to:

```
Orchestrator A active
→ bounded handoff prepared
→ Orchestrator A retired
→ Orchestrator B loaded
→ B reconstructs exact project state
→ no accepted work recreated
→ no authority changes
→ project continues

```

### Dependency

V2-01 and V2-03.

---

## V2-05 — Official Project Plan, Integration, Compatibility Validation, and V2 Release

### Objective

Complete the design-to-execution handoff capability, integrate all v2 additions, prove compatibility, and publish v2.0.0.

### Required deliverables

- official project-plan artifact;
- generation/validation rules;
- Floppy 1E integration where required;
- Floppy Z/Continuity Overseer integration where required;
- full user documentation;
- package-profile updates if required;
- schema integration;
- source validator integration;
- `floppyctl` integration where required;
- migration/adoption command or procedure if required by V2-01;
- complete v1 compatibility testing;
- complete v2 repository test suite;
- release documentation;
- version update to `2.0.0`;
- public `v2.0.0` release.

### Required end-to-end proofs

#### New user proof

```
new user
→ universal starter prompt
→ project described naturally
→ correct starting state identified
→ Floppy project onboarding
→ accepted official project plan
→ first work section remains inactive until separately authorized

```

#### Existing project proof

```
existing codebase
→ inspected before unnecessary questions
→ existing work preserved
→ Floppy adopted
→ project plan generated
→ implementation remains separately authorized

```

#### Existing v1 Floppy project proof

```
v1 project
→ recognized
→ historical accepted state preserved
→ explicit v2 adoption/migration route if required
→ no silent rewriting

```

#### Orchestrator continuity proof

```
active project
→ orchestrator handoff
→ Continuity Overseer preserves project state
→ new orchestrator resumes
→ no project restart

```

#### Provider-independence proof

Equivalent lifecycle outcomes must be possible through:

```
Class A — direct repository operation
Class B — read/direct analysis + administrator-applied writes
Class C — file/manual exchange

```

### Dependency

V2-02, V2-03, and V2-04.

---

# 13. Explicit V2 Non-Goals

Unless separately accepted by the administrator, v2 does not include:

- replacing GitHub as the canonical source host;
- building a desktop GUI;
- building a Windows executable or installer;
- requiring ordinary users to install a dedicated Floppy application;
- autonomous project implementation without administrator authority;
- hidden monitoring of AI conversations;
- AI-provider account management;
- private-conversation inspection;
- automatic credential access;
- automatic production deployment;
- automatic authority transfer;
- automatic section acceptance;
- automatic migration of v1 state;
- replacing Floppies A-E merely for naming or aesthetic reasons;
- redesigning BCE from scratch;
- rebuilding working v1 validators without demonstrated need;
- provider-specific forks of Floppy;
- an Anthropic/Claude-specific maintainer guide; or
- an assumed V2-06+ development program.

---

# 14. Development Repository Strategy

V2 development must not be performed as uncontrolled edits to public `main`.

Preferred development model:

```
public main
c8b40bb248336990da9112dd1b6b20de154572c5
        │
        ▼
dedicated v2 feature branch
        │
        ▼
V2-01 → V2-05
        │
        ▼
validated clean integration
        │
        ▼
main
        │
        ▼
v2.0.0

```

Proposed branch name:

```
feature/v2-continuity-onboarding

```

Proposed local worktree:

```
D:\A\Floppy-V2

```

Neither is created or authorized merely by this plan.

The administrator must explicitly accept the plan and subsequently authorize the appropriate setup operation.

The existing v1 development/audit history must remain preserved.

---

# 15. Development Authority Model

The v2 project plan does not authorize repository mutation.

Each work package must preserve the v1 distinction between:

```
preparation
acceptance
activation
implementation
verification
administrator acceptance
closeout

```

Where v2 legitimately simplifies lifecycle mechanics, that simplification itself must first be designed and accepted.

No orchestrator may infer implementation authority from project-plan acceptance.

---

# 16. V2 Completion Criteria

Version 2 is complete only when all of the following are true:

- V2-01 through V2-05 are closed.
- No additional work package remains implicitly required.
- V1 historical state remains preserved.
- The `v1.0.0` tag remains unchanged.
- User onboarding is publicly documented.
- ChatGPT onboarding is documented.
- Gemini onboarding is documented.
- Grok onboarding is documented.
- DeepSeek onboarding is documented.
- Generic Other-AI onboarding is documented.
- Provider capability classes are implemented/documented.
- Accepted-state continuity protection is validated.
- Continuity Overseer behavior is validated.
- Orchestrator succession is validated.
- Official project-plan generation is validated.
- Existing v1 Floppy projects have a proven compatibility/adoption path.
- Source validation passes.
- Repository tests pass.
- package/source validation passes where applicable.
- tracked machine-readable records validate.
- source repository boundaries remain correct.
- no root project-specific `.floppy` state is unintentionally integrated into reusable `main`.
- `VERSION` and release metadata identify `2.0.0`.
- `v2.0.0` is tagged from the exact accepted final `main`.
- the public GitHub release is created.
- no active work authorization remains.
- no repository writer remains active.
- the v2 project is finally closed.

---

# 17. Final V2 Outcome

When version 2 is complete, a person unfamiliar with Floppy should be able to discover the repository, choose their AI environment, paste one canonical starter prompt, describe their project naturally, and enter a controlled project workflow without first learning Floppy's internal vocabulary.

During long projects, replacement AI orchestrators should be able to inherit exact accepted state without restarting the project or silently rebuilding accepted work.

The repository—not the lifespan of a particular AI conversation—remains the durable source of project continuity, authority, and accepted state.

That is the intended Floppy Project Interaction System v2.0 outcome.
