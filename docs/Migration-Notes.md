# Prototype-to-Development Migration Notes

The supplied ZIP is preserved unchanged under `legacy/prototype-v0/`.

Version `0.2.0-dev` adds:

- A clear source-repository versus project-repository boundary
- A machine-readable source manifest
- A short bootstrap instruction
- New-project onboarding and initial Floppy creation
- A bounded active-session protocol
- Delta-based everyday closeout
- A separate revision-application gate
- Project-owned `.floppy/` seed templates
- Guarded project initialization and validation tools
- Tests for initialization and validation

The source is still marked development status. No stable `v1.0.0` release or license has been declared.

## FS-01 lifecycle specification addition

The `0.4.1-dev` development line adds an FS-01 formal lifecycle specification:

- a human-readable lifecycle state model;
- a declarative JSON transition table;
- explicit orthogonal lifecycle dimensions;
- stable lifecycle state and transition identifiers;
- preconditions, human-authority requirements, inputs, outputs, stop conditions,
  and forbidden side effects for each transition;
- a one-active-implementation-section invariant;
- valid and invalid lifecycle fixtures;
- standard-library tests;
- source-manifest SHA-256 registration and integrity checks;
- three draft, non-normative schema candidates.

This addition does not migrate an existing adopting project. It does not alter
the project seed, initializer output, accepted project Floppies, roadmaps, or
project-mode validation behavior.

The candidate schemas under `schemas/drafts/` are not FS-02 deliverables. Each
records:

```text
status: draft_non_normative
normative_section: FS-02
current_section: FS-01
production_enforcement: false
```

No migration, schema adoption, integration, merge, tag, release, FS-02 work, or
FS-03 work is implied or authorized by the presence of these artifacts.

<!-- V2_05_OPP_MIGRATION_BEGIN -->
## V2.0.0 OPP adoption and migration

No existing V1 project is automatically migrated or assigned an OPP/project UUID. Supported V1 projects may continue under their exact V1 profile. Explicit V2 adoption may establish accepted-state/OPP origin from verified existing state without rewriting V1 history. Any real migration remains a separately authorized operation.
<!-- V2_05_OPP_MIGRATION_END -->
