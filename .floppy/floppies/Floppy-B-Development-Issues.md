# Floppy B — Development Issues

This file records unresolved issues and risks. It grants no authority.

## Open control-layer issues

1. The lifecycle model is described across prose but is not yet formally specified.
2. Machine-readable BCE schemas are not yet normative.
3. The current validator checks structure and selected invariants but does not
   enforce the complete lifecycle.
4. The current validator assumes a fresh-project state for some checks and is not
   sufficient for active-project lifecycle validation.
5. There is no read-only `floppyctl` inspection interface.
6. Closeout completeness, authorization integrity, secret scanning, boot-package
   verification, controlled lifecycle writes, migrations, final closure, and BCE
   export remain unimplemented.
7. The self-hosted source-development exception must remain explicit so the root
   BCE is not confused with reusable `project-seed/.floppy/` media.
8. Source-system versioning and BCE/schema format versioning require explicit
   separation in later authorized work.

## Current disposition

FS-01 is the next implementation candidate for resolving the formal lifecycle gap.

FS-01 work package: `ACCEPTED AS PLANNING BASELINE`

FS-01 status: `WORK_PACKAGE_ACCEPTED_NOT_AUTHORIZED`

FS-01 activation: `NOT AUTHORIZED`

FS-01 implementation: `NOT STARTED`

Active implementation section: `NONE`

Active work authorization: `NO_ACTIVE_WORK_AUTHORIZATION`
