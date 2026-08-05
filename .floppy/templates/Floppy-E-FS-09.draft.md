STATUS: ACTIVE

# Floppy E - FS-09 Corrected Draft Work Package

## Section

`FS-09 - Controlled FS-01 lifecycle writes with dry-run and atomic replacement`

## Current authority state

```text
Draft correction: APPLIED
Status: DRAFT_NOT_AUTHORIZED
Active: NO
Accepted: NO
Authorized: NO
Implementation: NOT STARTED
Active authorization: NONE
Repository writer: NONE
FS-08: CLOSED
FS-10: INACTIVE / NOT AUTHORIZED
Maximum reusable-product paths: 3
Maximum reusable-product commits: 2
```

This corrected draft records an accepted architecture design basis only. It does
not accept or activate FS-09 and does not grant implementation or repository
write authority.

## Corrective architecture traceability

```text
Corrective architecture proposal:
ACCEPTED AS FS-09 DESIGN BASIS

Accepted proposal SHA-256:
6a221e89ac49dd1478906a8c80a26c99e0d9f5037384b3bca9dc225ffdb83b41

Normative contract destination:
specs/lifecycle-write-contract.json

Required repository contract status when committed:
ACCEPTED_NORMATIVE

Current FS-09 lifecycle status:
DRAFT_NOT_AUTHORIZED

Implementation authority:
NONE

Active authorization:
NONE

Repository writer:
NONE
```

The accepted proposal SHA-256 is design-traceability evidence. It is not an
authorization token and must not be interpreted as authority to implement,
activate, apply, migrate, integrate, release, or write lifecycle state.

## Initial supported lifecycle transition

The initial FS-09 capability is limited to exactly:

`TR-004-START-SECTION-IMPLEMENTATION`

No other FS-01 transition is included in the initial capability.

The accepted source state is:

`LC-SECTION-AUTHORIZED-NOT-STARTED`

The accepted destination state is:

`LC-SECTION-IMPLEMENTATION-IN-PROGRESS`

Only the implementation lifecycle dimension may change.

## Normative reusable-product contract

The future normative product contract path is:

`specs/lifecycle-write-contract.json`

When committed under a later FS-09 implementation authorization, that contract
must identify itself as accepted and normative rather than
`PROPOSED_NOT_ACCEPTED`.

It must retain this accepted design-proposal digest for traceability:

`6a221e89ac49dd1478906a8c80a26c99e0d9f5037384b3bca9dc225ffdb83b41`

The contract file is not created by this administrative draft correction.

## Exact reusable-product scope

```text
specs/lifecycle-write-contract.json
tools/floppyctl.py
tests/test_controlled_lifecycle_writes.py
```

Maximum reusable-product paths: `3`

Maximum reusable-product commits: `2`

Administrative lifecycle commits do not count against the reusable-product
commit maximum.

No fourth reusable-product path is authorized. One reusable-product commit is
preferred unless a technically necessary separation within the two-commit
maximum is proven.

## Exact target-project lifecycle path

The sole normative target-project path for the initial capability is:

`.floppy/lifecycle-state.json`

Authorized operation:

`REPLACE_ONLY`

The target must already exist in the exact valid source state.

Unexpected absence must be rejected.

## Prohibited caller-controlled write inputs

The initial capability must not accept:

- caller-supplied target paths;
- caller-supplied JSON pointers;
- caller-supplied patches;
- caller-supplied replacement bytes;
- caller-supplied replacement documents; or
- caller-supplied alternative lifecycle targets.

The complete replacement object must be derived from the accepted normative
contract and validated repository state.

## File and operation boundary

```text
File creation:
NOT SUPPORTED

Multi-file lifecycle operations:
NOT SUPPORTED

Generalized repository transaction framework:
NOT AUTHORIZED

Migration:
NOT AUTHORIZED
```

The initial operation is a single-file replacement only.

Multi-file rollback is not applicable. Single-file post-replacement restoration
after failed final verification remains required by the accepted design basis.

## Canonical target schema

The current and proposed lifecycle-state objects must conform to:

`schemas/bce/1.0.0/bce-lifecycle-state.schema.json`

