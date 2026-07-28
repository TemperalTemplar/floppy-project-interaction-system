# Active Session Operating Rules

These rules apply after the user authorizes the current Floppy E section.

## Scope control

- Work only toward Floppy E's objective and completion conditions.
- Use Floppy D to understand dependencies, not to activate future work.
- Record unrelated discoveries for Floppy B rather than fixing them automatically.
- Preserve Floppy C's accepted baseline unless the user explicitly reopens it.
- Treat cleanup, redesign, migration, rotation, deployment, and adjacent fixes as out of scope unless named in Floppy E.

## Evidence-first work

Inspect the real repository, branch, files, tests, and runtime evidence when available. State when a fact is unverified. Do not replace inspection with generic assumptions.

## Change discipline

- Modify only required files.
- Keep working code intact.
- Explain high-impact commands before execution.
- Identify target, expected effect, possible disruption, validation, and recovery.
- Never expose secret values in prompts, Floppies, logs, or handoffs.

## Progress and decisions

Routine implementation choices within accepted scope belong to the technical worker. Escalate only decisions that materially change scope, architecture, security, cost, production behavior, or acceptance criteria.

## Completion boundary

Implementation completion, testing completion, and user acceptance are separate states. Do not advance Floppy D or Floppy C to an accepted state until the user accepts the section.

## Closeout trigger

Closeout occurs only when the user requests it. At that moment, stop starting new work and follow the closeout protocol from the project manifest.
