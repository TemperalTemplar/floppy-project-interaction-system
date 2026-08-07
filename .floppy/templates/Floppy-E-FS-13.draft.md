STATUS: ACCEPTED_PLANNING_BASELINE

# Floppy E — FS-13 Accepted Work Package

## Section

`FS-13 — Export and Integrity`

## Acceptance record

```text
Transition: TR-002-ACCEPT-WORK-PACKAGE
Acceptance base checkpoint: 718e3c9ee6d0a87f6f700f4cbb50559725c158cc
Acceptance checkpoint: THIS_COMMIT
Administrator decision: ACCEPT THE 2-PATH FS-13 WORK PACKAGE AT BASE 718e3c9ee6d0a87f6f700f4cbb50559725c158cc WITH REUSABLE-PRODUCT PATHS tools/floppyctl.py AND tests/test_export_integrity.py, EXACTLY ONE REUSABLE-PRODUCT COMMIT, THE PREPARED 11-PATH BOUNDED FS-13 CONTROL-STATE SET, FOCUSED FS-07/FS-08/FS-13/CLI REGRESSION VALIDATION AND ONE COMPLETE REPOSITORY SUITE AT THE IMPLEMENTATION-COMPLETION BOUNDARY; AUTHORIZE ONLY TR-002-ACCEPT-WORK-PACKAGE AND COMMIT C1; DO NOT AUTHORIZE TR-003 OR ANY IMPLEMENTATION YET. RETURN THE EXACT C1 COMMIT SHA AND TREE, VERIFY IT IS PUSHED TO feature/ctrl-02-verification-only-lifecycle, THEN STOP FOR IMPLEMENTATION AUTHORIZATION.
Status: ACCEPTED_PLANNING_BASELINE
Accepted: YES
Active: NO
Activation authorized: NO
Implementation authorized: NO
Authorization identifier: null
Repository writer: NONE
Writer authorization reference: NONE
Final-project closure: OPEN
```

Work-package acceptance is a planning baseline only. It does not authorize
`TR-003`, `TR-004`, implementation, export execution, administrator result
acceptance, closeout, final-project closure, integration, merge, tag, release,
or modification of `main`.

## Objective

Export and verify one portable ZIP containing the accepted project context and
one adjacent integrity manifest.

FS-13 reuses the FS-08 deterministic packaging foundation. It extends the
existing CLI with one accepted-context export profile and matching verification;
it does not create a second packaging framework.

## Exact reusable-product scope

```text
Exact reusable-product paths: 2
Maximum reusable-product paths: 3
Exact reusable-product commits: 1
```

1. `tools/floppyctl.py`
2. `tests/test_export_integrity.py`

No other reusable-product path is authorized by this work package.

## Exact bounded administrative set

Maximum / exact bounded administrative paths: `11`.

- `.floppy/README.md`
- `.floppy/START-HERE.md`
- `.floppy/closeouts/FS-13-closeout.md`
- `.floppy/floppies/Floppy-D-Project-Map.md`
- `.floppy/floppies/Floppy-E-Current-Section.md`
- `.floppy/lifecycle-state.json`
- `.floppy/manifest.json`
- `.floppy/orchestrator-registry.json`
- `.floppy/roadmap/roadmap.json`
- `.floppy/roadmap/roadmap.md`
- `.floppy/templates/Floppy-E-FS-13.draft.md`

Individual lifecycle commits must use only the subset required by their exact
transition. The administrative set does not enlarge reusable-product scope.

## Required behavior

The future authorized implementation must:

- add one `export` operation and one matching `verify-export` operation to the
  existing `floppyctl` surface;
- export only a clean, checkpoint-bound adopting project's canonical `.floppy/`
  accepted context;
- produce exactly one deterministic portable ZIP and one adjacent integrity
  manifest;
- reuse FS-07 deterministic scanning and FS-08 ZIP/hash/manifest primitives;
- record deterministic archive identity, archive SHA-256/size, and sorted
  per-entry path/SHA-256/size integrity data;
- verify the ZIP and manifest without requiring the original checkout path;
- reject dirty or non-checkpoint-bound context, unsafe paths, symlinks/reparse
  points, path escape, duplicates, case collisions, extra/missing members,
  tampered bytes, noncanonical integrity data, and differing artifact collisions;
- reject export of this source-development repository's root `.floppy` control
  state as an adopting-project context export;
- preserve all lifecycle and Human-in-the-Loop authority semantics exactly.

## Explicit exclusions

FS-13 must not add:

- history compaction;
- an archival service;
- synchronization as a reusable-product feature;
- hosting;
- signing infrastructure;
- multiple export formats;
- final-project closure execution;
- integration, merge, tag, or release behavior.

## Test scope

Focused FS-13/regression modules:

- `tests/test_export_integrity.py`
- `tests/test_package_content_scan.py`
- `tests/test_validated_boot_package.py`
- `tests/test_floppyctl.py`

The new FS-13 tests must cover successful export/verification; source-root
rejection; exact `.floppy` boundary; clean/checkpoint binding; safe-path rules;
deterministic ordering and ZIP metadata; byte-identical repeatability;
artifact reuse/collision refusal; archive and per-entry SHA-256/size checks;
tampered/noncanonical manifests; missing/extra/duplicate/case-colliding entries;
checkout-location and current-working-directory independence; portable
verification after moving the artifact pair; concise CLI failures; and proof
that export does not mutate the project BCE.

## Validation cadence

- C1 work-package acceptance: transition-contract inspection, source validators,
  tracked JSON parse, exact control-scope comparison; no complete suite.
- C2 activation/start: focused authority and state validation only.
- P1 product commit: new FS-13 tests plus FS-07/FS-08/floppyctl regression scope.
- Implementation-completion boundary: one complete repository suite, source
  validator, floppyctl source validation, tracked JSON parse, committed-tree and
  exact-scope proof.
- Later acceptance/closeout commits: reuse immutable product evidence and run
  only transition-relevant control validation unless a committed contract
  explicitly requires more.

## Commit/lifecycle sequence

```text
C1  TR-002-ACCEPT-WORK-PACKAGE
C2  TR-003-AUTHORIZE-SECTION-IMPLEMENTATION + TR-004-START-SECTION-IMPLEMENTATION
P1  exactly one reusable-product commit
C4  TR-005-RECORD-IMPLEMENTATION-COMPLETE + TR-006-RECORD-VERIFICATION-COMPLETE
C5  TR-007-ACCEPT-SECTION
C6  TR-008-PROPOSE-SECTION-CLOSEOUT
C7  TR-009-APPLY-SECTION-CLOSEOUT
```

C1 is the only transition authorized by the current administrator decision.
C2 through C7 require their applicable later authority boundaries.

## Git trust and synchronization boundary

Every Git subprocess requiring the repository trust exception must use the
process-local `safe.directory` mechanism. Do not change global or repository Git
configuration to bypass the trust boundary.

After a validated committed checkpoint, synchronization may target only
`feature/ctrl-02-verification-only-lifecycle`, must be a normal fast-forward,
must refuse unexpected remote divergence, and must verify the remote SHA equals
the local SHA after push. No force push, history rewrite, amend, rebase,
cherry-pick reconstruction, merge, or `main` update is authorized.

## Final-section boundary

FS-13 is the final roadmap implementation section. Its future closeout must not
invent FS-14. After FS-13 is implemented, verified, accepted, and closed,
final-project closure remains a separate administrator-authorized operation;
clean integration into `main` remains separately authorized after final-project
closure.

## Mandatory stop

FS-13 is accepted only as a planning baseline. Stop after C1 until the
administrator gives exact implementation authorization tied to the C1 commit
and tree.
