# ChatGPT transport guide

Provider-specific instructions describe transport only. Never infer CLASS A/B/C, Floppy authority, or repository-writer status from the provider brand. Use the canonical starter prompt in `docs/getting-started/README.md` exactly once rather than maintaining a provider-specific copy.

## Use with ChatGPT

1. Open the ChatGPT conversation you want to use for the project.
2. If the session exposes a connected GitHub/repository capability, determine what it can actually do in this session. A visible or connected repository is evidence for read only when repository content can actually be read; direct write is true only when an actual repository mutation capability is technically available.
3. Record `command_execution` and `artifact_transfer` separately. Do not infer either from GitHub access.
4. Paste the canonical universal starter prompt from `docs/getting-started/README.md` and describe the project naturally.
5. If the result is CLASS B, ChatGPT may inspect the repository directly but repository mutations remain administrator-applied. If CLASS C, exchange files/evidence manually. CLASS A still requires separate Floppy authorization before any write.

ChatGPT UI names, connector labels, and plan availability are non-normative. The observed capability vector is what matters.
