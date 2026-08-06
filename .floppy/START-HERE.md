# Start Here — Canonical Source-System Development

This BCE controls development of the canonical Floppy Project Interaction System.
The self-hosted root control state is now in canonical integrated mode.

## Required read order

1. `.floppy/START-HERE.md`
2. `.floppy/floppies/Floppy-A-HITL.md`
3. `.floppy/floppies/Floppy-E-Current-Section.md`
4. `.floppy/floppies/Floppy-D-Project-Map.md`
5. `.floppy/floppies/Floppy-C-Project-Baseline.md`
6. `.floppy/floppies/Floppy-B-Development-Issues.md`
7. `.floppy/roadmap/roadmap.md`
8. `.floppy/lifecycle-state.json`
9. `.floppy/orchestrator-registry.json`
10. `.floppy/templates/Floppy-E-FS-11.draft.md`

## Present state

```text
Lifecycle state:
LC-SECTION-IMPLEMENTATION-IN-PROGRESS

Applied lifecycle transition:
TR-004-START-SECTION-IMPLEMENTATION

Control mode:
CANONICAL_INTEGRATED

Active implementation section:
FS-11

Active authorization:
FS_11_INT_01_SELF_HOSTED_RECONCILIATION

Repository writer:
FS_11_INT_01_WORKING_MODEL

Writer authorization reference:
FS_11_INT_01_SELF_HOSTED_RECONCILIATION

PROV-01 reusable-product output:
COMMITTED AND VERIFIED

INT-01 authority handoff:
COMMITTED AND VERIFIED

INT-01 self-hosted reconciliation:
APPLIED

FS-11 implementation:
IN PROGRESS

FS-11 verification:
NOT STARTED

FS-11 administrator result acceptance:
PENDING

FS-12:
INACTIVE / NOT AUTHORIZED
```

## Controlling checkpoints

- Reusable-product commit: `b4e9ffb520545a312d596aaf3aca53be7c2fd67b`
- INT-01 authority-handoff commit: `d0df2cf85011e068bc13d74ae9db9aedc5a376ae`
- Accepted INT-01 plan SHA-256: `a10e46f218b952f8fb5baf24807d1b9b7da2ec201314e57880808e032e8b33b6`
- Source version: `0.4.1-dev`

## Current boundary

The exact ten-path self-hosted reconciliation has been applied under INT-01.
No lifecycle state changed in that implementation commit.

The next legal FS-11 operation is the separately recorded implementation and
verification completion sequence:

```text
TR-005-RECORD-IMPLEMENTATION-COMPLETE
TR-006-RECORD-VERIFICATION-COMPLETE
```

INT-01 remains the only active authorization and writer until the later
administrator-result acceptance commit clears it.

No push, merge, integration into `main`, tag, release, package publication,
migration, production change, FS-12 activation, or additional path is
authorized.
