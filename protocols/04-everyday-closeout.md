# Everyday Session Closeout — Delta Handoff

Use this protocol when the user requests closeout for an existing project.

## Purpose

Preserve the session's exact stopping point while minimizing context growth. Ordinary closeout produces **deltas**, not full replacement Floppies.

## Freeze

Stop starting new implementation. Record:

- Current section and status
- Session objective
- Last completed action
- Exact continuation point
- Tests and verification state
- User acceptance state
- Pending decision or blocker

## Normal output

Create two compact project-owned records:

1. A **revision packet** using `.floppy/templates/revision-packet.md`
2. A **session handoff** using `.floppy/templates/session-handoff.md`

Do not rewrite or recreate unchanged Floppies.

## Per-Floppy revision rules

### Floppy A

Floppy A is sealed after onboarding. Ordinary closeout must state `NO CHANGE`. Do not rewrite it. A durable change requires an explicit user-authorized amendment process outside ordinary closeout.

### Floppy B

Record only issue deltas:

- Add issue
- Update status or evidence
- Mark resolved, blocked, deferred, or superseded

Preserve issue identifiers. Do not regenerate the full issue register.

### Floppy C

Add only accepted baseline increments. If the user has not accepted the section, state `NO BASELINE CHANGE — ACCEPTANCE PENDING`.

### Floppy D

Record only changed section statuses, dependencies, roadmap entries, or scope boundaries. Future ideas remain future and do not become active through closeout.

### Floppy E

For the same current section, record only progress, status, remaining work, tests, blockers, and the exact continuation point. Replace Floppy E only when the user explicitly authorizes a different section.

## Technical evidence

Include a small evidence appendix only when needed to preserve commands, errors, test results, repository state, or operational consequences. Summarize long logs and exclude secrets.

## Validation

Before delivery, confirm:

- A is unchanged.
- C contains no unaccepted work.
- D and E identify the same current section.
- Open issues have stable B identifiers.
- The continuation point is exact.
- Future sections were not activated.
- Untested claims are labeled.
- The next model's authority is explicit.

## Output order

1. Compact session handoff
2. Revision packet
3. Evidence appendix, only if needed
4. Validation result

Do not apply the revision packet automatically unless the user has separately authorized revision application. Do not perform additional implementation during closeout.
