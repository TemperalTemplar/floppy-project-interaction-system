STATUS: DRAFT_NOT_AUTHORIZED

# Floppy E - FS-10 Draft Work Package

## Section

`FS-10 - Targeted Migration`

## Current authority state

```text
Status: DRAFT_NOT_AUTHORIZED
Active: NO
Accepted: NO
Authorized: NO
Implementation: NOT STARTED
Active authorization: NONE
Repository writer: NONE
Writer authorization reference: NONE
Maximum reusable-product paths: 4
Commit limit: 1 per accepted real migration path
Product-scope rule: At most three implementation/test paths plus one real source-format fixture per accepted migration path.
```

## High-level objective

Inspect whether any real migration or provisioning path has been proven necessary
by an actual prior Floppy-format fixture or existing-project compatibility
evidence.

No migration may be invented merely because migration was anticipated. FS-10 may
determine that no reusable-product migration change is required.

## Evidence requirement

A migration path must be evidence-backed before implementation can be authorized.
Draft creation does not modify a real project, authorize migration, or provision
`.floppy/lifecycle-state.json`.

The TR-004 writer remains prohibited from real-project use until a separately
accepted provisioning and integration contract:

1. Establishes `.floppy/lifecycle-state.json`.
2. Defines its canonical initial state.
3. Defines precedence and consistency with existing project-control records.
4. Prevents contradictory or split-brain lifecycle state.
5. Validates existing-project compatibility.
6. Defines an authorized provisioning or migration path.
7. Provides reviewable evidence and rollback boundaries.

## Detailed decisions deferred

The following remain deferred:

- whether a real migration path exists;
- exact affected project types;
- exact source and destination states;
- exact files to create or replace;
- compatibility detection;
- precedence and reconciliation across existing lifecycle records;
- backup and rollback requirements;
- dry-run behavior;
- irreversible-action boundaries;
- dependency decisions;
- product paths;
- commit count for any accepted real migration path; and
- production or deployment behavior.

## Explicit prohibitions

This draft does not:

- accept or activate FS-10;
- authorize migration;
- provision `.floppy/lifecycle-state.json`;
- modify an adopting project;
- apply TR-004 to a real repository;
- authorize push, merge, integration, tag, release, or production activity;
- add dependencies;
- implement a generalized migration framework; or
- claim that the finished no-Python Windows release is complete.

Python may remain an internal implementation language and may remain in the source repository. The finished Windows release must not require ordinary users to install Python, configure PATH, download loose .py files, or manually execute Python commands. Temporary Python runners remain administrator-side construction tools only.
