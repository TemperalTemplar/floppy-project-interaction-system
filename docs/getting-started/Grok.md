# Grok transport guide

Provider-specific instructions describe transport only. Never infer CLASS A/B/C, Floppy authority, or repository-writer status from the provider brand. Use the canonical starter prompt in `docs/getting-started/README.md` exactly once rather than maintaining a provider-specific copy.

## Use with Grok

1. Start the project conversation and determine whether this specific session can read repositories, write repositories, execute commands, and transfer artifacts.
2. Record those four capabilities as booleans; do not promote a capability because the model can discuss code.
3. Paste the canonical starter prompt from `docs/getting-started/README.md`.
4. Follow Route A, B, or C from evidence. For Class B or C, repository writes remain outside the AI transport and are administrator-applied/manual as appropriate.

Any product UI or integration name is non-normative.

<!-- V2_05_PROVIDER_FRESHNESS_BEGIN -->
## V2-05 provider-documentation freshness

This guide remains subordinate to the canonical capability-vector classifier: provider brand never selects Class A/B/C and never grants Floppy authority.

D1 is a verification-time freshness check, not a P1 source-finalization claim. Before V2-05 verification completion, record the provider, official documentation reviewed where practical, review date, material repository/tool/artifact facts, result, and resulting capability-class guidance. D2 repeats the material-fact check after clean-main integration and before tag/publication. A material stale fact requires `PROVIDER_DOCUMENTATION_REFRESH_REQUIRED`; do not tag or release until separately corrected and revalidated.
<!-- V2_05_PROVIDER_FRESHNESS_END -->
