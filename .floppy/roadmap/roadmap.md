# BCE Control Layer Development Roadmap

```text
Development roadmap:
ACCEPTED — ADMINISTRATIVELY REVISED

Lifecycle state:
LC-SECTION-IMPLEMENTATION-IN-PROGRESS

Control mode:
CANONICAL_INTEGRATED

Authority:
EXACT_SECTION_IMPLEMENTATION_AUTHORIZATION

Active implementation section:
FS-11

Current authorized section:
FS-11

FS-01 through FS-09:
CLOSED

FS-10:
CLOSED / IMPLEMENTATION NOT_REQUIRED / VERIFICATION COMPLETE

FS-11:
IMPLEMENTATION IN PROGRESS
REUSABLE PRODUCT COMMITTED AND VERIFIED
INT-01 AUTHORITY HANDOFF COMMITTED
ROOT-CONTROL RECONCILIATION APPLIED

FS-12:
PLANNED_NOT_AUTHORIZED / INACTIVE

FS-13:
PLANNED_NOT_AUTHORIZED / INACTIVE

Active authorization:
FS_11_INT_01_SELF_HOSTED_RECONCILIATION

Repository writer:
FS_11_INT_01_WORKING_MODEL

Writer authorization reference:
FS_11_INT_01_SELF_HOSTED_RECONCILIATION

Integration, merge, tag, release, and production:
NOT AUTHORIZED
```

## Remaining package boundaries

Only the current next section may have exact product paths, exact tests, and a complete work-package draft. Later sections remain bounded capability objectives until their own drafts are prepared from the repository state that exists at that time.

| Section | Capability | Product-path cap | Product-commit cap |
|---|---|---:|---:|
| FS-03 | Add cross-record semantics to the existing validator. | **2 exact paths** | **1** |
| FS-04 | Add thin read-only `status`, `validate`, and `inspect` CLI commands. | **2** | **1** |
| FS-05 | Add closeout-completeness rules to the existing validator and CLI. | **3** | **1** |
| FS-06 | Add read-only authorization and Git-integrity checks. | **3** | **1** |
| FS-07 | Add a small package-content scan reused by packaging and export. | **2** | **1** |
| FS-08 | Produce one validated boot-package ZIP with one checksum manifest. | **3** | **1** |
| FS-09 | Add dry-run and controlled writes for FS-01 lifecycle transitions. | **3** | **2** |
| FS-10 | Implement only qualifying evidence-backed migrations; otherwise close after verification with no product change. | **4 per accepted real path** | **1 per accepted real path** |
| FS-11 | Establish bounded project-control provisioning and integration; real-root reconciliation remains separately authorized. | **DEFERRED** | **NOT AUTHORIZED** |
| FS-12 | Add final-project closure using the existing validator, CLI, and write code. | **4** | **1** |
| FS-13 | Export and verify one portable ZIP and integrity manifest. | **3** | **1** |

### FS-03 exact product scope

```text
tools/validate_floppy.py
tests/test_bce_semantics.py
```

FS-03 must reuse the FS-02 normative schemas and the existing validator. It must not create a new validation framework, domain layer, loader hierarchy, or package tree.

### Explicit scope limits

- FS-04 through FS-13 do not receive exact filenames or detailed test inventories until their own work-package drafts are prepared.
- FS-05 extends the validator and CLI; it is not a separate closeout engine.
- FS-06 uses Git directly; it does not create a Git abstraction, transaction layer, lock manager, or custom work-package hashing.
- FS-07 is a small deterministic package-content scan, not a DLP or repository-security platform.
- FS-08 and FS-13 reuse the same packaging foundation.
- FS-09 uses Git commits as the recovery boundary; no rollback engine, recovery journal, transaction coordinator, or automatic branch restoration is permitted.
- FS-10 supports only actual prior Floppy formats proven by a qualifying real adopting-project source-format fixture and may close after verification with no reusable-product changes when no qualifying migration path is proven.
- FS-11 owns future reusable project-control provisioning and integration; self-hosted-root reconciliation requires separate exact administrative authority and a separate commit.
- FS-12 is one validated final-closure operation, not a separate closure engine.
- FS-13 excludes history compaction, signing infrastructure, hosting, synchronization, and multiple export formats.

