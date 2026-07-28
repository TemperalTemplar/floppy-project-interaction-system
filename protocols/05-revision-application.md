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
