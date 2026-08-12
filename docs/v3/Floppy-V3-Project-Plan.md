# Floppy Project Interaction System V3 — Candidate Official Project Plan

**Target release:** `v3.0.0`  
**Repository:** `TemperalTemplar/floppy-project-interaction-system`  
**Plan status:** `DRAFT_FOR_ADMINISTRATOR_ACCEPTANCE`  
**Sections:** exactly `V3-01` through `V3-09`  
**V3-10:** `NONEXISTENT_NOT_AUTHORIZED`

> This document is a repository-backed candidate project plan. Its presence in the repository does not by itself constitute administrator acceptance, implementation authorization, migration authority, integration authority, or release authority.

## 1. V3 Mission

Floppy V3 will make the existing Floppy architecture operate more deterministically, consistently, and efficiently while preserving the Human-in-the-Loop authority model.

V3 is not intended to turn Floppy into an autonomous agent platform, permanent daemon, hosted orchestration service, or mandatory AI runtime.

The repository remains the durable source of project state, accepted authority, continuity evidence, lifecycle state, planning state, and project history. AI conversations and local tools remain temporary execution environments.

The controlling V3 principle is:

> **Human decisions stay human. Deterministic consequences of accepted human decisions should be bundled, applied consistently, and validated as atomic transactions.**

V3 therefore seeks to reduce redundant human transport and clerical work without reducing human authority.

## 2. V3 Design Laws

### V3-L1 — Human Authority Is Preserved

The following remain human decisions unless an already-accepted policy explicitly establishes otherwise:

- project-goal acceptance;
- material scope change;
- material architecture change;
- security or risk acceptance;
- meaningful cost commitment;
- work-package or section authorization;
- administrator acceptance;
- project-level revision acceptance;
- Project Orchestrator succession acceptance;
- migration approval;
- integration approval where required;
- release approval;
- exception approval.

AI reasoning may support those decisions but may not silently manufacture them.

### V3-L2 — Deterministic Consequences Should Be Bundled

Once the administrator has made an accepted decision, Floppy should not require the administrator to manually repeat every mechanical consequence.

Examples include:

- version propagation;
- manifest projections;
- lifecycle projections;
- accepted-state linkage;
- evidence registration;
- hash generation;
- checksum generation;
- package naming;
- documentation version references;
- inactive next-section draft creation;
- closeout record synchronization;
- release-readiness records;
- succession-package construction.

One human decision may lawfully produce multiple deterministic repository changes when those consequences are explicitly defined by an accepted transaction contract.

### V3-L3 — Transactions Are Atomic

A deterministic consequence bundle must either validate and apply as a complete transaction or fail without leaving a partially updated accepted state.

Partial projection is not successful completion.

### V3-L4 — Capability Does Not Create Authority

Repository access, command execution, API access, provider features, context size, or model intelligence never create Floppy authority.

Technical capability determines how an authorized operation can be performed. Floppy state determines whether it may be performed.

### V3-L5 — Repository State Remains Recoverable Without a Runtime

V3 must remain usable with Git, repository files, standard Floppy tooling, an AI capable of reading the repository, or administrator-mediated file exchange.

No permanent Floppy server, daemon, cloud account, or AI provider may become necessary to reconstruct accepted project state.

### V3-L6 — Context Loss Is Not Authority to Reconstruct Accepted Work

The existing continuity principle remains binding:

> **Context loss is not authority to reconstruct accepted work.**

Repository-backed accepted state remains authoritative.

### V3-L7 — No Unnecessary Human Relay

The administrator must not be used as a mechanical transport layer when the responsible model can directly access the required repository evidence, the action is already authorized, the consequences are deterministic, and no material decision remains unresolved.

Human interruption should occur for meaningful decisions, not repetitive transcription.

### V3-L8 — No Invented Gates

Models may not introduce speculative audits, approval gates, security reviews, tests, lifecycle states, migration requirements, work packages, or administrator decisions merely because they appear prudent.

Additional requirements require actual evidence, accepted policy, or administrator direction.

### V3-L9 — Terminal Delivery Has an Owner

Implementation completion alone is not project completion.

Every work package and the final V3 project must have a deterministic ownership path through:

`implementation → verification → acceptance → closeout → integration → release → final closure`

as applicable.