## FS-10 corrective routing revision

The administrator accepted:

`OPTION 3 — SEPARATE REUSABLE PROVISIONING FROM ONE-TIME SELF-HOSTED RECONCILIATION`

The accepted routing is:

1. FS-10 remains Targeted Migration and owns only actual prior Floppy formats
   used by real adopting projects and proven by qualifying real source-format
   fixtures.
2. FS-10 may close after verification with no reusable-product changes when no
   qualifying migration path is proven.
3. FS-11 is roadmap-only Project Control-State Provisioning and Integration.
4. FS-12 is Final-Project Closure.
5. FS-13 is Export and Integrity.
6. Reusable project-seed or initialization changes and real self-hosted-root
   reconciliation require separate authorities and separate commits.
7. TR-004 remains prohibited from real-project use.
8. No FS-11 work-package draft, product path, test inventory, or product commit
   is authorized by this administrative revision.

The finished Windows release must not require ordinary users to install Python,
configure PATH, download loose `.py` files, or manually execute Python
commands.

## Common operating rules

1. One start authorization may cover acceptance recording, worktree creation, activation, implementation, validation, authorized product commits, and completion/verification recording.
2. One later administrator-acceptance authorization may cover acceptance recording, distinct closeout proposal and application commits, creation of the next inactive draft, and clearing the writer.
3. Each section returns at most one implementation-completion report and one final closeout report.
4. Do not stop for staging, commit mechanics, or successful routine validation.
5. Stop only for scope or architecture change, a new dependency, security or production impact, destructive action, or failed acceptance criteria.
6. Every closeout creates the next section draft as inactive, unaccepted, unauthorized, and with repository writer `NONE`.
7. Work-package files must not contain full implementation scripts.

## Fixed FS-01 checkpoints

- Accepted implementation: `d03969aa93debb6b705098483c8b59bb9d37d58f`
- Acceptance recording: `5eeb3435644653534a6a430714a84b840ca497c0`
- Approved closeout proposal: `6355dcf9daf8a0bcb4c7cbe4b701cdc49c57d479`
- Product completion: `d907643874f9aa278f31311527f3e7ec907c6cb6`
- Source version: `0.4.1-dev`

## Fixed FS-02 checkpoints

- Product P1: `0ec8da6c7cd2224b284fcff57c3b03a444c594e6`
- Product P2: `fc52c289a0d4816ad5e5c24d01cd4cbbd1ed74c6`
- Completion: `087a8c306f7348b67d12c134a610696f28471aaf`
- Administrator acceptance: `6a174dd0d6a220121b3ed0e14de281afdbd28273`
- Closeout proposal: `849c1fc2e70a76b834256050b4077c0f5096f925`
- Closeout application: `7e1a1ba985e802cadac6588b9425dedfae787ac2`
- Deferred FS-03 draft correction: `b9bdd0594b49eaf0606b28c30acda373fdc9d8b3`
- Remaining-roadmap correction: `a9bae496b7835ebd05ce4d06008ffe0aed25ef7a`
- Source version: `0.4.1-dev`

<!-- FS-05-DRAFT-BOUNDARY:BEGIN -->
### FS-05 — Closed

```text
Status: CLOSED
Implementation: COMPLETE
Verification: COMPLETE
Administrator acceptance: ACCEPTED
Administrator-acceptance commit: 81fd397010bde5d840936af2aed90447dd7f9dfd
Closeout proposal: 0510e5054222711a23903843130369a186e95bc5
Closeout application: THIS_COMMIT
Active authorization: NONE
Repository writer: NONE
```

### FS-06 — Closed

```text
Status: CLOSED
Implementation: COMPLETE
Verification: COMPLETE
Administrator acceptance: ACCEPTED
Administrator-acceptance commit: a7da009580c25a614e0012e26645816e12ea728c
Closeout proposal: ca8bce0fb687503431de05b17e09637ab4558c15
Closeout application: THIS_COMMIT
Active authorization: NONE
Repository writer: NONE
```

### FS-07 — Closed

