# Session Handoffs

Store compact continuation records here. Keep the newest accepted handoff referenced in `manifest.json`. Handoffs preserve stopping points; they do not replace Floppies A–E.

<!-- V2_04_SUCCESSION_HANDOFF_BEGIN -->
## V2-04 Project Orchestrator succession

Project Orchestrator succession records use
`orchestrator-succession-######.json` and the V2-04 succession schema. They
preserve predecessor/successor identities, exact checkpoint, completed and
unresolved work, next legal operation, prohibited operations, and the exact
authority-state SHA-256.

A prepared handoff is invalid if the authority fingerprint changes. Do not
overwrite a stale handoff; stop with `STALE_SUCCESSION_HANDOFF` and prepare a
new record from current repository-backed state.
<!-- V2_04_SUCCESSION_HANDOFF_END -->
