# Floppy B — Development Issues

This file records unresolved issues and risks. It grants no authority.

## Closed FS-01 issue

The formal lifecycle and state-transition specification issue was resolved,
verified, accepted, and formally closed.

- Accepted implementation: `d03969aa93debb6b705098483c8b59bb9d37d58f`
- Acceptance recording: `5eeb3435644653534a6a430714a84b840ca497c0`
- Approved closeout proposal: `6355dcf9daf8a0bcb4c7cbe4b701cdc49c57d479`
- FS-01 status: `CLOSED`
- FS-01 closeout: `APPLIED`

## Remaining roadmap obligations

1. Normative machine-readable BCE schemas remain unimplemented.
2. Full lifecycle semantic enforcement remains unimplemented.
3. Read-only `floppyctl` inspection remains unimplemented.
4. Closeout-completeness validation remains unimplemented.
5. Structured authorization and work-package integrity automation remain
   unimplemented.
6. Secret and unsafe-content scanning remains unimplemented.
7. Boot-package generation and verification remain unimplemented.
8. Controlled lifecycle write commands are implemented only within the accepted
   FS-09 boundary; real-project use remains prohibited.
9. Evidence-backed Targeted Migration remains unimplemented and may close after
   verification with no reusable-product change.
10. Project Control-State Provisioning and Integration remains unimplemented.
11. Final-project closure remains unimplemented.
12. BCE export and integrity remain unimplemented.
13. Source-version and BCE/schema-format versioning remain separately controlled.

## Current disposition

```text
Lifecycle state:
LC-SECTION-CLOSED-NEXT-SECTION-INACTIVE

Authority:
NO_ACTIVE_WORK_AUTHORIZATION

FS-01:
CLOSED

FS-02 work package:
NOT ACCEPTED

FS-02 activation:
NOT AUTHORIZED

FS-02 implementation:
NOT STARTED

FS-02 active:
FALSE
```

The next legal operation is preparation, revision, acceptance, or withholding of
the FS-02 work package—not implementation.

## FS-10 corrective-routing issues

The accepted administrative routing decision is Option 3: separate reusable
provisioning from one-time self-hosted reconciliation.

- `PROV-01` is routed to future FS-11 reusable project-control provisioning and
  integration.
- `INT-01` shares the future architectural contract but requires a separate
  one-time self-hosted administrative reconciliation authority and a separate
  commit.
- The older-adopting-project migration question remains hypothetical.
- No qualifying older-adopter source-format fixture currently exists.
- FS-10 may not infer migration scope from provisioning or integration
  evidence.
- Source-of-truth precedence remains unresolved for future FS-11 preparation.
- Split-brain prevention remains unresolved for future FS-11 preparation.
- Rollback and partial-failure behavior remain unresolved for future FS-11
  preparation.
- Compatibility classes remain unresolved for future FS-11 preparation.
- Real-project reconciliation authority remains unresolved for future FS-11
  preparation.

The nonnormative provisioning/integration contract outline is planning evidence
only. It is not accepted implementation architecture and grants no authority.
