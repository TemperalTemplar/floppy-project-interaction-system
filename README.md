# Floppy Project Interaction System

**Status:** stable release, version `2.0.0`

The Floppy Project Interaction System is a reusable Human-in-the-Loop project-control layer for AI-assisted development. This repository is the **source of the system**, not the active record for every project that uses it.

A project adopts the system by copying the project seed into that project's own repository. From that point forward, the project owns its Floppies, roadmap, revisions, handoffs, and evidence. Normal project sessions must not write project data back to this source repository.

## New to Floppy? Start here

You do **not** need to understand Floppies A-E, BCE lifecycle states, work packages, or Floppy's internal governance before trying it.

Open a new ChatGPT conversation, paste the prompt below, and then describe your project naturally when ChatGPT asks. The model should determine whether you have only an idea, an existing repository that needs to adopt Floppy, or an existing project that already contains `.floppy/` state.

```text
I want to use the Floppy Project Interaction System to manage this project.

Canonical Floppy source:
https://github.com/TemperalTemplar/floppy-project-interaction-system

Use stable release/tag:
v2.0.0

Begin by reading `BOOTSTRAP.md` and `system-manifest.json` from the Floppy source repository. Treat that repository as the canonical read-only Floppy system.

I am a new Floppy user. Do not assume I understand Floppy, BCE, lifecycle states, Floppies A-E, work packages, or its internal governance terminology.

First ask me to describe the project I want to build or continue. Let me explain it naturally.

Then determine whether:
- I only have an idea and no project repository yet;
- I have an existing project or repository that has not adopted Floppy; or
- my project already contains a `.floppy` control environment.

If I provide a repository and you can access it, inspect the existing project before asking questions the repository can already answer.

If Floppy has not yet been initialized for the project, guide me through the required repository and `.floppy` initialization without beginning implementation.

When formal onboarding is required, load the canonical Floppy 1E onboarding controller and use it to establish the project outcome, verified starting state, requirements and constraints, assumptions and unknowns, bounded roadmap, acceptance criteria, deferred or excluded work, and first proposed work section.

Ask questions in ordinary language. Explain Floppy concepts only when I need them to make a decision. Recommend routine technical choices instead of making me design every implementation detail.

Do not treat my desire to build something as authorization to modify the project. Do not begin implementation during onboarding. Preserve existing valid work if this is an established project.

When onboarding is complete, explain what Floppy learned, what roadmap it created, what the first proposed work section is, what requires my approval, and exactly what I should do next.

From that point forward, use the Floppy Project Interaction System as the governing project-control and continuity system for this project.
```

For the complete first-time setup, the three supported starting conditions, initialization commands, and the shorter prompt for future conversations, read [`docs/User-Guide.md`](docs/User-Guide.md). The canonical model-facing role instructions remain in [`BOOTSTRAP.md`](BOOTSTRAP.md).

## About the system

Read [`ABOUT.md`](ABOUT.md) for the conceptual overview: why the system was created, the problem it solves, how the AI and repositories interact, the definition of a **BCE — Bootable Context Environment**, and how the method is applied to projects.

## Core model

- **Source repository:** defines the method, canonical controllers, templates, bootstrap instructions, and initialization tooling.
- **Floppy 1E onboarding controller:** helps the user and model define the project outcome, inspect the starting state, build an evidence-driven section roadmap, and prepare the first inactive work package. It never authorizes implementation.
- **Floppy Z coordinator:** reads the canonical source plus a project's accepted Floppies and tells the administrator exactly what to send to the active project model. It does not perform project writes by default.
- **Project repository:** contains the project code plus its own `.floppy/` control directory and roadmap records.
- **New conversation:** reads a small manifest first, then loads only the controls and project records required for the current lifecycle state.
- **Closeout:** creates a small revision packet, accepted-section record, and inactive next-section draft; it does not regenerate every Floppy.

## Project Floppies and source-system controllers

The five project Floppies remain A–E:

| Floppy | Role | Normal maintenance |
|---|---|---|
| A | Human-in-the-Loop rules | Created and sealed during onboarding; not rewritten during ordinary work |
| B | Development issues | Add or revise individual issue records |
| C | Accepted project baseline | Append only after explicit user acceptance |
| D | Project map and section status | Apply small status, dependency, or roadmap revisions |
| E | Current authorized work section | Revise within the same section; replace only when a new section is authorized |

