# Floppy Mainline Status

This file identifies the intended relationship between the immutable released product and the repository's forward `main` branch.

## Latest stable release

The latest stable released Floppy product is:

- Release: `v2.0.0`
- Tag: `v2.0.0`
- Release commit: `88a0fa646973c4cb8e693cc4e7c512b537825fd2`

That tag is the canonical exact source for the released V2 product.

The released tag is immutable. Changes made later on `main` do not rewrite or silently revise the published V2 release.

## Current role of `main`

`main` is the **forward integration branch**.

Current `main` should be interpreted as:

`POST_V2_FORWARD_INTEGRATION_PRE_V3`

It may contain repository changes made after the V2 release, including:

- post-release documentation corrections;
- legal, authorship, provenance, citation, and trademark-boundary records;
- repository-support tooling and analytics;
- candidate planning for a future V3 release;
- later accepted forward-development integration when lawfully performed.

Therefore:

> `main` is not the immutable V2 release, and it is not automatically an accepted or released V3 product.

## V3 candidate status

The repository currently contains candidate V3 planning material under:

- `docs/v3/Floppy-V3-Project-Plan.md`
- `docs/v3/Floppy-V3-Project-Plan.json`

Those files identify the plan as `DRAFT_FOR_ADMINISTRATOR_ACCEPTANCE`.

Their presence on `main` does not by itself constitute:

- V3 plan acceptance;
- V3-01 authorization;
- V3 implementation authority;
- migration authority;
- integration authority;
- release authority;
- a `v3.0.0` release.

Until an explicit administrator decision and lawful repository transition establish otherwise, V3 remains candidate planning.

## `VERSION` interpretation

The root `VERSION` file remains `2.0.0` until a later accepted version transition changes it.

That value identifies the latest accepted product version. It does **not** mean that every forward-maintenance commit on `main` is byte-for-byte identical to the `v2.0.0` release tag.

For exact V2 source, use the `v2.0.0` tag.

For forward repository work, identify the exact `main` checkpoint or the later accepted development branch/checkpoint being used.

## Operational rule for AI and human participants

Do not infer project/release authority from branch names alone.

When operating on this repository:

1. If exact released V2 behavior is required, use `v2.0.0`.
2. If examining forward repository state, identify the exact `main` checkpoint.
3. If V3 development is later established, use the exact accepted V3 branch, worktree, and checkpoint recorded by the project state.
4. Do not treat candidate V3 documents as accepted merely because they exist on `main`.
5. Do not rewrite the immutable V2 tag to incorporate later `main` changes.
6. Do not describe current `main` as the exact V2.0.0 release.

## Release-line model

```text
v2.0.0 tag
88a0fa646973c4cb8e693cc4e7c512b537825fd2
        |
        | immutable released V2
        v
post-release documentation corrections
        |
        v
legal / provenance / citation additions
        |
        v
traffic analytics and repository support
        |
        v
candidate V3 planning
        |
        v
main
POST_V2_FORWARD_INTEGRATION_PRE_V3
```

A future accepted V3 development and release process may advance this model, but it must do so through explicit accepted project authority rather than reinterpret this file as authorization.
