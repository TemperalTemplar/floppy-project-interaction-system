# Floppy Project Interaction System V2 Development Orchestrator

**Identifier:** `FLOPPY-V2-DEVELOPMENT-ORCHESTRATOR-01`  
**Role:** Project development orchestrator  
**Reports to:** Administrator  
**Repository writer:** V2_03_WORKING_MODEL
**V2 implementation authority:** V2_03_IMPLEMENTATION

# 1. Controlling authority

The authoritative V2 roadmap is controlled by:

- `.floppy/roadmap/Floppy-V2-Project-Plan.md`
- `.floppy/roadmap/Floppy-V2-Project-Plan-Revision-R1.md`
- `.floppy/roadmap/Floppy-V2-Project-Plan.json`

Project Plan Revision R1 is the controlling clarification for paired Continuity Overseer / initial Project Orchestrator bootstrap and project-origin preservation.

The governing principle remains:

**Context loss is not authority to reconstruct accepted work.**

# 2. Canonical repository state

Repository: `TemperalTemplar/floppy-project-interaction-system`

Published v1 release: `v1.0.0`

V2 development base: `main` at `c8b40bb248336990da9112dd1b6b20de154572c5`

V2 development branch: `feature/v2-continuity-onboarding`

Intended administrator-local worktree: `D:\A\Floppy-V2`

Public `main` remains the reusable Floppy product. Root `.floppy/` on the V2 development branch is development-control state and must not be integrated into reusable `main`.

# 3. V1 historical boundary

V1 is complete. FS-01 through FS-13 and release `v1.0.0` are historical and immutable.

V2-01 is CLOSED. Its original accepted Class B definition remains preserved in Git history. A later explicitly authorized S1/S2 supersession may change the controlling future V2 Class B semantics without reopening V2-01.

# 4. Exact V2 roadmap

1. `V2-01` — V2 Architecture and Compatibility Contract — CLOSED
2. `V2-02` — User Onboarding and Provider-Independent Adoption — IMPLEMENTATION + VERIFICATION COMPLETE / ADMINISTRATOR ACCEPTANCE PENDING
3. `V2-03` — Accepted-State Continuity Protection — PLANNED / NOT AUTHORIZED
4. `V2-04` — Continuity Overseer and Orchestrator Succession — PLANNED / NOT AUTHORIZED
5. `V2-05` — Official Project Plan, Integration, Compatibility Validation, and V2 Release — PLANNED / NOT AUTHORIZED

No V2-06 exists absent explicit administrator project-plan revision.

# 5. Current lifecycle state

Before W1, the prerequisite validator chain completed under no active authority:

- VC1 generic progression correction: `6fb83656798f28db11fa8bbef4d77d4eeb2fcbec`;
- VC2 UTF-8 Git-integrity correction: `3689aef930186c26c774c3813d1026586860dd92`;
- corrected validator SHA-256: `44564b3c848f7e23f0a8c7aa4d7a3a8c98eb4060171475cf5b3b3c7fb07c1689`;
- VC1 re-proof: PASSED;
- VC2 bounded integrity validation: PASSED;
- repository writer: NONE;
- complete repository suite consumed: NO;
- Class B S1 applied: NO.

After V2-02 work-package acceptance, the legal current state is:

- lifecycle: `LC-WORK-PACKAGE-ACCEPTED-NO-ACTIVE-WORK`
- V2-02 work package: `ACCEPTED_PLANNING_BASELINE`
- V2-02 implementation: `NOT_STARTED`
- V2-02 verification: `NOT_STARTED`
- administrator result acceptance: `PENDING`
- active work authorization: NONE
- active implementation authorization: NONE
- section working model: NONE
- repository writer: NONE
- implementation authority: NONE

Work-package acceptance does not imply implementation authority.

# 6. Current assignment

The current lawful task is to preserve the accepted V2-02 planning baseline and prepare, but not execute, a later exact `V2_02_IMPLEMENTATION` authorization package against the exact accepted W1 checkpoint.

The accepted prerequisite Class B semantic supersession is not applied.

Normal V2-02 reusable-product implementation is not authorized.

# 7. V2-02 accepted planning boundary

V2-02 owns provider-independent user onboarding/adoption, Route A/B/C selection, the actual-session capability record, and the R1 user-facing handoff into paired Continuity Overseer / initial Project Orchestrator bootstrap.

V2-02 must not implement V2-04 continuity runtime or succession.

Actual session capabilities remain independent:

- `repository_read`
- `repository_write`
- `command_execution`
- `artifact_transfer`

Provider brand alone does not determine workflow class.

Future controlling semantics after explicit S1/S2 supersession:

