# FS-01 Formal Lifecycle and State-Transition Specification

## Status and boundary

This document is the formal FS-01 lifecycle specification for the Floppy Project
Interaction System.

It defines lifecycle vocabulary, state dimensions, invariants, transition
identifiers, transition requirements, and forbidden implications.

It does not:

- execute or apply a transition;
- write lifecycle state;
- grant human authority;
- create normative FS-02 schemas;
- perform full JSON Schema validation;
- implement `floppyctl`;
- migrate an adopting project;
- authorize integration, merge, tag, release, or later-section work.

The machine-readable companion is:

`specs/lifecycle-transition-table.json`

That table is declarative only. A conforming reader may inspect it, compare it,
or validate its internal structure. A reader must not treat the table as an
instruction to perform a transition.

## Core rule

No lifecycle state, artifact, completion record, verification result, or human
decision silently implies another lifecycle state or decision.

Every state change requires one explicit transition record and the exact human
authority named by that transition.

## Orthogonal lifecycle dimensions

The lifecycle model separates these dimensions:

| Dimension | Purpose |
|---|---|
| `roadmap` | Whether onboarding is still required or the development roadmap is accepted |
| `work_package` | Whether a section work package is accepted as a planning baseline |
| `authority` | Whether exact implementation or migration authority exists |
| `implementation` | Whether authorized implementation is not started, in progress, or complete |
| `verification` | Whether required verification is not started, pending, complete, or failed |
| `acceptance` | Whether administrator acceptance is pending, accepted, or rejected |
| `closeout` | Whether closeout is not proposed, proposed, or applied |
| `migration` | Whether migration is absent, planned, authorized, applied, or verified |
| `final_closure` | Whether the project is open, proposed for final closure, or finally closed |

These dimensions are orthogonal. Changing one dimension does not change another
unless an explicit transition names both dimensions in `changed_dimensions`.

For example:

- roadmap acceptance does not create implementation authority;
- work-package acceptance does not activate a section;
- implementation completion does not complete verification;
- verification completion does not create administrator acceptance;
- section acceptance does not apply closeout;
- section closeout does not authorize the next section;
- migration application does not complete migration verification;
- a final-closure proposal does not finally close the project.

## Authority dimension

Authority values are:

- `NO_ACTIVE_WORK_AUTHORIZATION`
- `EXACT_SECTION_IMPLEMENTATION_AUTHORIZATION`
- `EXACT_MIGRATION_AUTHORIZATION`

An exact section implementation authorization must identify at least:

- the section;
- repository;
- accepted base checkpoint;
- source version;
- implementation branch;
- implementation worktree;
- exact file scope;
- required validation;
- required commit sequence;
- push boundary;
- prohibited side effects.

An exact migration authorization must identify at least:

- accepted migration plan;
- affected targets;
- pre-migration checkpoint;
- backups;
- rollback boundary;
- exact migration operations;
- verification;
- prohibited side effects.

Absence of exact authority means no write, commit, push, migration, closeout
application, integration, or later-section activation may be inferred.

## One-active-section invariant

At most one implementation section may be active.

The machine rule is:

```text
active_implementation_section_count <= 1
```

When `active_implementation_section` is not null, the authority dimension must be
`EXACT_SECTION_IMPLEMENTATION_AUTHORIZATION`, and the named section must match
the exact authorization.

A project in `FINALLY_CLOSED` state must have:

```text
authority == NO_ACTIVE_WORK_AUTHORIZATION
active_implementation_section == null
```

## Lifecycle state identifiers

The formal state identifiers are:

| Identifier | Meaning |
|---|---|
| `LC-ONBOARDING-REQUIRED` | Roadmap not accepted and no active work |
| `LC-ROADMAP-ACCEPTED-NO-ACTIVE-WORK` | Roadmap accepted but no work package or authority |
| `LC-WORK-PACKAGE-ACCEPTED-NO-ACTIVE-WORK` | Planning baseline accepted but implementation unauthorized |
| `LC-SECTION-AUTHORIZED-NOT-STARTED` | Exact section authority exists but implementation has not started |
| `LC-SECTION-IMPLEMENTATION-IN-PROGRESS` | Authorized implementation is active |
| `LC-IMPLEMENTATION-COMPLETE-VERIFICATION-PENDING` | Implementation complete but verification pending |
| `LC-VERIFICATION-COMPLETE-ACCEPTANCE-PENDING` | Verification complete but administrator acceptance pending |
| `LC-SECTION-ACCEPTED-CLOSEOUT-NOT-PROPOSED` | Section accepted but closeout not proposed |
| `LC-SECTION-ACCEPTED-CLOSEOUT-PROPOSED` | Closeout proposed but not applied |
| `LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE` | Section closed and no later section authorized |
| `LC-MIGRATION-PLANNED-NOT-AUTHORIZED` | Migration plan exists without migration authority |
| `LC-MIGRATION-AUTHORIZED-NOT-APPLIED` | Exact migration authority exists but migration not applied |
| `LC-MIGRATION-APPLIED-VERIFICATION-PENDING` | Migration applied but verification pending |
| `LC-MIGRATION-APPLIED-VERIFICATION-COMPLETE` | Migration applied and verified |
| `LC-PROJECT-CLOSURE-PROPOSED` | Final closure proposed but not applied |
| `LC-PROJECT-FINALLY-CLOSED` | Administrator applied final closure |

The state identifiers are snapshots of all lifecycle dimensions. They do not
replace the dimensions and must not be used to infer an unnamed transition.

## Transition identifiers

The formal transitions are:

