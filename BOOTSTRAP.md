# Short Bootstrap Instruction

Use this in a new conversation after replacing the bracketed values:

```text
Use the Floppy Project Interaction System from [SOURCE_REPOSITORY] at version [SOURCE_VERSION].

Open [PROJECT_REPOSITORY]. Read `.floppy/manifest.json` first, then read the files in its `required_read_order` exactly as listed. Treat the source repository as read-only and the project repository as the only location for project-specific Floppies, revisions, handoffs, and evidence.

Produce the intake readiness report required by the project protocol. Do not begin implementation, edit files, create commits, or advance sections until I explicitly authorize the current Floppy E section.

When I request closeout, load the closeout protocol named in the project manifest and produce delta revisions only. Do not recreate unchanged Floppies.
```

The project manifest is the authority for file locations and read order. Do not scan or load the entire repository when the manifest and active section identify a smaller sufficient set.
