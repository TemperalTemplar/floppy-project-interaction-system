# Floppy B — Development Issues

This file records unresolved issues and risks. It grants no authority.

## Closed architectural issues through FS-11 reconciliation

The following prior FS-11 preparation risks are now resolved in committed
product and control state:

1. Source-of-truth precedence:
   `.floppy/lifecycle-state.json` and
   `.floppy/orchestrator-registry.json` are authoritative after canonical
   bootstrap.
2. Split-brain prevention:
   both canonical records must exist together and all projections must agree.
3. Writer exclusivity:
   exactly one INT-01 writer is registered and bound to one authorization.
4. Provisioning rollback and partial failure:
   reusable initialization validates a staged candidate, installs atomically,
   refuses an existing `.floppy`, and restores the pre-operation state on
   failure.
5. Compatibility:
   self-hosted control validation recognizes only
   `LEGACY_PRE_INTEGRATION` and `CANONICAL_INTEGRATED`.
6. Real-root reconciliation:
   the exact ten-path one-time reconciliation was separately authorized and
   applied after the reusable-product commit.

## Current FS-11 position

```text
Lifecycle state:
LC-SECTION-IMPLEMENTATION-IN-PROGRESS

Control mode:
CANONICAL_INTEGRATED

Active authorization:
FS_11_INT_01_SELF_HOSTED_RECONCILIATION

Repository writer:
FS_11_INT_01_WORKING_MODEL

Reusable-product commit:
b4e9ffb520545a312d596aaf3aca53be7c2fd67b

INT-01 handoff commit:
d0df2cf85011e068bc13d74ae9db9aedc5a376ae

Root-control reconciliation:
APPLIED

Implementation completion:
NOT YET RECORDED

Verification completion:
NOT YET RECORDED

Administrator result acceptance:
PENDING

Closeout:
NOT PROPOSED

FS-12:
INACTIVE / NOT AUTHORIZED
```

## Remaining roadmap obligations

1. Record FS-11 implementation and verification completion through ordered
   TR-005 and TR-006 evidence.
2. Obtain administrator acceptance of the verified FS-11 result through TR-007.
3. Propose and apply FS-11 closeout through distinct TR-008 and TR-009 commits.
4. Create the inactive FS-12 draft only during FS-11 closeout application.
5. Implement FS-12 Final-Project Closure under its own future accepted work
   package and authorization.
6. Implement FS-13 Export and Integrity under its own future accepted work
   package and authorization.
7. Preserve the finished Windows distribution requirement: ordinary users must
   not be required to install Python or execute loose Python scripts.

## Prohibited inference

The completed reconciliation does not authorize Commit 6, administrator result
acceptance, closeout, FS-12 activation, push, merge, release, packaging, or
production action except through their exact later controls.
