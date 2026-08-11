# New Project Onboarding and Initial Roadmap Creation

Use this protocol only when a project is adopting the Floppy system for the first time or when the user explicitly orders controlled re-onboarding.

Canonical controller:

```text
onboarding/Floppy_1E.md
```

Floppy 1E is read-only source-system infrastructure. It guides onboarding but does not become project state and does not authorize implementation.

## Goal

Convert the project's real, verified state and the user's operating requirements into:

- A project outcome contract
- A bounded, dependency-aware section roadmap
- Testable acceptance criteria
- The first complete project-owned Floppy set
- A closed active Floppy E
- An inactive first-section draft
- Machine-readable and user-readable roadmap records

The roadmap must help the user understand the path to completion and help later models execute one accepted section at a time.

## Preconditions

- The project repository is identified.
- The `.floppy/` seed has been copied into that repository.
- The source repository is pinned and treated as read-only.
- Canonical Floppy 1E is loaded and its digest is verified when practical.
- The user has authorized onboarding, not implementation.

## Required load order

When the project manifest status is `onboarding_required`:

1. Read `system-manifest.json` from the pinned source version.
2. Read canonical `onboarding/Floppy_1E.md`.
3. Read this onboarding protocol.
4. Read the project's `.floppy/manifest.json`.
5. Read the project's local files in `required_read_order`.
6. Inspect only the project evidence required for onboarding.

After onboarding is accepted, ordinary sessions do not reload Floppy 1E unless the user explicitly orders controlled re-onboarding.

## Discovery

Inspect available project evidence before drafting. Identify:

- Project name, purpose, and primary operator
- Desired observable final outcome
- Repository and environment boundaries
- Existing architecture and working components
- Known defects, blockers, risks, and deferred work
- User communication and approval requirements
- Security, production, budget, hardware, platform, and support constraints
- Major deliverables and dependencies
- The smallest useful first work section
- Facts that are verified, user-reported, proposed, assumed, deferred, excluded, or unknown

Do not ask the user to repeat information already available in the repository, supplied documents, connected evidence, or prior accepted records.

## Question control

Ask only questions that materially change purpose, scope, architecture, security, cost, production behavior, acceptance criteria, or section order.

Recommend routine technical decisions. Do not force the user to translate requirements into modules, functions, schemas, tests, or deployment commands.

## Project definition

Create the project outcome contract required by Floppy 1E. The project-level acceptance statement must be observable and must identify what the user will be able to do when the project is complete.

Record the accepted definition in:

```text
.floppy/onboarding/initial-project-definition.md
```

## Roadmap construction

Create sections with coherent acceptance boundaries. Each section must define:

- Purpose and user-visible outcome
- Dependencies and starting evidence
- Permitted and prohibited actions
- Scope and exclusions
- Deliverables
- Automated and manual validation
- Safety controls and stop conditions
- Recovery or safe-abort path
- Required user decisions
- Testable acceptance criteria
- Closeout artifacts
- Inactive next-section draft requirement

Separate read-only discovery, local writes, production writes, credential work, destructive operations, packaging, release, and final validation when combining them would weaken safety or acceptance.

Record the roadmap in:

```text
.floppy/roadmap/roadmap.json
.floppy/roadmap/roadmap.md
```

The JSON is authoritative for machine-readable section identity, dependencies, statuses, and authorization. The Markdown file is the user-readable explanation.

## Classification into project Floppies

- **Floppy A:** durable Human-in-the-Loop rules for the project relationship
- **Floppy B:** known development issues, risks, and unresolved decisions with stable identifiers
- **Floppy C:** verified and explicitly accepted starting baseline
- **Floppy D:** project map and bounded roadmap summary referencing the roadmap files
- **Floppy E:** exactly one current authorization, which remains closed unless the user separately authorizes the first section

A future idea may be recorded in Floppy D or the deferred backlog without becoming authorized work. Visibility is not authorization.

## Draft review

Before writing accepted state, present:

- Project definition
- Verified starting state
- Assumptions and unknowns
- Recommended section roadmap
- Section dependencies
- Proposed first section
- Acceptance evidence for the first section
- Items intentionally deferred, excluded, or rejected
- Risks requiring later approval
- Exact user decisions still required

Use a compact roadmap table with section, outcome, dependency, acceptance evidence, and status.

## Roadmap acceptance

