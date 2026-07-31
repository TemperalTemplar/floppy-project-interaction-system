# Architecture and Lifecycle

## Layer 1 — Source system

The source repository contains protocols, templates, schemas, tooling, and preserved design history. It is the point of origin for new project instances.

## Layer 2 — Project control directory

Each adopting repository receives a `.floppy/` directory. This directory is project-owned and versioned with the project code. It contains the manifest, Floppies A–E, revision packets, handoffs, and narrowly selected evidence.

## Layer 3 — Session context

A new model reads the project manifest first. The manifest supplies the minimal required read order. The model then loads only additional files relevant to the active Floppy E section.

## State transitions

```text
Source seed
    -> project onboarding
    -> initial A-E acceptance
    -> intake readiness
    -> current-section authorization
    -> active work
    -> user-requested closeout
    -> delta revision packet
    -> user acceptance
    -> revision application
    -> next session
```

## Anti-bloat principles

- Manifest first, repository scan later only when needed.
- No full conversation copies as routine context.
- No regeneration of unchanged Floppies.
- Floppy A sealed after onboarding.
- Floppy C accepts only verified, user-accepted increments.
- Floppy D stores future ideas without activating them.
- Floppy E contains one bounded work section.
- Evidence appendices are optional and narrowly scoped.

## Git role

Git provides traceability, review, rollback, and section-history boundaries. It does not replace user authorization. A commit proves a recorded change, not that a project section was accepted unless the record explicitly says so.

## FS-01 formal lifecycle model

The earlier lifecycle sequence is an operational overview, not an implication
chain. FS-01 defines a formal state model in:

```text
specs/lifecycle-state-model.md
specs/lifecycle-transition-table.json
```

### Orthogonal dimensions

A lifecycle snapshot records these dimensions independently:

- roadmap;
- work package;
- human authority;
- implementation;
- verification;
- administrator acceptance;
- closeout;
- migration;
- final project closure.

An explicit transition may change only the dimensions listed in that
transition's `changed_dimensions` field. No state, artifact, commit, test result,
or draft silently changes another dimension.

### Explicit transition contract

Each formal transition identifies:

- a stable transition ID;
- permitted source and destination state IDs;
- preconditions;
- required human authority;
- required inputs;
- required outputs;
- stop conditions;
- forbidden side effects.

At most one implementation section may be active. An active section requires an
exact authorization record for that same section. A finally closed project
cannot retain active implementation or migration authority.

### Declarative-only boundary

The FS-01 transition table is data, not an execution engine. The source validator
may verify its structure, references, required fields, prohibited implications,
and registered digest. It does not:

- apply transitions;
- mutate a project BCE;
- perform full instance-schema validation;
- grant authority;
- run a migration;
- implement `floppyctl`;
- implement FS-02 or FS-03.

Git remains evidence and traceability. It does not replace the explicit human
decision required by a transition.
