# Floppy V2 Architecture and Compatibility Contract

**Work package:** `V2-01 — V2 Architecture and Compatibility Contract`  
**Strategy:** `Alternative A — explicit V2 compatibility/profile family`  
**V2 compatibility profile:** `2.0.0`  
**Development source identity:** `2.0.0-dev`

## 1. Purpose

V2-01 defines the compatibility composition layer between the published Floppy
V1 system and future Floppy V2 capabilities. It does not redesign V1 and does
not implement V2-02 through V2-05.

The controlling rule is:

> **Context loss is not authority to reconstruct accepted work.**

Committed accepted repository state remains authoritative until changed through
an explicit lawful revision, supersession, adoption, or migration mechanism.

## 2. Version and schema strategy

V2 uses an explicit `2.0.0` compatibility/profile family. Existing V1 schemas
remain immutable:

- `schemas/bce/1.0.0/*`
- `schemas/bce/1.1.0/*`
- `schemas/bce/1.2.0/*`

The V2 profile composes with those contracts; it does not replace them.

Schema selection is exact and profile-driven. Numeric ordering is forbidden.
In particular, lifecycle schema `1.2.0` does not automatically supersede
`1.1.0`; the two extensions represent distinct accepted V1 contract families.

The machine-readable source of truth is
`specs/v2-compatibility-profile.json`, validated by
`schemas/bce/2.0.0/bce-compatibility-profile.schema.json`.

## 3. Compatibility resolution

Resolution uses these exact selector fields:

1. `source_lineage`
2. `lifecycle_schema`
3. `verification_only_extension`
4. `final_closure_extension`
5. `compatibility_profile`

A supported result is lawful only when every selector field is present and
exactly one registered combination matches.

Safe-failure behavior:

- missing selector information: `STOP / AMBIGUOUS_PROFILE`;
- more than one match: `STOP / AMBIGUOUS_PROFILE`;
- no match: `STOP / UNSUPPORTED_PROFILE`;
- unknown future records/profile markers: `STOP / UNSUPPORTED_PROFILE`.

A consumer must not guess a nearest, newest, or numerically highest schema.

## 4. Supported V1 recognition

V2 tooling recognizes without migration:

- V1 base lifecycle `1.0.0`;
- V1 verification-only lifecycle `1.1.0`;
- V1 final-closure lifecycle `1.2.0`.

Recognition is read/validation compatibility only. It does not create V2 state,
change a project version, reopen a finally closed project, rewrite accepted
dispositions, or authorize migration.

## 5. V1-to-V2 adoption and migration

Five dispositions are normative:

### `CONTINUE_V1`
The project remains V1. V2 tooling may recognize and validate the exact
supported V1 profile. No V2 adoption or migration is implied.

### `V2_ADOPTION_OPTIONAL`
The project may remain V1, or the administrator may explicitly select V2
adoption. Merely using a V2-capable model, tool, or provider is not adoption.

### `V2_ADOPTION_REQUIRED`
A requested capability requires durable V2-only state. The operation stops
before that write. Explicit administrator-approved V2 adoption is required and,
when existing durable state must be transformed, migration must be separately
authorized.

### `V2_ADOPTION_DEFERRED`
V2 adoption is possible but a prerequisite is not yet satisfied. Existing V1
state remains authoritative and work may continue only within the lawful V1
boundary.

### `UNSUPPORTED_INCOMPATIBLE`
The observed state/profile is unknown, contradictory, ambiguous, or unsupported.
The consumer stops. No inference or silent migration is permitted.

Automatic V1-to-V2 migration is forbidden in every disposition.

## 6. Accepted-state precedence and evidence roles

For reconstruction and compatibility reasoning, sources are considered in this
order:

1. committed accepted repository state;
2. historical accepted records;
3. current operational state;
4. drafts;
5. explicit administrator evidence;
6. live repository evidence;
7. conversation memory.

The entries have different semantics. Committed accepted repository state is
accepted-state truth. Historical accepted records preserve immutable lineage.
Current operational state governs continuation when non-conflicting. Drafts are
proposals only. Explicit administrator evidence may authorize or accept an
exact known action/artifact, but it does not authorize reconstruction of
different accepted content and must be applied through the lawful lifecycle
mechanism. Live repository evidence can prove Git/file facts but not acceptance
by itself. Conversation memory is advisory only.

No lower source may silently rewrite a higher accepted source.

## 7. Provider capability classes

Provider capability describes technical access only. It is not Floppy authority.

- **CLASS A:** direct repository read, bounded repository write, command
  execution, and artifact transfer are technically available.
- **CLASS B:** direct repository read is technically available; repository
  mutations are administrator-applied. General local command execution is not
  available in the accepted Class B profile, and artifact transfer remains
  technically available.
