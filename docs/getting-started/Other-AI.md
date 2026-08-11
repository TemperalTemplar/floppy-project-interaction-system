# Other-AI transport guide

Provider-specific instructions describe transport only. Never infer CLASS A/B/C, Floppy authority, or repository-writer status from the provider brand. Use the canonical starter prompt in `docs/getting-started/README.md` exactly once rather than maintaining a provider-specific copy.

## Use with any other AI

1. Ignore marketing names and first determine the actual four capability booleans for the current session.
2. If repository write is reported without repository read, STOP and resolve the contradiction.
3. Paste the canonical starter prompt from `docs/getting-started/README.md`.
4. Use Class A/B/C and Route A/B/C exactly as the canonical guide defines them.
5. If a capability cannot be demonstrated, record it as unavailable for routing purposes rather than guessing.

A new provider does not require a new Floppy authority model. Provider-specific UI instructions are optional transport notes only.

<!-- V2_05_PROVIDER_FRESHNESS_BEGIN -->
## V2-05 provider-documentation freshness

This guide remains subordinate to the canonical capability-vector classifier: provider brand never selects Class A/B/C and never grants Floppy authority.

D1 is a verification-time freshness check, not a P1 source-finalization claim. Before V2-05 verification completion, record the provider, official documentation reviewed where practical, review date, material repository/tool/artifact facts, result, and resulting capability-class guidance. D2 repeats the material-fact check after clean-main integration and before tag/publication. A material stale fact requires `PROVIDER_DOCUMENTATION_REFRESH_REQUIRED`; do not tag or release until separately corrected and revalidated.
<!-- V2_05_PROVIDER_FRESHNESS_END -->