- CLASS A — direct repository-write workflow technically available when separately authorized.
- CLASS B — direct repository read available; repository mutations administrator-applied.
- CLASS C — manual/file/evidence exchange required for repository interaction.

# 8. Frozen future Class B S1 scope

A later exact `V2_02_IMPLEMENTATION` authorization may apply S1 only to:

1. `specs/v2-architecture-compatibility.md`
2. `specs/v2-compatibility-profile.json`
3. `system-manifest.json`
4. `tests/test_v2_compatibility.py`

The V2 compatibility schema, V1 schemas, V2-01 closeout/control records, and `project-seed/.floppy/*` remain outside S1.

S1 must be verified and recorded by S2 before normal V2-02 P1 begins.

# 9. Frozen future V2-02 P1 scope

A later exact `V2_02_IMPLEMENTATION` authorization may apply normal P1 only to:

1. `docs/getting-started/README.md`
2. `docs/getting-started/ChatGPT.md`
3. `docs/getting-started/Gemini.md`
4. `docs/getting-started/Grok.md`
5. `docs/getting-started/DeepSeek.md`
6. `docs/getting-started/Other-AI.md`
7. `tests/test_user_onboarding.py`
8. `README.md`
9. `BOOTSTRAP.md`
10. `docs/User-Guide.md`
11. `onboarding/Floppy_1E.md`
12. `onboarding/README.md`
13. `protocols/01-new-project-onboarding.md`
14. `system-manifest.json`
15. `tools/validate_floppy.py`
16. `tools/floppyctl.py`
17. `tests/test_validated_boot_package.py`

No P1 mutation is authorized by W1.

# 10. R1 ownership boundary

V2-02 defines the paired-bootstrap trigger and user-facing handoff.

V2-03 protects the accepted project origin, original intent, accepted scope, exclusions, constraints, and accepted-plan records.

V2-04 implements paired bootstrap, durable shared-origin linkage, Continuity Overseer persistence, scope-drift protection, and Project Orchestrator succession.

V2-05 binds the Official Project Plan to the same project origin and proves the paired bootstrap end to end.

# 11. Required read order

1. `.floppy/roadmap/Floppy-V2-Project-Plan.md`
2. `.floppy/roadmap/Floppy-V2-Project-Plan-Revision-R1.md`
3. `.floppy/roadmap/Floppy-V2-Project-Plan.json`
4. `.floppy/roadmap/Floppy-V2-Project-Plan-Acceptance.md`
5. `.floppy/lifecycle-state.json`
6. `.floppy/orchestrator-registry.json`
7. `.floppy/work-packages/V2-01.md`
8. `.floppy/work-packages/V2-02.md`
9. this orchestrator directive

# 12. Immediate STOP boundary

At the W1 checkpoint this orchestrator may prepare the exact later V2-02 implementation authorization package for administrator review.

It may not:

- create `V2_02_IMPLEMENTATION`;
- register `V2_02_WORKING_MODEL`;
- apply the Class B S1 supersession;
- modify reusable-product files;
- implement V2-02;
- implement V2-03, V2-04, or V2-05;
- migrate;
- modify `main`;
- integrate, merge, tag, release;
- rebase, force-push, destructively reset, or rewrite history.

`V2 IMPLEMENTATION AUTHORITY = NONE`

<!-- V2_02_A1_BEGIN -->
# V2-02 A1 authorization

Exact authority: `V2_02_IMPLEMENTATION`
Sole repository writer: `V2_02_WORKING_MODEL`
Base: `c52726ad8fdb8a3d77252016ebd3b784a92dc4ff` / `33cac03fec71f578836e7d43abff7a3a5dd941f4`
S1 may proceed only after distinct B1 implementation-start control. P1 remains blocked until verified S2.

<!-- V2_02_A1_END -->

<!-- V2_02_B1_BEGIN -->
# V2-02 B1 implementation start

Implementation is in progress under `V2_02_IMPLEMENTATION` / `V2_02_WORKING_MODEL`. S1 Class-B supersession must be implemented and verified, then S2 must be recorded before P1 begins.

<!-- V2_02_B1_END -->

<!-- V2_02_S2_BEGIN -->
# V2-02 S2 verified supersession

S1 `6c3afb660bb72f85d828c388d0f05696a2f9f26f` / `e84a815e83e2b27ec62ec51e7e8139061d541748` is validated and controlling for future Class-B semantics. V2-01 remains closed. Normal P1 onboarding implementation is now the next legal operation.

<!-- V2_02_S2_END -->

<!-- V2_02_C1_BEGIN -->
# V2-02 C1 implementation completion

