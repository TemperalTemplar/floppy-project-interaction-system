# Gemini transport guide

Provider-specific instructions describe transport only. Never infer CLASS A/B/C, Floppy authority, or repository-writer status from the provider brand. Use the canonical starter prompt in `docs/getting-started/README.md` exactly once rather than maintaining a provider-specific copy.

## Use with Gemini

1. Start the Gemini conversation that will carry the project.
2. Inspect the actual repository/file/code tools exposed to that session rather than assuming capabilities from the Gemini product name.
3. Record the four booleans independently and use the canonical starter prompt from `docs/getting-started/README.md`.
4. Preserve existing-project evidence before Route B adoption, and use `.floppy/manifest.json` first for Route C.
5. Repository or command tools never create Floppy authority; all mutations remain bounded by the active Floppy authorization.

Gemini UI wording is transport guidance only and may change independently of the Floppy contract.
