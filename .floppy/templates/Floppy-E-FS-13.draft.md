STATUS: IMPLEMENTATION_IN_PROGRESS

# Floppy E — FS-13 Work Package

Section: `FS-13 — Export and Integrity`

Lifecycle state: `LC-SECTION-IMPLEMENTATION-IN-PROGRESS`

Administrator amendment: `AMEND ACTIVE FS-13 IMPLEMENTATION AT CHECKPOINT ca46998aad6b2eb0a1027647e629628e98baabf6 TREE faef39ddd002a624f2bcedf52d433d929017d540 BY STATE-PRESERVING AUTHORITY HANDOFF FROM AUTHORIZATION FS_13_IMPLEMENTATION AND WRITER FS_13_WORKING_MODEL TO AUTHORIZATION FS_13_IMPLEMENTATION_V2 AND WRITER FS_13_WORKING_MODEL_V2; ADD ONLY system-manifest.json TO THE ACCEPTED REUSABLE-PRODUCT SCOPE, MAKING THE EXACT P1 SCOPE tools/floppyctl.py, tests/test_export_integrity.py, AND system-manifest.json; RETAIN EXACTLY ONE REUSABLE-PRODUCT COMMIT, THE ACCEPTED FS-07/FS-08/FS-13/CLI FOCUSED REGRESSIONS, ONE COMPLETE REPOSITORY SUITE AT THE IMPLEMENTATION-COMPLETION BOUNDARY, SOURCE VERSION 0.4.3-dev, AND ALL OTHER FS-13 TERMS. AUTHORIZE EXACTLY ONE ADDITIONAL STATE-PRESERVING CONTROL COMMIT BEFORE P1 TO RECORD THIS HANDOFF; DO NOT CHANGE THE FS-13 LIFECYCLE STATE DURING THAT COMMIT. CONTINUE TO AUTHORIZE P1, TR-005, TR-006, AND C4 UNDER THE REPLACEMENT AUTHORIZATION. DO NOT AUTHORIZE TR-007, TR-008, TR-009, FINAL-PROJECT CLOSURE, INTEGRATION, MERGE, TAG, RELEASE, FORCE PUSH, HISTORY REWRITE, OR ANY MODIFICATION OF main.`

```text
Accepted: YES, AS AMENDED
Active: YES
Prior authorization: FS_13_IMPLEMENTATION
Replacement authorization: FS_13_IMPLEMENTATION_V2
Prior repository writer: FS_13_WORKING_MODEL
Replacement repository writer: FS_13_WORKING_MODEL_V2
Handoff base checkpoint: ca46998aad6b2eb0a1027647e629628e98baabf6
Exact reusable-product paths: 3
- tools/floppyctl.py
- tests/test_export_integrity.py
- system-manifest.json
Exact reusable-product commits: 1
Additional state-preserving control commits authorized: 1
Lifecycle state changed by handoff: NO
Implementation: IN_PROGRESS
Verification: NOT_STARTED
Administrator acceptance: PENDING
Closeout: NOT_PROPOSED
Final-project closure: OPEN
```

`system-manifest.json` is added only because the registered
`tools/floppyctl.py` SHA-256 must remain coherent with the CLI implementation.
All other accepted FS-13 terms remain in force.
