# Required Floppy Fields

These are content requirements, not a requirement to use YAML or another particular syntax.

## Floppy A

- Project/user authority model
- Communication requirements
- Approval boundaries
- Safety and destructive-action rules
- Expected implementation format
- Acceptance and closeout behavior
- Seal statement and acceptance date

## Floppy B issue record

- Stable issue ID
- Title
- Status
- Relevant section
- Description or observed behavior
- Evidence level
- Impact
- Work attempted
- Current blocker
- Next safe action
- Authorization requirement

## Floppy C baseline increment

- Accepted section or baseline identifier
- Acceptance date or acceptance reference
- Verified facts and completed deliverables
- Tests or evidence supporting the state
- Active constraints
- Superseded baseline references, when applicable

## Floppy D section record

- Stable section ID and name
- Status
- Objective
- Dependencies
- Scope summary
- Acceptance gate
- Deferred or out-of-scope relationships

## Floppy E

- Current section ID and name
- Status
- Authorized objective
- In scope
- Out of scope and prohibited actions
- Completion conditions
- Stop conditions
- Relevant B issues
- Progress and continuation point
- Required tests
- Pending approvals
- Next model authorization

## FS-01 lifecycle content boundary

FS-01 adds formal lifecycle concepts without making the draft JSON schemas
normative. Project records may use Markdown, JSON, or another reviewable format,
but the content must preserve the following distinctions.

### Lifecycle snapshot

A lifecycle snapshot identifies:

- Stable lifecycle state ID
- Roadmap state
- Work-package state
- Human-authority state
- Implementation state
- Verification state
- Administrator-acceptance state
- Closeout state
- Migration state
- Final-closure state
- Active implementation section, when one exists
- Relevant exact authorization ID
- Accepted base checkpoint

At most one implementation section may be active.

### Exact work authorization

An implementation authorization identifies at least:

- Authorization ID and kind
- Explicit human authority and decision
- Exact section
- Repository
- Accepted base checkpoint
- Source version
- Branch and worktree
- Exact file scope
- Required validation
- Ordered commit sequence
- Push boundary
- Forbidden side effects
- Administrator-acceptance status
- Closeout boundary
- Integration boundary
- Later-section boundary

Work-package acceptance is not a substitute for exact implementation
authorization.

### Lifecycle transition record

A transition record identifies:

- Stable transition ID
- Source state ID or IDs
- Destination state ID
- Changed dimensions
- Preconditions
- Required human authority
- Required inputs
- Required outputs
- Stop conditions
- Forbidden side effects

A transition record is declarative. Recording or validating it does not execute
the transition or grant authority.

### Draft schema status

The files under `schemas/drafts/` are FS-01 review candidates only. They are
non-normative, not production-enforced, and do not activate FS-02.

## Deterministic project control-state provisioning (FS-11)

Every newly provisioned project must contain these canonical project-owned
records:

```text
.floppy/lifecycle-state.json
.floppy/manifest.json
.floppy/orchestrator-registry.json
```

`lifecycle-state.json` uses the normative BCE lifecycle-state 1.0.0 schema and
starts at `LC-ONBOARDING-REQUIRED`. Its initial dimensions are roadmap
`ONBOARDING_REQUIRED`, work package `NOT_ACCEPTED`, authority
`NO_ACTIVE_WORK_AUTHORIZATION`, implementation and verification `NOT_STARTED`,
acceptance `PENDING`, closeout `NOT_PROPOSED`, migration `NONE`, and final
closure `OPEN`. `active_implementation_sections` is empty.

The manifest `control_state` object must include:

- `provisioning_version`: `1`
- `status`: `TEMPLATE` in the source seed or `PROVISIONED` in a project
- canonical lifecycle-state and orchestrator-registry paths
- lifecycle-state schema path
- repository, branch, worktree, and checkpoint identity
- serialization profile `UTF-8/LF/canonical-json-v1`
- `implementation_authority`: `false`

The orchestrator registry `project_checkpoint` object must exactly match the
manifest control-state identity. The initial registry must have no repository
writer and no writer-authorization reference. Provisioning status and
serialization metadata must agree with the manifest.

The initializer must stage and validate the complete tree before atomic
installation, reject an existing destination, reject symlink or reparse-point
inputs, remove partial output on failure, and produce the same bytes for the
same inputs. Initialization never grants implementation authority.