```text
Status: CLOSED
Implementation: COMPLETE
Verification: COMPLETE
Administrator acceptance: ACCEPTED
Administrator-acceptance commit: a215a26d6b9db08e48ad679b5c8d801bce4e998f
Closeout: APPLIED
Closeout proposal: cbc6307abea6a35321548a193c5bebcf0961c27e
Closeout application: THIS_COMMIT
Reusable-product commit: 4ee33d571d16ba9802332efd09e1ca14183ba558
Active authorization: NONE
Repository writer: NONE
```

Exact accepted reusable-product scope:

```text
tools/floppyctl.py
tests/test_package_content_scan.py
```

Verification evidence: focused FS-07 `18 PASSED`; complete repository suite
`102 PASSED`; all required FS-06 through FS-02 regressions and validators
`PASSED`.

<!-- FS-08-PHASE-2:BEGIN -->
### FS-08 — Validated boot-package ZIP and checksum manifest

```text
Lifecycle state: LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE
Status: CLOSED
Implementation: COMPLETE
Verification: COMPLETE
Administrator acceptance: ACCEPTED
Administrator-acceptance commit: 75656b680b44f81972d9ff2dfab9ff7d244f9a59
Closeout: APPLIED
Closeout proposal commit: 3969ade7efc7b08b7665bd0dcb7324d202ba50c4
Reusable-product commit: b05e8d6bd6205ad17f10eceae0d319de981b07f8
Active authorization: NONE
Repository writer: NONE
```

The accepted ZIP and checksum manifest remain unchanged and verified read-only.
The ZIP is a validated FS-08 boot package, not the finished no-Python Windows
release.

### FS-09 — Controlled FS-01 lifecycle writes with dry-run and atomic replacement

```text
Draft: .floppy/templates/Floppy-E-FS-09.draft.md
Status: DRAFT_NOT_AUTHORIZED
Accepted: NO
Active: NO
Authorized: NO
Implementation: NOT STARTED
Maximum reusable-product paths: 3
Maximum reusable-product commits: 2
Active authorization: NONE
Repository writer: NONE
```

All detailed implementation choices remain deferred. FS-09 grants no write,
migration, integration, release, or production authority.

<!-- FS09_PHASE1_BEGIN -->
## FS-09 Phase-1 control state — IMPLEMENTATION AND VERIFICATION COMPLETE

```text
Implementation: COMPLETE
Verification: COMPLETE
Product commit: f732cdbbadcc0c92489ad178de3a4fb6d5fffd5a
Accepted corrective architecture: 6a221e89ac49dd1478906a8c80a26c99e0d9f5037384b3bca9dc225ffdb83b41
Normative contract SHA-256: 3ca2c7a398b6bca82b98eab48a93f9cf9ea944f44411854767b2f6e011d3c34e
Focused FS-09 tests: 28 PASSED
Complete repository suite: 151 PASSED
Administrator acceptance: PENDING
Closeout: NOT STARTED
Active authorization: NONE
Repository writer: NONE
FS-10: INACTIVE / NOT AUTHORIZED
```
<!-- FS09_PHASE1_END -->

<!-- FS09_PHASE2_BEGIN -->
## FS-09 Phase-2 control state — CLOSED

```text
Lifecycle state: LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE
FS-09 status: CLOSED
Implementation: COMPLETE
Verification: COMPLETE
Administrator acceptance: ACCEPTED
Administrator-acceptance commit: c4c748388d05ab1ec50d25ea05fb2fb558d49632
Closeout proposal commit: 2b73428daae08d94ee634ce810b9fc59794a1116
Closeout: APPLIED
Closeout application commit: THIS_COMMIT
Active authorization: NONE
Repository writer: NONE
Writer authorization reference: NONE
FS-10: DRAFT_NOT_AUTHORIZED / INACTIVE / NOT ACCEPTED / NOT AUTHORIZED
```

Real-project use of TR-004 remains prohibited. Project provisioning and
lifecycle-state integration remain incomplete and separately controlled.
<!-- FS09_PHASE2_END -->