| Identifier | Transition |
|---|---|
| `TR-001-ACCEPT-ROADMAP` | Accept the development roadmap |
| `TR-002-ACCEPT-WORK-PACKAGE` | Accept a section work package as a planning baseline |
| `TR-003-AUTHORIZE-SECTION-IMPLEMENTATION` | Issue exact section implementation authority |
| `TR-004-START-SECTION-IMPLEMENTATION` | Start implementation within existing exact authority |
| `TR-005-RECORD-IMPLEMENTATION-COMPLETE` | Record implementation completion with verification pending |
| `TR-006-RECORD-VERIFICATION-COMPLETE` | Record verification completion with acceptance pending |
| `TR-007-ACCEPT-SECTION` | Administrator accepts the verified section |
| `TR-008-PROPOSE-SECTION-CLOSEOUT` | Propose closeout for an accepted section |
| `TR-009-APPLY-SECTION-CLOSEOUT` | Administrator applies section closeout |
| `TR-010-PLAN-MIGRATION` | Record a non-authorizing migration plan |
| `TR-011-AUTHORIZE-MIGRATION` | Issue exact migration authority |
| `TR-012-APPLY-MIGRATION` | Apply a migration within exact authority |
| `TR-013-VERIFY-MIGRATION` | Record migration verification completion |
| `TR-014-PROPOSE-FINAL-CLOSURE` | Propose final project closure |
| `TR-015-APPLY-FINAL-CLOSURE` | Administrator applies final project closure |

The machine-readable transition record for each identifier contains:

- `from_state_ids`;
- `to_state_id`;
- `changed_dimensions`;
- `preconditions`;
- `required_human_authority`;
- `required_inputs`;
- `required_outputs`;
- `stop_conditions`;
- `forbidden_side_effects`.

A transition is invalid if any required field is absent, if a referenced state
identifier is unknown, or if the same transition identifier appears more than
once.

## Drafting, acceptance, activation, completion, and closeout

These events are distinct:

1. Drafting creates a proposal only.
2. Roadmap acceptance accepts roadmap structure only.
3. Work-package acceptance accepts a planning baseline only.
4. Section authorization grants exact bounded implementation authority.
5. Activation records that the authorized section is the one active section.
6. Implementation start begins writes within that exact authority.
7. Implementation completion records that authorized outputs exist.
8. Verification completion records that required checks passed.
9. Administrator acceptance accepts the verified result.
10. Closeout proposal prepares a reviewable closeout record.
11. Closeout application closes the accepted section.
12. Later-section authorization requires a separate exact human decision.

No step in this sequence may be skipped by implication.

## Stop conditions

Every transition defines transition-specific stop conditions. The following
conditions always stop lifecycle progression:

- stale or mismatched base checkpoint;
- missing exact human authority;
- missing exact file or target scope;
- more than one active implementation section;
- dirty worktree when a clean worktree is required;
- unresolved failed verification;
- unauthorized file, target, side effect, commit, or push;
- missing required input or output;
- final project closure combined with active implementation or migration authority.

A stop condition preserves the prior accepted state. It does not authorize an
automatic repair, rollback, migration, or alternate transition.

## Forbidden side effects

Unless an explicit authorization separately names them, all transitions forbid:

- modifying canonical `main`;
- integrating, merging, tagging, or releasing;
- modifying an adopting project;
- modifying reusable project seed content;
- activating a later section;
- widening file or target scope;
- changing source version;
- applying a migration;
- writing lifecycle state through an executable transition engine;
- deleting or compacting history;
- treating a proposal as applied;
- treating implementation completion as administrator acceptance.

## Declarative transition table

`specs/lifecycle-transition-table.json` is data, not an executor.

The table contains:

```text
declarative_only: true
execution_capability: false
applies_transitions: false
writes_lifecycle_state: false
production_schema_enforcement: false
```

FS-01 permits structural and integrity validation of this table. FS-01 does not
permit a tool to apply transitions, mutate a BCE, enforce future FS-02 schemas,
or create controlled lifecycle write commands.

## Relationship to FS-02 and FS-03

FS-02 may later define normative machine-readable BCE schemas only after separate
administrator authorization.

FS-03 may later define a semantic validator engine only after FS-02 is accepted,
closed, and followed by separate FS-03 authorization.

The FS-01 specification and transition table do not activate or complete either
later section.

## Verification-only lifecycle extension (1.1.0)

CTRL-02 adds the implementation disposition `NOT_REQUIRED` for accepted work packages of type `VERIFICATION_ONLY_NO_REUSABLE_PRODUCT_CHANGE`. Such a package has no reusable-product paths, no reusable-product commits, no active implementation authorization, and no repository writer.

The extension adds these states:

- `LC-VERIFICATION-ONLY-WORK-PACKAGE-ACCEPTED-PENDING`
- `LC-VERIFICATION-ONLY-COMPLETE-ACCEPTANCE-PENDING`
- `LC-VERIFICATION-ONLY-SECTION-ACCEPTED-CLOSEOUT-NOT-PROPOSED`
- `LC-VERIFICATION-ONLY-SECTION-ACCEPTED-CLOSEOUT-PROPOSED`

It adds transitions TR-016 through TR-020. TR-020 returns the current operational state to `LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE` without rewriting the closed section's accepted `NOT_REQUIRED` disposition.

### INV-010-CLOSED-SECTION-OUTCOME-PRESERVED

Applying closeout changes the current operational lifecycle position but must not rewrite the closed section's accepted implementation disposition, verification result, acceptance result, or no-product-change result.