- **CLASS C:** no direct repository write or command execution is available;
  administrator-mediated commands or artifact transfer are required.

For every class, capability does not grant work authorization, repository-writer
status, acceptance authority, migration authority, or release authority.

Provider-specific onboarding belongs to V2-02 and is not implemented here.

## 8. Future Continuity Overseer authority boundary

V2-01 defines only the architectural boundary for the future V2-04 Continuity
Overseer.

A future Continuity Overseer may read accepted roadmap/control/evidence,
check continuity and succession completeness, prepare handoff evidence between
orchestrators, and report conflicts.

By role alone it may not grant implementation or migration authority, become
repository writer, accept work, apply closeout, migrate project state, modify
`main`, merge, tag, integrate, release, or implement V2 work packages.

No Continuity Overseer runtime behavior or durable V2-04 record is implemented
during V2-01.

## 9. Future Official Project Plan semantics

The future V2-05 Official Project Plan is a planning artifact. After explicit
administrator acceptance it may become the authoritative planning baseline for
the project it describes. Neither existence nor acceptance of that plan grants
implementation authorization, migration authorization, repository-writer
status, integration/merge authority, tag authority, or release authority.

The V2-05 plan generator is not implemented during V2-01.

## 10. V2 development-control compatibility

Root `.floppy/` development control is branch-local control state and remains
excluded from clean reusable-source integration.

V1 lifecycle schemas accept only `FS-xx` section identifiers. A V2 work package
such as `V2-01` must not be falsified into an `FS-xx` field. When the frozen V1
lifecycle structure is used as a compatibility representation for V2 source
development control:

- `section` remains `null`;
- `active_implementation_sections` remains empty;
- exact V2 work-package identity is recorded in V2 development-control records;
- the V1 authority dimension may represent an exact implementation
  authorization without changing the V1 schema.

The source validator distinguishes this V2 development-control mode from a
normal initialized V1 project BCE.

## 11. Package and validation impact

The validated boot/source package includes the V2 architecture specification,
compatibility profile, and compatibility-profile schema.

Source validation verifies profile/schema registration and digests, Draft
2020-12 validity, exact supported combinations, frozen V1 identities,
prohibition on numeric latest-version inference, no automatic migration,
accepted-state precedence, provider capability/authority separation, and
future V2-04/V2-05 non-implementation boundaries.

## 12. Non-goals

V2-01 does not implement provider-specific onboarding, accepted-state
enforcement, Continuity Overseer runtime behavior, orchestrator succession
runtime behavior, Official Project Plan generation, automatic migration, GUI,
installer, executable packaging, public release, integration into `main`, or
V2-02 through V2-05.

<!-- V2_02_CLASS_B_SUPERSESSION_BEGIN -->
## V2-02 controlling Class-B supersession

Under explicit `V2_02_IMPLEMENTATION` authority, V2-02 supersedes the future operational Class-B transport semantics without reopening V2-01. The original V2-01 acceptance remains immutable in Git history. For future V2 operation, Class B means direct repository read is available while repository mutations are administrator-applied. Provider capability remains technical transport only and grants neither Floppy authority nor repository-writer status.

V2-01 reopened: **NO**.
<!-- V2_02_CLASS_B_SUPERSESSION_END -->

<!-- V2_04_IMPLEMENTED_CONTINUITY_BEGIN -->
## 13. V2-04 implemented continuity/succession capability

V2-04 lawfully supersedes only the earlier V2-01 **future capability**
description for Continuity Overseer runtime support. Historical V2-01 text and
acceptance remain unchanged.

Current V2-04 source support provides:

- a distinct Continuity Overseer record schema;
- a distinct Project Orchestrator succession record schema;
- project-side presence and continuity validation;
- deterministic `CO-<project_id>` identity;
- deterministic shared-origin hashing from V2-03 ORIGINAL accepted state;
- authority-state fingerprinting and stale-handoff STOP behavior;
- normal and repository-backed recovery succession;
- paired Continuity Overseer / Project Orchestrator bootstrap instructions;
- material scope-drift surfacing without AI revision authority.

The compatibility-profile family and its schema remain `2.0.0`. Existing V1
schemas remain immutable. The historical
`future_record_families.continuity_overseer.implemented` flag remains `false`
because its frozen V2-01 schema defines that historical allocation; its
`semantics` now explicitly records the V2-04 implemented supersession. Current
implementation status is registered separately in `system-manifest.json`.

Authority by existence remains false, repository-writer status by role remains
false, and automatic migration/authority transfer/conversation creation remain
forbidden.
<!-- V2_04_IMPLEMENTED_CONTINUITY_END -->
