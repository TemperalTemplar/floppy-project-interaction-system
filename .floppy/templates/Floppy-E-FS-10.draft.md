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
Maximum reusable-product paths: 4 per accepted real migration path
Commit limit: 1 reusable-product commit per accepted real migration path
Product-scope rule: At most three implementation/test paths plus one qualifying
real adopting-project source-format fixture per accepted migration path.
```

## High-level objective

Determine whether an actual prior Floppy format used by a real adopting project
requires a targeted migration into an exact accepted destination format.

FS-10 owns only evidence-backed migration from an existing real source state.

FS-10 does not own:

- new-project provisioning;
- project initialization;
- creation of `.floppy/lifecycle-state.json`;
- creation of `.floppy/orchestrator-registry.json`;
- project-seed establishment;
- generic control-record reconciliation;
- split-brain prevention outside an accepted migration path; or
- one-time repair of the self-hosted source repository.

No migration may be invented merely because migration was anticipated on the
roadmap.

If no qualifying real migration path is proven, FS-10 may close after
verification with no reusable-product changes.

## Migration-path acceptance prerequisite

No implementation-bearing migration path may be accepted unless repository
evidence provides a qualifying real adopting-project source-format fixture and
proves all required path facts, including:

- the actual existing source format or project state;
- the exact destination format or state;
- the affected project class;
- why normal initialization or provisioning cannot handle it;
- exact files or records involved;
- deterministic compatibility detection;
- source preconditions;
- destination postconditions;
- exact authority requirements;
- dry-run requirements;
- backup and rollback boundaries;
- interruption and failure behavior;
- preservation of unrelated content;
- exact prohibited side effects; and
- why the transformation belongs in FS-10.

When no qualifying path exists, only a verification-only no-change closeout
package may be prepared. That package must name no reusable-product paths,
authorize no implementation, and create no product commit.

## Product-scope boundary

Reusable-product paths, tests, fixture paths, and product commits must not be
named before a qualifying real migration path is evidence-backed and accepted.

For each accepted real migration path:

- the maximum reusable-product scope is four paths;
- the scope may contain at most three implementation/test paths and one
  qualifying real adopting-project source-format fixture; and
- the maximum reusable-product commit count is one.

One accepted migration path does not widen another path.

## FS-09 and real-project boundary

TR-004 remains prohibited from real-project use.

FS-10 does not authorize:

- creation or provisioning of `.floppy/lifecycle-state.json`;
- creation or establishment of `.floppy/orchestrator-registry.json`;
- application of TR-004 to a real repository;
- project-control reconciliation;
- modification of the self-hosted root control state; or
- modification of an adopting project without an accepted migration path and
  separate exact migration authority.

## Detailed decisions deferred

Unless and until an evidence-backed real migration path is accepted, the
following remain deferred:

- exact affected project types;
- exact source and destination states;
- exact create, replace, or delete operations;
- compatibility detection;
- source preconditions;
- destination postconditions;
- authority format;
- dry-run behavior;
- backup contents;
- rollback boundaries;
- interruption and partial-failure handling;
- unrelated-content preservation;
- prohibited side effects;
- dependency decisions;
- reusable-product paths;
- tests;
- fixture path;
- product commit scope;
- production or deployment behavior; and
- user-facing delivery behavior.

Draft creation does not resolve any deferred implementation decision.

## Explicit prohibitions

This draft does not:

- accept or activate FS-10;
- authorize migration;
- authorize provisioning or initialization;
- create `.floppy/lifecycle-state.json`;
- create `.floppy/orchestrator-registry.json`;
- modify an adopting project;
- modify the self-hosted root control state;
- apply TR-004 to a real repository;
- name reusable-product paths before a migration path is proven;
- authorize a product commit;
- authorize push, merge, integration, tag, release, packaging, installation, or
  production activity;
- add dependencies;
- create a generalized migration framework, migration language, plugin system,
  hypothetical version matrix, transaction framework, or separate rollback
  framework; or
- claim that the finished no-Python Windows release is complete.

Python may remain an internal implementation language and may remain in the
source repository. The finished Windows release must not require ordinary users
to install Python, configure PATH, download loose `.py` files, or manually
execute Python commands. Temporary Python runners remain administrator-side
construction tools only.
