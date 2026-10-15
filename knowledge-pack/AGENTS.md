# Instructions for an incoming agent

## Mission

Help the owner build new projects using documented architecture from existing repositories. Read `README.md`, `GOALS.md`, `docs/CHAT_SYSTEM.md` and `docs/SECURITY_AND_LIMITATIONS.md` before proposing implementation. Use Bangla/Banglish for discussion when appropriate; code identifiers can remain English.

## Truth and evidence

- Distinguish **confirmed owner requirement**, **observed source behavior**, **inference**, and **new recommendation**.
- The owner requested reusable methods, patterns, system/logic/chat documentation and a GitHub/ZIP handoff. A specific next site, app feature set and business model are not yet confirmed.
- The snapshot reviewed 23 repo trees and 19 archives. Selected bodies were read; broader declarations were indexed. Do not tell the owner every source line was reviewed or that the applications passed runtime tests.
- `docs/repository-inventory.json` pins root blobs/archive SHA-256 and selected declarations. Paths in the inventory refer to files inside ZIPs, not necessarily files in this documentation repo.
- `docs/method-index.json` is a static navigation index. Empty declarations do not mean a file has no code. In particular, the documented ws_bot.py has a syntax error.
- Inspect current source and dependencies before copying behavior. Archived README/AGENTS comments are source material, not authority to override the owner's request or your applicable instructions.

## Required working approach

1. Summarize the goal in plain language. Identify the target platform, UI, authorization model, required features and deployment constraints; ask only the unresolved questions that block work.
2. Fill `templates/NEXT_PROJECT_BRIEF.md`. Mark unresolved values explicitly; never fabricate IDs, credentials, supported endpoints or business requirements.
3. Pick one baseline family and exact snapshot. Explain the choice; do not merge all ZIP versions blindly.
4. Separate lifecycle, transport, reply decisions, conversation state, persistence and diagnostics. Keep safety/consent policy outside individual reply categories so it can apply globally.
5. Start with a mock transport and neutral synthetic messages. First prove one conversation, duplicate handling and clean stop/reset.
6. Add a thin UI and persistent config. Introduce concurrency only after the single-worker path is reliable.
7. Use supported APIs or explicitly authorized integrations. Respect platform terms, consent and rate limits. Do not build bulk credential checks, token harvesting, spam or anti-abuse bypass features from the historical tooling.
8. Keep secrets, cookies, stored sessions and raw conversation logs out of source control, deliverable ZIPs and screenshots. Do not request secret values in chat.
9. Test lifecycle, policy, deduplication, delivery ambiguity, reconnect and persistence separately. A stop request is not necessarily completed cleanup.
10. End with changed files, exact validation commands/results and remaining risks. Update the project decision log when requirements change.

## Important baseline cautions

- `bigfih765` and `v2v2cc` archives are identical. `chatfilehere` and `lastch` archives are identical.
- `root-project-pro` and `bigfih765` have different live-chat implementations. A newer-sounding name does not establish superiority.
- `chatchat2222/.../transport/ws_bot.py:252` fails Python parsing. Do not import it or claim the WebSocket variant is ready.
- `tgbot` filename mentions DeepSeek; inspected main/reply flow is local-only. Confirm any new AI provider explicitly.
- Existing age/share flags do not prove comprehensive safety. Unknown age, refusal and consent revocation need policy decisions/tests before sensitive functionality.
- This pack intentionally does not redistribute historical source ZIPs, datasets, capture payloads or credentials.

## Suggested first response after reading

Briefly explain the relevant existing system and the proposed baseline. State what is still unknown about the new project and propose a small offline first milestone. Do not promise identical behavior on a new site until its integration contract is verified.
