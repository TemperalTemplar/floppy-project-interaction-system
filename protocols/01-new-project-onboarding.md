# New Project Onboarding and Initial Floppy Creation

Use this protocol only when a project is adopting the Floppy system for the first time or when the user explicitly orders a clean new project instance.

## Goal

Convert the project's real, verified state and the user's operating requirements into the first complete project-owned Floppy set without allowing the roadmap or current work section to absorb every future idea.

## Preconditions

- The project repository is identified.
- The `.floppy/` seed has been copied into that repository.
- The source repository is treated as read-only.
- The user has authorized onboarding, not implementation.

## Discovery

Inspect available project evidence before drafting. Identify:

- Project name and purpose
- Repository and environment boundaries
- Existing architecture and working components
- Known defects, blockers, risks, and deferred work
- User communication and approval requirements
- Major deliverables and dependencies
- The smallest useful first work section
- Facts that are verified, user-reported, proposed, or unknown

Do not ask the user to repeat information that is already available in the repository, supplied documents, or connected evidence.

## Classification

Place information according to role:

- **Floppy A:** durable Human-in-the-Loop rules for this project relationship
- **Floppy B:** known development issues and unresolved risks
- **Floppy C:** verified starting baseline, including already accepted or demonstrably working project state
- **Floppy D:** bounded roadmap, section order, dependencies, future ideas, deferred areas, and explicit out-of-scope areas
- **Floppy E:** exactly one current or proposed first work section

A future idea may be recorded in Floppy D without becoming authorized work. Visibility is not authorization.

## Draft review

Before final acceptance, present:

- Important assumptions and unknowns
- Proposed section boundaries
- Proposed first section and its acceptance criteria
- Items intentionally deferred or excluded
- Any conflict between project evidence and user statements

## Initial creation rule

Onboarding is the normal time to create all five complete Floppies. After the user accepts them:

- Mark Floppy A as sealed.
- Establish issue identifiers in Floppy B.
- Establish the accepted starting baseline in Floppy C.
- Establish section identifiers and dependencies in Floppy D.
- Establish exactly one current section in Floppy E, or state that no work is yet authorized.

Do not begin implementation merely because onboarding is complete. Produce an intake readiness report and wait for explicit authorization.

## Existing project adoption

For an established codebase, onboarding must describe the verified current state rather than pretending the project is starting from zero. Historical uncertainty should be labeled; it should not be invented or erased.
