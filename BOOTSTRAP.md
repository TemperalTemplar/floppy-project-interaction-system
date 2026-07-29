# Bootstrap Instructions

The system supports two separate conversation roles. Do not silently combine them.

## 1. Floppy Z coordinator mode

Use this when Alva wants a coordinator to reconstruct project state and tell the active project model what to do.

Replace the bracketed values:

```text
Use the Floppy Project Interaction System from [SOURCE_REPOSITORY] at version, tag, or commit [SOURCE_VERSION_OR_COMMIT].

Load `orchestrator/Floppy_Z.md` from the source repository as the canonical Project Floppy coordinator. Verify it against the orchestrator digest in `system-manifest.json`. Treat the source repository as read-only.

Open [PROJECT_REPOSITORY]. Read `.floppy/manifest.json` first, then read the project files in its required order exactly as listed. Reconstruct the accepted project state, current Floppy E authorization, closeout status, and next required decision.

Remain in coordinator mode. Do not implement project work, edit either repository, create commits, perform closeouts, contact production, access credentials, or advance sections.

Tell me:
1. Which model or existing project conversation is responsible for the next action.
2. Exactly what I should paste into that project conversation.
3. What result that model should return.
4. How I can verify that it followed the Floppy system correctly.
```

Floppy Z may perform direct work only after Alva gives an explicit, named execution override as defined in `orchestrator/Floppy_Z.md`.

## 2. Direct project-model mode

Use this only when the current conversation is intended to perform the authorized project work.

```text
Use the Floppy Project Interaction System from [SOURCE_REPOSITORY] at version [SOURCE_VERSION].

Open [PROJECT_REPOSITORY]. Read `.floppy/manifest.json` first, then read the files in its `required_read_order` exactly as listed. Treat the source repository as read-only and the project repository as the only location for project-specific Floppies, revisions, handoffs, and evidence.

Produce the intake readiness report required by the project protocol. Do not begin implementation, edit files, create commits, or advance sections until I explicitly authorize the current Floppy E section.

When I request closeout, load the closeout protocol named in the project manifest and produce delta revisions only. Do not recreate unchanged Floppies. Create the next section's work package only as an inactive draft unless I explicitly authorize that section.
```

The project manifest is the authority for project-file locations and read order. Do not scan or load the entire repository when the manifest and active section identify a smaller sufficient set.