No terminal obligation may become orphaned between AI roles.

## 3. Compatibility Boundary

V3 will preserve the established V2 architectural foundation unless a V3 section explicitly and lawfully changes a defined contract.

Protected V2 concepts include:

- BCE;
- repository-backed project state;
- Human-in-the-Loop authority;
- accepted-state protection;
- Official Project Plan;
- lifecycle separation;
- explicit work authorization;
- repository-writer separation;
- Continuity Overseer;
- Project Orchestrator;
- Section Working Model;
- orchestrator succession;
- provider independence;
- project/source repository separation;
- deterministic validation;
- release packaging;
- immutable released tags.

The immutable `v2.0.0` release remains a compatibility reference. V3 development may proceed from the current post-V2 `main` state rather than rewriting `v2.0.0`.

Existing V2 projects must not be silently migrated or rewritten merely because V3 exists.

## 4. Administrator Local Environment — Binding

The administrator's established Windows environment is part of the V3 operating constraints.

### Development drive

Repository development worktrees belong under:

`D:\A\`

Use the exact repository-recorded V3 worktree once it is lawfully established. Do not invent, guess, normalize, or substitute another worktree path.

A path such as `D:\A\Floppy-V3` must not be assumed until it is actually established and recorded.

### Exact Python interpreter

Python installation:

`D:\A\Tools\Python313`

Required interpreter:

`D:\A\Tools\Python313\python.exe`

Administrator-local Python commands must use that exact interpreter. Do not substitute `python`, `python3`, `py`, Microsoft Store Python, or another interpreter unless the administrator explicitly changes this rule.

### Exact Downloads directory

Administrator Downloads directory:

`C:\Users\alvar.TERMINAL1\Downloads\`

Any script, helper, checksum file, execution runner, administrator-transfer package, or other artifact intended for manual administrator download/execution must use this exact directory unless the administrator explicitly specifies another destination.

### Path separation

```text
D:\A\
    repository worktrees and development repositories

D:\A\Tools\Python313\python.exe
    administrator Python execution

C:\Users\alvar.TERMINAL1\Downloads\
    administrator-transfer scripts and artifacts
