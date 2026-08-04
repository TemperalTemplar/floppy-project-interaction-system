STATUS: DRAFT_NOT_AUTHORIZED

# Floppy E - FS-08 Draft

## Section

`FS-08 - Validated boot-package ZIP and checksum manifest`

## Authority state

```text
Work package: NOT ACCEPTED
Status: DRAFT_NOT_AUTHORIZED
Active: NO
Authorized: NO
Implementation: NOT STARTED
Active authorization: NONE
Repository writer: NONE
```

## High-level objective

Define and validate one Windows boot-package ZIP and one checksum manifest after
FS-08 is separately reviewed, accepted, and authorized.

## Deferred until separate FS-08 review and authorization

- Exact reusable-product paths and test inventory.
- ZIP name, layout, included files, and archive rules.
- Checksum algorithm, manifest schema, and verification interface.
- Packaging or runtime-bundling architecture.
- Dependency selection.
- Export behavior.
- Migration behavior.
- End-user command and application interface.

## Controlling Windows-release requirement

Python may remain an internal implementation language and may remain in the source repository. The finished Windows release must not require ordinary users to install Python, configure PATH, download loose .py files, or manually execute Python commands. Temporary Python runners are administrator-side construction tools only.

## Explicit prohibitions

This draft does not activate or accept FS-08. It does not authorize
implementation, create a ZIP, create a checksum manifest, create a release
artifact, select dependencies, establish export or migration behavior, or make
ordinary manual Python execution the end-user interface.

FS-08 remains inactive, unaccepted, and unauthorized. Active authorization and
repository writer are `NONE`.
