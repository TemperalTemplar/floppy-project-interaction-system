STATUS: IMPLEMENTATION_IN_PROGRESS

# Floppy E — FS-13 Work Package

Section: `FS-13 — Export and Integrity`

Lifecycle state: `LC-SECTION-IMPLEMENTATION-IN-PROGRESS`

Administrator decision: `AUTHORIZE FS-13 IMPLEMENTATION FROM ACCEPTED CHECKPOINT 7ee76091cc5b290a14c40b8ec9ffba516cdf105d TREE 0de4edaf4a1e392162360b1cba469f9ad93317c7 ON feature/ctrl-02-verification-only-lifecycle IN D:\A\Floppy-CTRL-02 WITH AUTHORIZATION FS_13_IMPLEMENTATION AND REPOSITORY WRITER FS_13_WORKING_MODEL; AUTHORIZE TR-003-AUTHORIZE-SECTION-IMPLEMENTATION, TR-004-START-SECTION-IMPLEMENTATION, THE EXACT ONE-COMMIT REUSABLE-PRODUCT IMPLEMENTATION LIMITED TO tools/floppyctl.py AND tests/test_export_integrity.py, THE ACCEPTED FOCUSED FS-07/FS-08/FS-13/CLI REGRESSION VALIDATION, ONE COMPLETE REPOSITORY SUITE AT THE IMPLEMENTATION-COMPLETION BOUNDARY, TR-005-RECORD-IMPLEMENTATION-COMPLETE, TR-006-RECORD-VERIFICATION-COMPLETE, AND COMMITS C2, P1, AND C4; DO NOT AUTHORIZE TR-007, TR-008, TR-009, FINAL-PROJECT CLOSURE, INTEGRATION, MERGE, TAG, RELEASE, FORCE PUSH, HISTORY REWRITE, OR ANY MODIFICATION OF main.`

```text
Accepted: YES
Active: YES
Authorization: FS_13_IMPLEMENTATION
Repository writer: FS_13_WORKING_MODEL
Base checkpoint: 7ee76091cc5b290a14c40b8ec9ffba516cdf105d
Exact reusable-product paths: 2
- tools/floppyctl.py
- tests/test_export_integrity.py
Exact reusable-product commits: 1
Implementation: IN_PROGRESS
Verification: NOT_STARTED
Administrator acceptance: PENDING
Closeout: NOT_PROPOSED
Final-project closure: OPEN
```

Objective: Export and verify one portable ZIP containing the accepted context
and one integrity manifest.

FS-13 reuses the FS-07 scanner and FS-08 deterministic package/integrity
foundation. It does not authorize history compaction, archival service,
synchronization as a reusable feature, hosting, signing infrastructure,
multiple export formats, final-project closure, or integration.
