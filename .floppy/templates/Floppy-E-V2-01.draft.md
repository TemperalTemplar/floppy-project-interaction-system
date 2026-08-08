# Floppy V2-01 Work-Package Draft

**Work package:** `V2-01`  
**Title:** V2 Architecture and Compatibility Contract  
**Status:** DRAFT_NOT_AUTHORIZED  
**Implementation authority:** NONE  
**Repository writer:** NONE  
**Controlling roadmap:** `.floppy/roadmap/Floppy-V2-Project-Plan.md`

# 1. Objective

Define the exact legal relationship between v1 and v2 before implementation begins. This draft is subordinate to the accepted V2 project plan and may not redesign the five-package roadmap.

# 2. Required deliverables from the accepted project plan

V2-01 must produce:

- V2 architecture specification;
- V1 compatibility contract;
- V1→V2 migration/adoption rules;
- confirmation of which v1 lifecycle concepts remain unchanged;
- definition of new v2 record families required by later sections;
- defined provider-capability semantics;
- defined accepted-state protection semantics;
- defined Continuity Overseer authority boundaries;
- defined official project-plan artifact semantics;
- exact schema/version strategy;
- exact validation impact assessment; and
- exact package-profile impact assessment.

# 3. Required compatibility decisions

V2-01 must determine:

- whether a v1 project can continue without migration;
- when migration is required;
- whether migration may be deferred;
- how old accepted state remains authoritative;
- how newly introduced v2 records are initialized;
- whether schema versions remain mixed or are upgraded as a coherent bundle; and
- how a v1 BCE is recognized by v2 tooling.

# 4. Read-only intake findings to carry forward

The completed intake identified technical questions that V2-01 must resolve, but none of these findings is an accepted implementation decision yet:

1. V1 lifecycle schema versions must not be treated with a naive numeric “highest version wins” rule. The 1.1.0 verification-only extension and 1.2.0 final-closure extension are not safely assumed to form a simple cumulative chain.
2. V1 schemas and accepted historical records should remain immutable unless the accepted V2-01 contract explicitly defines a lawful compatibility mechanism.
3. Existing V1 projects must not be silently migrated merely because V2 tooling can read them. Reading/validating V1 state and adopting durable V2 state are separate concepts to define.
4. Existing root project-control state and reusable `project-seed/.floppy/` have different roles. V2 development-control `.floppy/` must remain out of clean reusable `main`.
5. The existing portable BCE export can transport tracked `.floppy` records, but V2-01 must define consumer/profile compatibility for new V2 records.
6. The validated boot/source package uses an explicit inventory, so any new canonical V2 source artifacts require deliberate package-profile impact analysis.
7. The raw project-seed `0.4.1-dev` text is a provisioning substitution token and must not be misclassified as a live V2 project-version defect.

# 5. Design questions to resolve

- DQ-01 — What exact V1/V2 source/project compatibility matrix is authoritative?
- DQ-02 — How is lifecycle schema/profile selection made explicitly?
- DQ-03 — Does V2 introduce a coherent `2.0.0` compatibility/schema family, continue the `1.x` family, or compose independent component schemas under an explicit profile?
- DQ-04 — What exact V1→V2 adoption/migration semantics preserve accepted history and finally-closed state?
- DQ-05 — What precedence rules govern accepted repository state, historical accepted records, current operational state, drafts, conversation memory, administrator evidence, and live repository evidence?
- DQ-06 — What exact interface and authority boundary defines the future Continuity Overseer?
- DQ-07 — Where will Continuity Overseer durable state live without prematurely implementing V2-04?
- DQ-08 — How are provider capability classes represented without making provider capability a source of authority?
- DQ-09 — How will portable BCE/context export identify compatible V1/V2 record profiles?
- DQ-10 — How will boot/source package profiles identify canonical V2 artifacts?
- DQ-11 — What exact authority status does the future Official Project Plan artifact have?
- DQ-12 — What must V1 consumers do when they encounter V2 records: ignore safely, reject/stop, or require an explicit upgraded profile?

