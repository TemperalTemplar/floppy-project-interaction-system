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
