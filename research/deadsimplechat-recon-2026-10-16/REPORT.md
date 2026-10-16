# DeadSimpleChat · Step 1 Recon · 2026-10-16

Status: **documentation recon + offline diagnostic implementation; no live staging**.
Scope: one authorized room/bot with consenting diagnostic participants; no join-triggered outreach or bulk promotion. Baseline `c920fba`; next site selected through the restored root SITES queue. No other site was researched this turn.

## Primary sources refreshed

1. https://deadsimplechat.com/support/rest-api/bots/post-send-message-bot — full page read. Business Advanced API; POST `https://api.deadsimplechat.com/consumer/api/v2/bot/:botId/chatroom/:roomId/message?auth=...`; JSON message at most 1000 characters. Private key required in auth query table. Examples also include Authorization header. HTTP 200 + boolean success:true is documented API acceptance only, not recipient-visible delivery.
2. https://deadsimplechat.com/support/bots/quiz-bot-using-action-buttons — both chunks read. The worker example uses query auth with only Content-Type header; extra Authorization requirement therefore unresolved. actionButtonPressed includes user/chatRoom/bot/message/actionButtonPressed; enclosing message is original bot question, not user text. Button definition IDs are not proven unique per click. Example join-triggered automatic messages and public webhook inspection services are **not** adopted.

Observed here: official documentation content. Unknown: actual account entitlement, valid auth combination, webhook authentication/signatures/retries, unique occurrence identity, server timing/rates, browser storage and consenting peer delivery. Documentation cannot close these live gates. No runtime endpoint was probed; this sandbox does not allow provider API egress.

## Code / reproducible recon

```sh
python -B control-plane/tools/recon_site.py deadsimplechat
# Only when an appropriate authorized trace is actually needed:
python -B control-plane/tools/recon_site.py deadsimplechat --har .runtime/authorized.har
python -B control-plane/tools/run_checks.py --ui
```

`recon_deadsimplechat.py` returns a structured single-site contract/evidence summary. Saved output is `data/deadsimplechat_recon.json`; its source hash participates in the receipt, and a regression ensures saved output matches the tool. Optional HAR reader bounds input to 20 MiB / 10k entries / 500 matches and selects only the documented HTTPS POST bot-send route. It never reproduces requests or inspects body/cookie/WebSocket content. It emits a fixed public route template, boolean auth-query/header presence, integer HTTP status, and explicit unverified acceptance/delivery. Other routes are skipped without exporting their URL or names. Query/header values, bot/room IDs, paths, input filenames and parser details are never printed. Raw HAR and `.env.local` stay ignored; do not commit or attach them.

Header presence does not establish requirement or validity. A missing/stripped header does not imply permission to send unauthenticated. Metadata-only HTTP 200 does not establish JSON success:true. Browser HAR usually cannot show backend bot sends or provider-to-backend callbacks; no irrelevant capture was requested. Need a separately redacted consenting server-side fixture for occurrence/authenticity evidence, never API-key/token harvesting or credential sharing.

## Tests / review

Eleven new synthetic tests cover documented-contract gates, saved-output consistency, secret/ID/body/cookie redaction, auth-location metadata, missing auth, lookalike origins, plain HTTP/userinfo/ports/other paths/WS/GET filtering, bad schemas/status/URLs, metadata/entry/match limits, runnable CLI and generic parser/size errors. No live capture is used; no network/send function exists in the recon modules. Executed full regression: **98 Python + 20 DOM checks PASS**, JavaScript syntax PASS. Source-bound receipt retained at `control-plane/data/test_results.json`; two DOM checks use explicit injected responses, not live provider traffic.

Root PROJECT_MEMORY/SITES/SKILLS/PLAN/CHANGELOG support continuation. GOALS content is unchanged; the root path aliases the existing mission. Percent 12.5 = one of eight delivery steps, not the older 67% evidence checklist or an automation success rate. Requested system-output template was not supplied, so PLAN documents a short fallback rather than inventing a system instruction.

## Next boundary

Step 2: implement/test explicit diagnostic contract/safety decisions without enabling transport while auth and occurrence identity are unresolved. Do not automatically treat button IDs as unique clicks or copy Minnit webhook semantics. Access values remain owner-managed in ignored server environment/.env.local (not automatically loaded). Step 8 will create a new versioned ZIP/sha256 with extracted-copy checks; old released artifacts stay untouched now. Git push is this step's backup.