The future implementation must use deterministic UTF-8 JSON, exact preimage and
postimage SHA-256 verification, safe same-filesystem atomic replacement, and
fail-closed diagnostics as established by the accepted corrective architecture.

## Authority and writer sources

Authority source:

`.floppy/manifest.json#/active_work_authorization`

Writer source:

`.floppy/orchestrator-registry.json#/current_assignments`

Both are read-only inputs to the initial operation.

The future capability must not create, activate, widen, transfer, replace, or
clear authority. It must not register, replace, or clear a repository writer.

Authorization `exact_file_scope` may withhold permission by omitting the
normative target. It may never widen, substitute, or redefine the normative
target set.

## Phase-1 exercise boundary

```text
Real-project use during FS-09 Phase 1:
PROHIBITED

Disposable-fixture use:
AUTHORIZED FOR TESTING ONLY
```

All dry-run, apply, stale-state, unauthorized-writer, path-safety,
atomic-replacement, restoration, and failure-injection tests must use disposable
temporary fixtures or disposable temporary Git repositories.

The capability must not be used on the Floppy source repository, an adopting
project, another real repository, an external repository, production, or the
accepted FS-08 artifacts during FS-09 Phase 1.

## Provisioning and integration boundary

Real-project use remains prohibited until a later separately authorized
provisioning and integration operation establishes:

`.floppy/lifecycle-state.json`

That later operation must prevent contradictory lifecycle state across existing
project-control records, including as applicable:

- `.floppy/manifest.json`;
- `.floppy/roadmap/roadmap.json`;
- `.floppy/roadmap/roadmap.md`;
- `.floppy/floppies/Floppy-E-Current-Section.md`;
- authorization records;
- orchestrator-registry assignments;
- acceptance records;
- implementation and verification evidence;
- closeout records;
- revision records; and
- handoff records.

FS-09 must not silently provision the file, migrate an existing project, or
claim that cross-record integration has already been resolved.

## Decisions fixed by the corrective architecture

The following are no longer deferred:

- initial supported transition scope;
- normative contract placement;
- exact target-project lifecycle path;
- replacement-only behavior;
- caller-controlled path, pointer, patch, and byte prohibition;
- file-creation prohibition;
- multi-file-operation prohibition;
- canonical target schema;
- authority-source binding;
- writer-source binding;
- exact reusable-product paths;
- reusable-product path and commit limits;
- deterministic dry-run target inventory;
- single-file atomic-replacement boundary;
- post-replacement restoration requirement;
- path-safety boundary;
- real-project prohibition; and
- disposable-fixture-only Phase-1 exercise.

Implementation details not already fixed by the accepted design may be resolved
only after separate FS-09 work-package acceptance and activation, and only
within this corrected boundary.

## Explicit prohibitions

This correction does not authorize or perform:

- FS-09 work-package acceptance;
- FS-09 activation;
- registration of `FS_09_WORKING_MODEL`;
- reusable-product implementation;
- creation of `specs/lifecycle-write-contract.json`;
- modification of `tools/floppyctl.py`;
- creation of `tests/test_controlled_lifecycle_writes.py`;
- lifecycle writes against any real repository;
- project provisioning;
- migration;
- dependency addition or expansion;
- push;
- merge;
- integration;
- tag;
- release;
- package creation;
- installer creation;
- runtime bundling;
- modification of an external repository; or
- production changes.

FS-09 remains corrected but inactive, unaccepted, unauthorized, and not started.

<!-- FS09_PHASE1_BEGIN -->
## FS-09 Phase-1 control state — IMPLEMENTATION ACTIVE

```text
Status: ACTIVE
Accepted work-package checkpoint: 688814e5d2382cf2bb3794730a6bdb435c62d022
Active authorization: FS_09_IMPLEMENTATION
Repository writer: FS_09_WORKING_MODEL
Writer authorization reference: FS_09_IMPLEMENTATION
Exact product paths:
- specs/lifecycle-write-contract.json
- tools/floppyctl.py
- tests/test_controlled_lifecycle_writes.py
Real-project lifecycle writes: PROHIBITED
Disposable fixture use: AUTHORIZED FOR TESTING ONLY
```
<!-- FS09_PHASE1_END -->
