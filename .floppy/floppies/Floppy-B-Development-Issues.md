# Floppy B — Development Issues

This file records unresolved issues and risks. It grants no authority.

## Resolved by FS-01

The prior formal-lifecycle specification gap is resolved by the accepted FS-01
implementation at:

`d03969aa93debb6b705098483c8b59bb9d37d58f`

FS-01 implementation and verification are complete, and administrator acceptance
is recorded through `TR-007-ACCEPT-SECTION`.

## Open development issues

1. Machine-readable BCE schemas are not yet normative.
2. The current validator does not enforce the complete lifecycle.
3. The validator is not yet sufficient for every active-project lifecycle state.
4. There is no read-only `floppyctl` inspection interface.
5. Closeout completeness, authorization integrity, secret scanning, boot-package
   verification, controlled lifecycle writes, migrations, final closure, and BCE
   export remain unimplemented.
6. The self-hosted source-development exception must remain explicit so root
   `.floppy/` is not confused with reusable `project-seed/.floppy/` media.
7. Source-system versioning and BCE/schema format versioning still require explicit
   separation in later authorized work.

## Current disposition

```text
FS-01 state:
LC-SECTION-ACCEPTED-CLOSEOUT-NOT-PROPOSED

FS-01 implementation:
COMPLETE

FS-01 verification:
COMPLETE

FS-01 administrator acceptance:
ACCEPTED

Active implementation section:
NONE

Current authorized section:
NONE

Active work authorization:
NO_ACTIVE_WORK_AUTHORIZATION

Section closeout:
NOT_PROPOSED

Closeout execution:
NOT AUTHORIZED

FS-02:
NOT AUTHORIZED
```

FS-01 is accepted but not closed.

The next possible operation is a separately authorized FS-01 closeout proposal or
a decision to withhold closeout. FS-02 remains inactive and unauthorized.
