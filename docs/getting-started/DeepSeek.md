# DeepSeek transport guide

Provider-specific instructions describe transport only. Never infer CLASS A/B/C, Floppy authority, or repository-writer status from the provider brand. Use the canonical starter prompt in `docs/getting-started/README.md` exactly once rather than maintaining a provider-specific copy.

## Use with DeepSeek

1. Determine the tools actually attached to the current DeepSeek session.
2. Treat code reasoning as distinct from repository read, repository write, command execution, and artifact transfer.
3. Paste the canonical starter prompt from `docs/getting-started/README.md` and provide the project description or evidence.
4. If no repository read is available, use Class C manual/file/evidence exchange. Do not claim direct repository state that has not been supplied or read.

Product UI wording is non-normative; the capability vector controls transport selection.

<!-- V2_05_PROVIDER_FRESHNESS_BEGIN -->
## V2-05 provider-documentation freshness

This guide remains subordinate to the canonical capability-vector classifier: provider brand never selects Class A/B/C and never grants Floppy authority.

D1 is a verification-time freshness check, not a P1 source-finalization claim. Before V2-05 verification completion, record the provider, official documentation reviewed where practical, review date, material repository/tool/artifact facts, result, and resulting capability-class guidance. D2 repeats the material-fact check after clean-main integration and before tag/publication. A material stale fact requires `PROVIDER_DOCUMENTATION_REFRESH_REQUIRED`; do not tag or release until separately corrected and revalidated.
<!-- V2_05_PROVIDER_FRESHNESS_END -->
