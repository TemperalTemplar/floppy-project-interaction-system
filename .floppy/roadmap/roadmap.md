# BCE Control Layer Development Roadmap

```text
Development roadmap:
ACCEPTED

FS-01 work package:
ACCEPTED AS PLANNING BASELINE

FS-01 activation:
NOT AUTHORIZED

Active implementation section:
NONE

FS-01 implementation:
NOT STARTED

Active work authorization:
NO_ACTIVE_WORK_AUTHORIZATION
```

## Sections

1. **FS-01 — Formal Lifecycle and State-Transition Specification**
2. **FS-02 — Normative Machine-Readable BCE Schemas**
3. **FS-03 — Semantic Validator 2.0 Engine**
4. **FS-04 — Read-Only floppyctl Core**
5. **FS-05 — Closeout-Completeness Validator**
6. **FS-06 — Structured Authorization, Work-Package Integrity, and Git Checkpoints**
7. **FS-07 — Secret and Unsafe-Content Scanning**
8. **FS-08 — Boot-Package Generation and Verification**
9. **FS-09 — Controlled Lifecycle Write Commands**
10. **FS-10 — Migration Planning and Application**
11. **FS-11 — Final-Project Closure**
12. **FS-12 — BCE Export, Integrity, and History Compaction**

## Section status

| Section | Work package / plan | Activation | Implementation |
|---|---|---|---|
| FS-01 | `ACCEPTED AS PLANNING BASELINE` | `NOT AUTHORIZED` | `NOT STARTED` |
| FS-02 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` |
| FS-03 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` |
| FS-04 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` |
| FS-05 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` |
| FS-06 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` |
| FS-07 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` |
| FS-08 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` |
| FS-09 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` |
| FS-10 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` |
| FS-11 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` |
| FS-12 | `PLANNED_NOT_AUTHORIZED` | `NOT AUTHORIZED` | `NOT STARTED` |

## Dependency and activation rules

- FS-01 is first.
- Each later section depends on acceptance and controlled closeout of the preceding
  section unless an accepted roadmap revision changes that dependency.
- Only one implementation section may be active.
- Roadmap acceptance never activates a section.
- Work-package acceptance never activates a section.
- Draft creation never activates a section.
- Section acceptance, implementation completion, verification, closeout, and next
  activation remain separate states and decisions.
- FS-01 implementation requires a separate exact administrator authorization.

The machine-readable companion is `.floppy/roadmap/roadmap.json`.