Two canonical source-system controllers support them:

### Floppy 1E

Floppy 1E is the initial-project definition and roadmap builder. It is loaded only during new-project onboarding or explicit controlled re-onboarding. It produces:

- The project outcome contract
- Verified starting-state classification
- Machine-readable and user-readable roadmap files
- Initial Floppies A–E
- A closed active Floppy E
- An inactive first-section draft

Canonical files:

```text
onboarding/Floppy_1E.md
onboarding/README.md
```

### Floppy Z

Floppy Z is the project-model orchestrator. It reads accepted project state, determines which project model is responsible, and produces the exact instruction the administrator should give that model.

Canonical files:

```text
orchestrator/Floppy_Z.md
orchestrator/README.md
```

Neither Floppy 1E nor Floppy Z is a sixth project-state Floppy. Load them read-only from a pinned source version or commit. Do not alter them per project or store project-specific data in this source repository.

## Repository layout

```text
ABOUT.md                         Conceptual overview and BCE architecture
BOOTSTRAP.md                     Startup instructions for onboarding, coordinator, and direct project modes
system-manifest.json             Machine-readable source map and controller digests
onboarding/                      Canonical Floppy 1E and onboarding replication instructions
orchestrator/                    Canonical Floppy Z and coordination instructions
protocols/                       Canonical operating rules
project-seed/.floppy/            Files copied into an adopting project
project-seed/.floppy/roadmap/    Initial roadmap JSON and Markdown templates
schemas/                         Human-readable field requirements
tools/                           Initialization and validation scripts
docs/                            User and design documentation
legacy/prototype-v0/             Original supplied prototype, preserved unchanged
tests/                           Standard-library tests for the tooling
```

## Initialize a project

Run a dry run first:

```bash
python tools/initialize_project.py --target /path/to/project --project-name "Project Name" --dry-run
```

Then initialize:

```bash
python tools/initialize_project.py --target /path/to/project --project-name "Project Name"
```

The initializer creates only `/path/to/project/.floppy`. It refuses to overwrite an existing `.floppy` directory unless the user deliberately chooses a separate migration process.

## Build the initial roadmap

After initialization, load canonical `onboarding/Floppy_1E.md` and follow `protocols/01-new-project-onboarding.md`.

Floppy 1E guides the user and model through:

1. Evidence inspection
2. Project definition
3. Scope and constraint boundaries
4. Section decomposition
5. Dependency ordering
6. Acceptance-evidence design
7. Roadmap review and explicit acceptance
8. Project-owned Floppy creation
9. First inactive work-package creation

Roadmap acceptance does not authorize implementation. The first section begins only after the user separately authorizes it through project Floppy E.

## Start a coordinator conversation

Use the coordinator instruction in `BOOTSTRAP.md`. The coordinator loads `orchestrator/Floppy_Z.md` from this source repository, treats this repository as read-only, reads the adopting project's manifest and Floppies, and tells the administrator exactly what to send to the active project model.

The coordinator does not modify either repository unless the administrator gives a separate, explicit, named execution override.

## Start a direct project-model conversation

Use the direct-project instruction in `BOOTSTRAP.md`. The project model reads the project manifest, produces a readiness report, and waits for explicit authorization from Floppy E.

## Close a session

Use `protocols/04-everyday-closeout.md`. The ordinary output is a revision packet under `.floppy/revisions/` plus a compact handoff under `.floppy/handoffs/`. Unchanged Floppies are not recreated.

Every accepted section closeout should create the next section's work package as an inactive draft. It must not authorize the next section automatically.

When Floppy Z is coordinating, it prepares the closeout directive for the active project model. It does not perform the closeout writes itself by default.

## FS-01 formal lifecycle specification

FS-01 defines the system's formal lifecycle vocabulary and explicit transition
boundaries:

```text
specs/lifecycle-state-model.md
specs/lifecycle-transition-table.json
```

The model keeps roadmap, work-package, authority, implementation, verification,
acceptance, closeout, migration, and final-closure state separate. A decision or
status in one dimension does not silently change another dimension.

In particular:

- Roadmap acceptance does not authorize a section.
- Work-package acceptance does not authorize implementation.
- Draft creation does not activate a section.
- Implementation completion does not complete verification or create
  administrator acceptance.
