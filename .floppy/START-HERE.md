# Start Here — Canonical Source-System Development

This BCE controls development of the canonical Floppy Project Interaction System.

## Required read order

1. `.floppy/START-HERE.md`
2. `.floppy/floppies/Floppy-A-HITL.md`
3. `.floppy/floppies/Floppy-E-Current-Section.md`
4. `.floppy/floppies/Floppy-D-Project-Map.md`
5. `.floppy/floppies/Floppy-C-Project-Baseline.md`
6. `.floppy/floppies/Floppy-B-Development-Issues.md`
7. `.floppy/roadmap/roadmap.md`
8. `.floppy/closeouts/FS-01-closeout.md`
9. `.floppy/templates/Floppy-E-FS-02.draft.md`

## Present state

```text
Lifecycle state:
LC-SECTION-ACCEPTED-CLOSEOUT-PROPOSED

Applied transition:
TR-008-PROPOSE-SECTION-CLOSEOUT

Authority:
NO_ACTIVE_WORK_AUTHORIZATION

Active implementation section:
NONE

Current authorized section:
NONE

FS-01 implementation:
COMPLETE

FS-01 verification:
COMPLETE

FS-01 administrator acceptance:
ACCEPTED

FS-01 closeout:
PROPOSED

FS-01 closeout application:
NOT AUTHORIZED

Integration:
NOT AUTHORIZED

FS-02:
DRAFT ONLY — NOT AUTHORIZED
```

## Fixed checkpoints

- Accepted FS-01 implementation: `d03969aa93debb6b705098483c8b59bb9d37d58f`
- FS-01 acceptance recording: `5eeb3435644653534a6a430714a84b840ca497c0`
- FS-01 product completion: `d907643874f9aa278f31311527f3e7ec907c6cb6`
- Source version: `0.4.1-dev`

## Proposal boundary

Only `TR-008-PROPOSE-SECTION-CLOSEOUT` has been applied.

The proposal is not a completed closeout. It does not authorize:

- `TR-009-APPLY-SECTION-CLOSEOUT`;
- additional FS-01 product writes;
- integration or a pull request;
- merge, tag, release, or migration;
- FS-02 work-package acceptance;
- FS-02 activation or implementation; or
- any later section.

The next legal action is administrator review of the committed, unchanged closeout
proposal. Stage 2 requires a separate approval naming that proposal commit.

Do not begin Stage 2 without that exact approval.