```

The Downloads directory must not silently become the project worktree.

## 5. V3 Section Roadmap

| Section | Name | Primary outcome |
|---|---|---|
| V3-01 | Architecture and Compatibility Contract | Freeze the V3 design laws and V2 compatibility boundary |
| V3-02 | Terminal Delivery Contract | Ensure every work package has explicit end-to-end delivery ownership |
| V3-03 | Role Capability Contracts | Formalize what each Floppy role may read, decide, prepare, write, and verify |
| V3-04 | Deterministic Context and Retrieval Profile | Define bounded context selection without requiring a permanent runtime |
| V3-05 | Project Orchestrator Succession V3 | Make succession deterministic, verifiable, and low-friction |
| V3-06 | Human-Authority Transaction Bundles | Bundle deterministic consequences of accepted human decisions |
| V3-07 | `floppyctl status` and Project-State Inspection | Provide one canonical project-status and next-operation surface |
| V3-08 | Release Automation and Consistency Validation | Automate packaging and detect cross-artifact contradictions |
| V3-09 | Integration, Compatibility, Documentation, Packaging, and V3 Release | Deliver, publish, and finally close V3 |

# V3-01 — Architecture and Compatibility Contract

## Purpose

Establish the controlling V3 architecture before implementation begins and prevent later sections from gradually redefining V3 into an autonomous orchestration platform or weakening existing Human-in-the-Loop boundaries.

## Required work

Define:

- V3 mission;
- V3 design laws;
- protected V2 behaviors;
- compatibility expectations;
- human-only decision classes;
- deterministic-consequence classes;
- AI-recommendation classes;
- transaction terminology;
- repository/runtime boundary;
- V3 versioning rules;
- migration boundary;
- release compatibility expectations.

Create a formal authority classification for `HUMAN_DECISION`, `DETERMINISTIC_CONSEQUENCE`, and `AI_ASSISTED_REASONING`.

## Deliverables

- V3 architecture specification;
- V3 compatibility profile;
- human-authority/transaction specification;
- machine-readable compatibility representation where useful;
- validation fixtures for compatibility rules.

## Acceptance criteria

V3-01 is complete only when the Human-in-the-Loop boundary is explicit, deterministic bundling is defined without creating autonomous authority, V2 compatibility is documented, no permanent runtime is required, migration is not silently implied, and the remaining sections can rely on stable definitions.

## Dependency

None beyond the accepted V2/post-V2 baseline.

# V3-02 — Terminal Delivery Contract

## Purpose

Eliminate terminal-delivery gaps in which a Working Model completes implementation while integration, release, documentation, packaging, or final closeout becomes orphaned.

## Required work

Define terminal states and responsibility across implementation, verification, administrator acceptance, section closeout, integration, compatibility verification, documentation reconciliation, package creation, tag, public release, and final project closure.

Every authorized work package must identify:

- implementation owner;
- verification owner;
- acceptance authority;
- closeout owner;
- next handoff recipient;
- terminal obligations;
- conditions under which responsibility ends.

Distinguish section completion, product/release completion, and final project closure.

## Required terminal handoff

When a model's responsibility ends before the project is terminally complete, it must leave a machine/human-readable handoff identifying exact completed responsibility, checkpoint, unresolved terminal obligations, next responsible role, next lawful operation, and prohibited operations.

## Acceptance criteria

Tests must cover normal Working Model completion, verification handoff, administrator acceptance pending, integration pending, release pending, interrupted terminal responsibility, successor recovery, and final closure. No tested required terminal obligation may exist without a determinable responsible role.

# V3-03 — Role Capability Contracts

## Purpose

Formalize the responsibilities of each role so models neither overstep nor stop unnecessarily.

## Required roles

- Administrator / Project Authority;
- Continuity Overseer;
- Project Orchestrator;
- Section Working Model;
- onboarding role / Floppy 1E;
- integration/release working mode as a bounded operational mode rather than a new permanent authority role.

## Capability matrix

For every role define:

- may read;
- may reason;
- may recommend;
- may prepare;
- may verify;
- may write;
- may commit;
- may apply lifecycle transactions;
- may accept;
- may authorize;
- may release;
- may perform succession;
- prohibited operations.

A role and a technical capability are separate. `repository_write = true` does not imply repository-writer authorization.

## Acceptance criteria

The contracts must make human decisions, deterministic operations, writer authority, implementation responsibility, coordination responsibility, continuity responsibility, and terminal ownership unambiguous. Cross-role tests must reject prohibited authority inheritance.

# V3-04 — Deterministic Context and Retrieval Profile

## Purpose

Reduce unnecessary context loading while preserving reliable reconstruction. This remains repository-native and does not require a vector database, cloud RAG service, daemon, or persistent AI runtime.

## Context levels

### Level 0 — Bootstrap Identity

Minimum records necessary to identify project, Floppy version, accepted project ID, current lifecycle, Official Project Plan, role, and current checkpoint.

### Level 1 — Current Operational Context

Current section, authorization, writer, Project Orchestrator, Working Model, dependencies, immediate evidence, and next lawful operation.

### Level 2 — Relevant Accepted Context

Only accepted architecture decisions, project-plan portions, unresolved issues, or prior-section evidence relevant to the present task.

### Level 3 — Historical Retrieval

Older accepted sections, superseded plans, succession records, historical evidence, previous Orchestrators, and deep project history, loaded only when needed.

## Retrieval rules

Define required read order, stop conditions, expansion conditions, reference following, stale-record rejection, accepted-record precedence over conversation memory, and conditions requiring deeper history.

## Optional future compatibility

The representation should be capable of later export/indexing for RAG or vector retrieval, but V3 must not require such infrastructure.

## Acceptance criteria

Two fresh compatible models given the same repository state and role should identify substantially the same required context set and authority state. Full-repository loading must not be the default when bounded context is sufficient.

# V3-05 — Project Orchestrator Succession V3

## Purpose

Turn Project Orchestrator replacement into a deterministic, low-friction, repository-backed handoff.

## Required succession bundle

Capture:

- project identity;
- accepted-state revision;
- Official Project Plan revision;
- Continuity Overseer identity;
- outgoing Project Orchestrator identity;
- proposed successor identity;
- lifecycle state;
- active section;
- current authorization;
- repository writer;
- current Working Model;
- exact repository checkpoint;
- unresolved obligations;
- terminal-delivery obligations;
- next lawful operation;
- authority fingerprint.

## Continuity Overseer function

The Overseer verifies the succession bundle against current repository state. If authority or checkpoint state changes before application, stop with `STALE_SUCCESSION_HANDOFF`.

## Human decision

The administrator retains the decision to replace or accept a Project Orchestrator.

## Deterministic consequences

After that decision, Floppy may bundle outgoing status update, incoming registration, succession history, fingerprint linkage, successor bootstrap generation, manifest projection, and validation without requiring separate human approval for each mechanical consequence.

## Acceptance criteria

Test normal succession, stale checkpoint, changed authorization, predecessor unavailable, active/no-active Working Model, terminal-delivery handoff, double-active Orchestrator rejection, and attempted automatic authority transfer.

# V3-06 — Human-Authority Transaction Bundles

## Purpose

Implement the central V3 efficiency model: human decisions remain discrete while their deterministic repository consequences become bounded transactions.

## Transaction requirements

Every transaction must define:

- triggering accepted decision;
- exact allowed pre-state;
- exact affected records;
- deterministic calculations;
- validation;
- resulting state;
- rollback/failure behavior;
- forbidden side effects.

## Candidate transaction families

### Section Authorization Bundle

After explicit section authorization: authority record, lifecycle projection, current-work projection, writer state only if explicitly included, manifest projection, and validation.

### Administrator Acceptance Bundle

After explicit acceptance: acceptance record, accepted-state projection where applicable, evidence linkage, lifecycle projection, and manifest consistency.

### Section Closeout Bundle

After lawful closeout: closeout record, roadmap status, accepted history, inactive next-section draft when applicable, writer deactivation, authorization clearing, and manifest/lifecycle synchronization.

### Version Bundle

After an accepted release-version decision: `VERSION`, manifest version, public documentation version references, package version names, release metadata, and compatibility metadata.

### Succession Bundle

Apply V3-05 deterministic consequences after administrator succession acceptance.

### Release Preparation Bundle

Prepare deterministic release artifacts after release-candidate preparation is authorized.

## Atomicity

A failed transaction must not leave part of accepted state updated. Dry-run inspection should be available where practical.

## Acceptance criteria

For every supported transaction, same input state plus same accepted decision must produce the same planned consequence set; unauthorized paths are rejected; partial application is rejected or rolled back; a transaction cannot create its own human authorization; and resulting state validates.

# V3-07 — `floppyctl status` and Project-State Inspection

## Purpose

Give humans and models one canonical way to understand current project state without manually opening numerous records.

## Required command

At minimum:

`floppyctl status`

with machine-readable output such as:

`floppyctl status --json`

## Required output

Where applicable:

- project name;
- project ID;
- Floppy version;
- source version;
- current repository;
- branch;
- checkpoint;
- accepted-state revision;
- Official Project Plan revision;
- Continuity Overseer;
- Project Orchestrator;
- current Section Working Model;
- repository writer;
- current section;
- work authorization;
- implementation status;
- verification status;
- administrator-acceptance status;
- closeout status;
- migration status;
- terminal-delivery owner;
- blockers;
- next lawful operation.

`next lawful operation` reports what current accepted state permits or requires; it does not automatically perform the operation.

## Acceptance criteria

Status output must derive from authoritative repository state rather than conversation memory. Contradictory records must produce conflict/invalid state rather than fabricated status.

# V3-08 — Release Automation and Consistency Validation

## Purpose

Make release preparation deterministic and prevent contradictions among code, documentation, manifests, packages, and release metadata.

## Release readiness manifest

Create a canonical representation containing target version, expected integration checkpoint/tree, release tag, source package name, validated boot-package name, package inventory, checksums, compatibility status, migration status, documentation status, test status, and administrator release-decision state.

## Cross-artifact consistency validation

Validate agreement among relevant `VERSION`, `README.md`, `BOOTSTRAP.md`, User Guide, Getting Started documentation, system manifest, compatibility profile, schemas, package inventory, release notes, source package, boot package, and intended tag/commit.

A stale prior-release reference in active V3 public instructions must be detected.

## Packaging

Provide deterministic tooling to build:

- full V3 source/distribution ZIP;
- validated V3 boot package;
- `SHA256SUMS.txt`;
- release notes;
- release-readiness report.

Package construction does not equal release approval. Public publishing remains a human decision.

## Acceptance criteria

The release system must intentionally fail tests containing mismatched version references, incorrect tag target, stale public documentation, missing/unexpected boot-package paths, incorrect checksum, manifest mismatch, release-notes mismatch, or incomplete readiness state.

# V3-09 — Integration, Compatibility, Documentation, Packaging, and V3 Release

## Purpose

Own the complete V3 terminal delivery. V3-09 is not merely a verification package; it owns the path from completed V3 implementation to a properly published and finally closed V3 product.

## Required work

### 1. Integration preparation

Confirm V3-01 through V3-08 are accepted and closed and no active unauthorized work or repository writer remains.

### 2. Compatibility validation

Validate required V2 compatibility behavior. Existing V2 project state must not be silently rewritten.

### 3. Full validation

Run focused V3 tests, regression suite, compatibility suite, schema validation, lifecycle validation, transaction tests, status tests, context/retrieval tests, succession tests, and release consistency tests.

### 4. Documentation reconciliation

Perform deterministic cross-checks of all public V3 documentation. Documentation is part of the product and must be validated before release.

### 5. Administrator product acceptance

Present the complete V3 result for required administrator acceptance.

### 6. Clean integration

Integrate accepted V3 reusable-product source into the release branch/main according to accepted repository policy. Development-control records that are not product source remain outside the product distribution.

### 7. Release preparation

Apply the accepted version bundle for `3.0.0`, build deterministic release assets, generate checksums/release notes, and validate release readiness.

### 8. Administrator release decision

Public release remains a human decision.

### 9. Release

After authorization, create/verify `v3.0.0`, verify exact tag target, publish V3 release, attach canonical assets, and verify public release state.

### 10. V3 closeout

Close V3-09 and apply final V3 project closure. No V3-10 is created.

Final state:

`V3 PROJECT FINALLY CLOSED`

and:

`V3-10 = NONEXISTENT_NOT_AUTHORIZED`

## 6. Human Decision Matrix

| Decision or operation | Human decision required? |
|---|---|
| Accept V3 Official Project Plan | YES |
| Authorize a work section | YES |
| Material goal/scope revision | YES |
| Material architecture/security/cost decision | YES |
| Administrator acceptance | YES |
| Accept Project Orchestrator replacement | YES |
| Approve migration | YES |
| Approve public release | YES |
| Apply deterministic version propagation after version accepted | NO additional decision |
| Generate hashes/checksums | NO |
| Synchronize manifest projections | NO |
| Generate a lawful handoff package | NO |
| Generate inactive next-section draft after accepted closeout | NO |
| Build authorized release packages | NO additional decision |
| Validate documentation consistency | NO |
| Report next lawful operation | NO |

## 7. V3 Completion Definition

Floppy V3 is complete only when:

1. all nine sections are accepted and closed;
2. V3 compatibility requirements pass;
3. transactional consequence bundling is implemented and tested;
4. Human-in-the-Loop authority remains explicit;
5. deterministic context retrieval is validated;
6. Project Orchestrator succession V3 is validated;
7. `floppyctl status` is operational;
8. release consistency validation passes;
9. public V3 documentation accurately describes V3;
10. canonical V3 packages are built and verified;
11. the administrator approves release;
12. `v3.0.0` is published and verified;
13. V3 final project closure is applied;
14. no V3-10 exists.

## 8. Explicit Non-Goals

V3 does not require:

- a persistent Floppy server;
- an autonomous Floppy agent;
- automatic administrator acceptance;
- automatic scope changes;
- automatic release approval;
- automatic Project Orchestrator replacement;
- provider-specific authority;
- a mandatory vector database;
- a mandatory RAG service;
- a hosted dashboard;
- continuous monitoring;
- hidden inspection of AI conversations;
- automatic conversation creation.

Those may be investigated in later independent work, but they are not part of this nine-section V3 plan.

## 9. Intended Observable Outcome

> A provider-independent, repository-native Floppy V3 system in which accepted human decisions remain the source of project authority, deterministic consequences are applied as coherent validated transactions, project context can be reconstructed selectively, Project Orchestrator succession is reliable, project state is immediately inspectable, terminal delivery responsibility cannot silently disappear, and releases can be packaged and validated without repetitive administrator clerical work.