- Verification completion does not create administrator acceptance.
- Section acceptance does not apply closeout.
- Section closeout does not authorize the next section.
- Migration planning does not authorize or apply migration.
- A final-closure proposal does not finally close the project.

At most one implementation section may be active. Active implementation requires
exact section authority tied to its section, checkpoint, branch, worktree, file
scope, validation, commit sequence, push boundary, and forbidden side effects.

FS-01 also supplies three candidate schemas under `schemas/drafts/`. They are
marked `draft_non_normative`, identify FS-02 as the future normative section, and
set `production_enforcement` to `false`. They are review artifacts only.

The transition table is declarative data. It cannot execute a transition, write
lifecycle state, apply a migration, authorize a section, or implement controlled
write commands. Those capabilities require separately authorized later sections.

## Source-repository boundary

This repository may change only when the Floppy system itself is deliberately developed. It is read-only during normal use of an adopting project. Canonical Floppy 1E and Floppy Z must not be edited for an individual project. See `protocols/00-source-repository-policy.md`, `onboarding/README.md`, and `orchestrator/README.md`.

## Version and integrity

Canonical source-system controllers must be pinned to a source version, tag, or commit. `system-manifest.json` records their paths and expected SHA-256 digests. A mismatch is a stop condition, not permission to silently use an altered copy.

## Licensing

Floppy Project Interaction System version 2.0.0 is licensed under the Apache License, Version 2.0 (`Apache-2.0`). The license permits use, modification, and redistribution, including commercial use, subject to its terms, and includes an explicit patent license from contributors for applicable patent claims.

The complete license text is included below so it is carried in the validated source/boot package without adding a new package-profile path.

<details>
<summary>Apache License 2.0</summary>

```text
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works, alongside or as an addendum to
          the NOTICE text from the Work, provided that such additional
          attribution notices cannot be construed as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with the
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```

</details>

## Deterministic project control-state provisioning

FS-11 provisions the initial project control state as one bounded operation. The
initializer stages the complete project-owned `.floppy/` tree, writes canonical
UTF-8/LF JSON for the manifest, lifecycle state, and orchestrator registry,
validates the staged records, and then installs the directory atomically. If any
step fails, the staged tree and any newly installed destination are removed.
An existing `.floppy/` directory is never overwritten.

The initial lifecycle state is `LC-ONBOARDING-REQUIRED`. It records no active
section, no work authorization, and no repository writer. Git repository,
branch, worktree, and checkpoint identity are captured when available; a
non-Git directory receives an explicit local repository identity and null branch
and checkpoint values.

Use the source CLI entrypoint:

```bash
python tools/floppyctl.py initialize \
  --target /path/to/project \
  --project-name "Project Name" \
  --source-repository owner/floppy-source
```

Add `--dry-run` to print the exact path plan without writing. The direct
`tools/initialize_project.py` entrypoint remains available for development and
verification. Version 2.0.0 is distributed as a GitHub-hosted source system and
does not require an executable or installer.

## Validated final-project closure

Version `2.0.0` includes bounded final-project closure support in the existing validator and `floppyctl`. It preserves distinct no-migration and migration-applied routes, requires separate proposal and application operations, validates the canonical proposal digest before application, and rejects active authority, partial path sets, cross-route application, and history deletion. Final closure remains unavailable until every required section is closed.

<!-- V2_02_USER_ONBOARDING_BEGIN -->
## Start here — provider-independent onboarding

New users begin at `docs/getting-started/README.md`. It contains the one canonical universal starter prompt and routes actual session capability evidence into Class A/B/C plus Route A/B/C. Provider guides describe transport only. User onboarding does not grant implementation authority.

<!-- V2_02_USER_ONBOARDING_END -->

<!-- V2_05_RELEASE_OVERVIEW_BEGIN -->
## Floppy V2.0.0 source content

V2.0.0 adds the Official Project Plan contract, accepted-origin linkage, durable plan history/active aliases, and paired Continuity Overseer / Project Orchestrator bootstrap while preserving V1 lifecycle schemas and explicit authority boundaries. The source manifest status `stable-release` means only that intended V2.0.0 source content is final; verification, administrator acceptance, clean-main integration, tag, and public release remain separate operations.
<!-- V2_05_RELEASE_OVERVIEW_END -->