P1 `5dabb87da1c0fb7d16dde27cfaa47bb297c4f32c` / `4f8342045209ea530b9fff806a6d6fa2016ab2fb` is complete. Run the required source, focused, tracked-JSON, validated-boot-package, and regression verification. Only if all pass may the single authorized complete repository suite run.

<!-- V2_02_C1_END -->

<!-- V2_02_V1_BOOT_CORRECTED_BEGIN -->
# V2-02 V1 verification completion

Implementation and verification are complete after bounded C2/BPC1 boot-package completeness correction. Corrected validated boot inventory: 59 paths including `specs/lifecycle-write-contract.json`. Administrator result acceptance remains PENDING. No V2-02 closeout is authorized. Active work authorization, implementation authorization, section working model, and repository writer are cleared.

<!-- V2_02_V1_BOOT_CORRECTED_END -->

<!-- V2_03_W1_BEGIN -->
# V2-03 W1 work-package acceptance

Administrator decision: `ACCEPT THE V2-03 ACCEPTED-STATE CONTINUITY PROTECTION WORK-PACKAGE PROPOSAL AS THE V2-03 PLANNING BASELINE UNDER CONTROLLING PROJECT-PLAN REVISION R1.`

Transition: `TR-002-ACCEPT-WORK-PACKAGE`

Acceptance base: `6ad7c67fdd7f22732681c193694ac3a13f0d9ea0` / `ca483d6cf2c097824289f02818c0ab4196e960e5`

Resulting lifecycle: `LC-WORK-PACKAGE-ACCEPTED-NO-ACTIVE-WORK`

- V2-01: CLOSED
- V2-02: CLOSED
- V2-03 work package: ACCEPTED_PLANNING_BASELINE
- V2-03 implementation: NOT_STARTED
- V2-03 verification: NOT_STARTED
- V2-03 administrator result acceptance: PENDING
- V2-03 closeout: NOT_PROPOSED
- active work authorization: NONE
- active implementation authorization: NONE
- repository writer: NONE
- V2-04: PLANNED_NOT_AUTHORIZED
- V2-05: PLANNED_NOT_AUTHORIZED

The exact future V2-03 reusable-product scope is frozen to 11 paths in `.floppy/work-packages/V2-03.md`. W1 modifies control state only. It does not create `V2_03_IMPLEMENTATION`, `V2_03_WORKING_MODEL`, a repository writer, `.floppy/accepted-state.json`, V2-04 runtime, or V2-05 Official Project Plan implementation.

Next possible lifecycle operation: `TR-003-AUTHORIZE-SECTION-IMPLEMENTATION`, requiring separate explicit administrator authorization; NOT EXECUTED.

`V2 IMPLEMENTATION AUTHORITY = NONE`
<!-- V2_03_W1_END -->

<!-- V2_03_A1_BEGIN -->
# V2-03 A1 implementation authorization

`TR-003-AUTHORIZE-SECTION-IMPLEMENTATION` is applied under explicit administrator authority.

Authorization: `V2_03_IMPLEMENTATION`  
Sole repository writer: `V2_03_WORKING_MODEL`  
Base: `33e3f831303ea25defa41acbbe474b6cc8baff96` / `6ad0bf21373a2cc23a678def44fc4eebd932d368`

Lifecycle: `LC-SECTION-AUTHORIZED-NOT-STARTED`

Implementation remains `NOT_STARTED`; verification remains `NOT_STARTED`; administrator result acceptance remains `PENDING`; closeout remains `NOT_PROPOSED`.

The exact future P1 scope is the eleven reusable-product paths frozen in `.floppy/work-packages/V2-03.md`.

`V2 IMPLEMENTATION AUTHORITY = V2_03_IMPLEMENTATION`
<!-- V2_03_A1_END -->

<!-- V2_03_B1_BEGIN -->
# V2-03 B1 implementation start

`TR-004-START-SECTION-IMPLEMENTATION` is applied. V2-03 implementation is `IN_PROGRESS` under `V2_03_IMPLEMENTATION` / `V2_03_WORKING_MODEL`.

No reusable-product path is changed by B1. P1 remains a separate exact eleven-path commit.
<!-- V2_03_B1_END -->

<!-- V2_03_C1_BEGIN -->
# V2-03 C1 implementation completion

The exact eleven-path P1 commit is complete and `TR-005-RECORD-IMPLEMENTATION-COMPLETE` is applied.

Implementation is `COMPLETE`. Verification is `PENDING`. `V2_03_IMPLEMENTATION` and `V2_03_WORKING_MODEL` remain active only through the authorized verification boundary.

Run the exact bounded V2-03 verification gates. Only after all bounded gates pass may complete repository pytest-suite attempt 1 run.
<!-- V2_03_C1_END -->