The roadmap becomes accepted only when the user explicitly approves it or approves a revised final version.

Record acceptance in:

```text
.floppy/onboarding/roadmap-acceptance.md
```

The record must preserve the roadmap version, accepted sections, deferred and excluded items, remaining unknowns, evidence boundary, acceptance authority, and first-section authorization status.

Do not manufacture an acceptance phrase or infer acceptance from silence.

## Initial creation rule

Onboarding is the normal time to create or finalize all five complete project Floppies. After the user accepts the roadmap:

- Mark Floppy A as sealed.
- Establish issue identifiers in Floppy B.
- Establish the accepted starting baseline in Floppy C.
- Establish section identifiers and dependencies in Floppy D and the roadmap files.
- Keep active Floppy E at `NO_ACTIVE_WORK_AUTHORIZATION` unless the user separately authorizes Section 01.
- Create `.floppy/templates/Floppy-E-Section-01.draft.md` with `STATUS: DRAFT_NOT_AUTHORIZED`.
- Update the project manifest onboarding and roadmap status.
- Preserve the canonical Floppy 1E source path and digest as provenance.

Do not begin implementation merely because onboarding is complete.

## Completion report

After accepted project-file creation, report:

```text
Onboarding:
ACCEPTED AND RECORDED

Roadmap version:
[VERSION]

Project Floppies:
A–E CREATED OR FINALIZED

Current active section:
NONE, unless separately authorized

First section draft:
CREATED — NOT AUTHORIZED

Next action:
User reviews and explicitly authorizes the first Floppy E work package.
```

## Existing project adoption

For an established codebase, onboarding must describe the verified current state rather than pretending the project starts from zero. Existing working behavior belongs in Floppy C and must be preserved. Historical uncertainty must be labeled, not invented or erased.

## Re-onboarding boundary

Ordinary roadmap revisions do not rerun Floppy 1E. Load it again only when the user explicitly orders controlled re-onboarding because the project purpose or completion path has materially changed. Preserve the earlier accepted roadmap as historical evidence.

<!-- V2_02_USER_ONBOARDING_BEGIN -->
## V2 route-aware entry

Before this project-onboarding protocol begins, V2 user onboarding identifies Route A (idea only), Route B (existing non-Floppy project), or Route C (existing Floppy project). Route B must preserve existing code/evidence/history/architecture/behavior before formal adoption. Route C does not restart this protocol merely because conversation context was lost; it reads `.floppy/manifest.json` first and continues from accepted state.

<!-- V2_02_USER_ONBOARDING_END -->

<!-- V2_03_ACCEPTED_STATE_CONTINUITY_BEGIN -->
## V2-03 accepted-state establishment

For a new project accepted under a V2-03-capable source, roadmap acceptance must atomically establish `.floppy/accepted-state.json` and `.floppy/manifest.json#accepted_state_continuity` with status `ACTIVE`.

Generate `project_id` once as a random canonical lowercase UUIDv4. Do not derive it from repository identity, paths, Git state, administrator identity, provider, model, conversation, scope, or outcome.

The `ORIGINAL` protected state must bind the accepted project origin, original intent, accepted scope, and accepted plan. Its digest is lowercase SHA-256 of `json.dumps(protected_state, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")`.

The accepted-state record grants no implementation authority and creates no repository writer. Route C context recovery must read an existing accepted-state record when activation is present and must not reconstruct it from conversation memory.

An older Floppy project with no prior V2-03 activation remains a valid legacy project. Adoption requires explicit controlled acceptance; no automatic backfill or fabricated project ID is permitted.
<!-- V2_03_ACCEPTED_STATE_CONTINUITY_END -->

<!-- V2_04_PROJECT_ACCEPTANCE_CONTINUITY_BEGIN -->
## V2-04 project-acceptance continuity handoff

For a project lawfully adopting V2-04, V2-03 accepted-state establishment is
the origin authority. After that accepted origin exists, determine the
Continuity Overseer and initial Project Orchestrator identities, calculate the
shared-origin digest, establish durable V2-04 linkage, commit it where Git
applies, and only then render the paired prompts from the same exact checkpoint
and authority state.

Present the two prompts together for separate conversations. Do not create the
conversations automatically and do not infer implementation authority from
paired prompt issuance.
<!-- V2_04_PROJECT_ACCEPTANCE_CONTINUITY_END -->
