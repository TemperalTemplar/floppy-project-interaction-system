# Revision Application Protocol

A closeout revision packet is a proposed delta. Apply it to project-owned Floppies only after the user accepts or authorizes the packet.

## Rules

- Modify the project repository only; never the source repository.
- Apply only the listed delta.
- Do not rewrite unchanged sections for style or consistency.
- Preserve identifiers, dates, acceptance boundaries, and historical records.
- Never update sealed Floppy A through this ordinary process.
- Append to Floppy C only when acceptance is explicit.
- Replace Floppy E only when a new section is explicitly authorized.
- Record the applied revision packet's identifier in `.floppy/manifest.json` or the applicable Floppy history field.

## Safe sequence

1. Verify the current project Floppies match the packet's stated base state.
2. Report any conflict or stale packet before editing.
3. Apply B, C, D, and E deltas in that order when applicable.
4. Validate cross-document consistency.
5. Commit the changes with a message that names the revision packet.
6. Preserve the packet under `.floppy/revisions/`.

A packet that conflicts with newer accepted project state must not be applied silently.

<!-- V2_03_ACCEPTED_STATE_CONTINUITY_BEGIN -->
## V2-03 protected accepted-state revision rule

If `.floppy/manifest.json#accepted_state_continuity` is `ACTIVE`, a project-level change to protected accepted state is lawful only when the administrator explicitly accepts that project-level revision.

The revision operation must verify the current record against its committed base, preserve `project_id` and `original` exactly, preserve every existing accepted revision object exactly and in order, append the new accepted revision, set `supersedes_revision_id` to the previously current revision, record explicit administrator acceptance, calculate the exact canonical protected-state digest, and advance `current_accepted_revision` only to the newly appended revision.

Do not rewrite an older accepted revision merely to label it superseded. `CURRENT_ACCEPTED` and `SUPERSEDED_BUT_HISTORICAL` are derived from the current pointer while immutable history remains unchanged. Ordinary section revisions that do not change protected accepted project state do not append accepted-state history.

Any historical mutation or non-append replacement must stop with deterministic accepted-state continuity failure rather than being silently reconciled.
<!-- V2_03_ACCEPTED_STATE_CONTINUITY_END -->