# 6. Preliminary schema/version strategies for administrator review

These are alternatives, not accepted design:

### Alternative A — V2 public compatibility family

Introduce a V2 compatibility/profile family such as `schemas/bce/2.0.0/`, keep V1 `1.x` immutable, prohibit numeric latest-wins selection, and require explicit compatibility/profile resolution. Development source identity may become `2.0.0-dev` when separately accepted.

### Alternative B — Continue the 1.x family

Extend as `1.3.0` or another `1.x` revision while defining explicit compatibility rules. This reduces apparent major schema churn but still requires a solution for non-cumulative V1 extensions.

### Alternative C — Component-schema composition

Define independent component schemas and compose them through an explicit compatibility profile. This may be precise but adds profile-resolution complexity.

The prior intake favored Alternative A as a preliminary recommendation, but the accepted V2 project plan leaves the exact strategy to V2-01. No alternative is accepted merely by appearing in this draft.

# 7. Preliminary affected reusable-product path classes

Subject to V2-01 acceptance and later implementation authorization, likely path classes are:

- `specs/` for the normative V2 architecture/compatibility contract;
- `schemas/bce/` only as required by the accepted schema/version strategy;
- `system-manifest.json` for registered normative artifacts/digests where required;
- `VERSION` only if/when an accepted development-version strategy requires it;
- `tools/validate_floppy.py` for compatibility validation;
- `tools/floppyctl.py` only for bounded package/profile compatibility where required;
- `tests/` for focused compatibility and regression proofs;
- `docs/Architecture.md` and/or `ABOUT.md` only where architecture documentation requires a public update;
- `project-seed/.floppy/` only if the accepted compatibility design proves a new durable compatibility marker is necessary.

No reusable-product path is authorized for mutation by this draft.

# 8. V1 capabilities expected to remain unchanged unless V2-01 evidence proves otherwise

- Floppies A–E role separation;
- Floppy E execution-authorization principle;
- Floppy 1E onboarding authority boundary;
- Floppy Z project-orchestrator role;
- v1 work-authorization semantics;
- v1 historical lifecycle states/transitions;
- deterministic project provisioning;
- single repository-writer invariant;
- status/role does not grant write authority;
- project-orchestrator handoff semantics;
- revision/closeout separation;
- portable context-export integrity model;
- final-project closure semantics;
- source/project repository separation; and
- immutable `v1.0.0` release history.

# 9. Compatibility risks to control

- assuming later V1 schema numbers supersede all earlier extension semantics;
- modifying V1 schemas in place;
- silently converting V1 project state to V2;
- reconstructing accepted state because a model lost context;
- allowing the Continuity Overseer to gain implicit implementation authority;
- extending the orchestrator registry in a backward-incompatible way;
- omitting required boot/source-package inventory updates;
- allowing portable-export consumer mismatch for unknown V2 records;
- reopening finally-closed V1 projects;
- treating the Official Project Plan as execution authority;
- letting provider documentation define lifecycle authority; and
- misreading historical provisioning tokens as current project-version defects.

# 10. Explicit V2-01 non-goals

V2-01 does not implement provider-specific onboarding (V2-02), accepted-state protection enforcement (V2-03), the Continuity Overseer (V2-04), the Official Project Plan generator/integration/release work (V2-05), automatic V1 migration, a V1 history rewrite, a V2-06 package, a GUI/installer, or any root `.floppy` integration into reusable `main`.

# 11. Acceptance evidence required before V2-01 can close

- no implementation ambiguity remains for V2-02 through V2-05;
- no silent v1 state conversion is required;
- no accepted v1 disposition is rewritten;
- all proposed new state has an explicit owner and lifecycle role; and
- exact version/schema compatibility rules are reviewable.

# 12. Current administrator decision required

The administrator may accept, revise, or reject this V2-01 work-package draft. Acceptance of this draft would establish a planning baseline only. Activation and implementation authority would remain separate decisions.

`V2 IMPLEMENTATION AUTHORITY = NONE`