<!-- BEGIN FS-10 VERIFICATION-ONLY WORK-PACKAGE ACCEPTANCE -->
## FS-10 verification-only section — closed

```text
Section: FS-10 — Targeted Migration
Status: CLOSED
Global lifecycle: LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE
Work-package type: VERIFICATION_ONLY_NO_REUSABLE_PRODUCT_CHANGE
Implementation disposition: NOT_REQUIRED
Verification: COMPLETE
Administrator acceptance: ACCEPTED
Closeout: APPLIED
Closeout proposal commit: ed0967eb300fe6d47ce6c07b53d5cbdcd8d1fefc
Closeout proposal SHA-256: 71937643c79c969adb668ad3d16041ff3182cd457f5f735225957a289445a5d0
Closeout application transition: TR-020-APPLY-VERIFICATION-ONLY-SECTION-CLOSEOUT
Closeout application checkpoint: THIS_COMMIT
Reusable-product paths: 0
Reusable-product commits: 0
Product commit: null
Active work authorization: NONE
Repository writer: NONE
```

The global next-section-inactive state does not replace FS-10's closed-section
outcome. `NOT_REQUIRED` remains authoritative.

## FS-11 inactive draft

```text
Draft: .floppy/templates/Floppy-E-FS-11.draft.md
Status: DRAFT_NOT_AUTHORIZED
Accepted: NO
Active: NO
Authorized: NO
Implementation started: NO
Repository writer: NONE
```

The next legal operation is preparation, revision, acceptance, or withholding
of the FS-11 work package under separate authority.
<!-- END FS-10 VERIFICATION-ONLY WORK-PACKAGE ACCEPTANCE -->


<!-- FS11_PROV01_ACTIVATION_BEGIN -->
## FS-11 INT-01 authority handoff complete

```text
Lifecycle state: LC-SECTION-IMPLEMENTATION-IN-PROGRESS
Lifecycle transition: NONE
Operation: STATE_PRESERVING_AUTHORITY_HANDOFF
Accepted plan SHA-256: a10e46f218b952f8fb5baf24807d1b9b7da2ec201314e57880808e032e8b33b6
Commit 3 product checkpoint: b4e9ffb520545a312d596aaf3aca53be7c2fd67b
PROV-01 authorization: CLEARED
INT-01 authorization: FS_11_INT_01_SELF_HOSTED_RECONCILIATION
Repository writer: FS_11_INT_01_WORKING_MODEL
Writer authorization reference: FS_11_INT_01_SELF_HOSTED_RECONCILIATION
Active implementation section: FS-11
INT-01 exact reconciliation paths: 10
Canonical root records: CREATED TOGETHER
Root reconciliation output applied: NO
Commit 4 checkpoint: THIS_COMMIT
FS-12: INACTIVE / NOT AUTHORIZED
```

Commit 4 replaced the PROV-01 writer with the one INT-01 writer without changing
the lifecycle state. Commit 5 remains a separate exact ten-path root-control
implementation and has not been applied.
<!-- FS11_PROV01_ACTIVATION_END -->


<!-- FS11_INT01_RECONCILIATION_APPLIED_BEGIN -->
## FS-11 INT-01 reconciliation applied

```text
Lifecycle state: LC-SECTION-IMPLEMENTATION-IN-PROGRESS
Operation: ROOT_CONTROL_IMPLEMENTATION
Lifecycle transition: NONE
Reusable-product commit: b4e9ffb520545a312d596aaf3aca53be7c2fd67b
Authority-handoff commit: d0df2cf85011e068bc13d74ae9db9aedc5a376ae
Exact root-control paths: 10
Root-control reconciliation: APPLIED
Active authorization: FS_11_INT_01_SELF_HOSTED_RECONCILIATION
Repository writer: FS_11_INT_01_WORKING_MODEL
Implementation completion: NOT YET RECORDED
Verification completion: NOT YET RECORDED
Administrator acceptance: PENDING
Closeout: NOT PROPOSED
FS-12: INACTIVE / NOT AUTHORIZED
```

The next planned commit records ordered TR-005 and TR-006 evidence while
retaining INT-01.
<!-- FS11_INT01_RECONCILIATION_APPLIED_END -->
