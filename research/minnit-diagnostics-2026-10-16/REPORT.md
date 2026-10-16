# Minnit missing-gap implementation · 2026-10-16 · v0.4.0

## Identity and scope

- Request: fill the missing implementation gaps, following the delivered v0.3 registry/onboarding baseline.
- Baseline: `ca8833b` on `arena/d73f03f8-bigfih765`; existing v0.1–v0.3 backups preserved.
- Scope selected/announced: one authorized Minnit room/channel; protected webhook intake, persistent replay protection, guarded outbound transport and durable outcome ledger.
- Status: **OFFLINE_VALIDATED — implementation delivered; live staging blocked.** Not COMPLETE_FOR_LIVE_SCOPE.
- Non-goals: general-purpose replies, automatic conversation progression, promotion, random-stranger automation, account/cookie reuse, bot restriction bypass, campaign/lead/Snap acquisition, multi-process operation or 100 live connectors.
- Runtime: Python 3.9+ standard library. Optional Node 18+/jsdom only for tests. No upstream source imported.

## Primary evidence refreshed

Fetched official documentation on 2026-10-16:

1. https://docs.minnit.chat/chat-settings/webhooks/ — chat_message/data[] with msg_id, stable chat_id, chat_name, channel, user_id, message, edited, UNIX timestamp; Community+; provider batches events, including across rooms when URLs are shared. No signature format is established by the inspected page. Only register this diagnostic URL for the bound room; mixed-room batches deliberately fail closed.
2. https://docs.minnit.chat/organizations/api/#sendmessage---send-chat-messages-post — organization endpoint `https://example.minnit.org/page/api`, form body action=sendmessage/chatname/username/message/optional channel and X-Key. Message maximum 10,000 characters; example response `{"success":true,"response":"Message sent"}`. This closes the previous documentation-only unknown about the example ACK schema/length, **not live routing/delivery**. Our response is a much shorter fixed disclosed test reply.

Webhook numeric channel example versus name-like description is still ambiguous. `MINNIT_WEBHOOK_CHANNEL` and `MINNIT_SEND_CHANNEL` are separate explicit values; no inferred conversion/default-channel routing is used.

## Implementation and system flow

`app.py` -> `minnit.py` -> shared Controller lock/SQLite -> operator action -> pinned HTTPS transport -> sanitized ledger.

1. Environment-only configuration binds exactly one existing Minnit instance plus provider room ID/name, incoming channel, outgoing channel and owned bot username. Explicit enablement, authorization assertion and independent strong operator/webhook secrets are required. Ownership is operator-asserted, not independently authenticated by environment presence.
2. Operator arms a 15-minute diagnostic window. Disabled/default launch cannot send. The fleet Start path remains simulator-only; the registry now identifies Minnit's separate `diagnostic_connector` phase instead of claiming no implementation exists.
3. Dedicated `/hooks/minnit/{secret}` validates the independent URL secret before reading JSON. It rejects browser-origin requests. This is shared-secret possession, **not a vendor signature or proof of event provenance**. Existing operator APIs retain Bearer and same-origin guards.
4. Body cap 16 KiB and local batch cap 100. Validate complete batch scope first; room ID/name and incoming channel must all match. Only unedited `!orbit ping`, no older than 300 seconds or more than 30 seconds in the future, is eligible. Other interactions never trigger a send. Timestamp checks are local replay/eligibility safeguards, not vendor-signed timestamps.
5. Hash organization/room/channel/message ID; insert a unique durable pending intent. `BEGIN IMMEDIATE` serializes DB decisions. No transcript, user identity, IP, profile, attachment, key, URL secret or response body is persisted. Existing event keys survive Stop, rearm and restart.
6. Operator explicitly approves one pending item with the current run ID. The server accepts **only** run_id, no arbitrary reply text. Check age, run, state, binding and durable 30-second local cooldown. Commit `submitting` intent before network dispatch, preventing automatic retry even after interruption.
7. HTTPS POST to the pinned documented organization endpoint. X-Key header; form body contains only configured routing/username plus fixed `[Orbit diagnostic bot] pong - requested test only.`. No query secrets, arbitrary hosts/ports/userinfo/paths, inherited proxy configuration, redirects or automatic retries. Five-second socket-I/O timeout and 4 KiB response limit; not a strict wall-clock deadline.
8. HTTP 200 + boolean success:true -> `api_accepted`; explicit success:false or 4xx -> `rejected`; unrecognized/redirect/5xx/reset/timeout -> `unknown`. All remain `peer_delivery:unverified`, `safe_to_blind_retry:false`. Never expose provider body/error text.
9. Disarm/Stop all/bound Stop/Delete invalidate the run and cancel pending work. Stop takes the same lock as dispatch: an existing attempt completes first, then no new send can begin until rearmed. A submitted message cannot be recalled. Restart is disarmed; pending becomes cancelled and interrupted submitting becomes unknown.
10. Latest 50 outcomes appear in the dashboard. Cap 10,000 durable records; fail closed rather than evicting replay protection. Private runtime backup/rotation instructions are in README; runtime data stays outside Git/ZIP.

## Gaps closed versus still external

| Gap | Result/evidence |
| --- | --- |
| No real HTTP intake route | Dedicated secret-protected route implemented; actual local HTTP tests |
| Volatile dedup | SQLite unique hashed identity; replay across Controller/database reopen tested |
| No guarded sender | Actual HTTPS/form/header transport implemented; network layer mocked in tests; never live invoked |
| Pre-send state advance / ambiguous resend | Durable submitting-before-network intent, unknown on crash/timeout, no retries |
| No durable outcome ledger | Persisted timestamps/state/HTTP code, sanitized dashboard view |
| Stale queued work / Stop race | Run/age/window checks, serialized Stop, bound Stop/Delete and global stop cancellation tests |
| Missing diagnostic operator controls | Separate view, arm/disarm/confirmation, one-shot approval and outcome UI |
| Exact documented Minnit API ACK/limit unknown | Official sendmessage section inspected; exact success boolean and 10k-character doc limit recorded |
| Live entitlement/credentials | **Still blocked** — none configured, no purchase or account access used |
| Provider callback/auth/channel/retry compatibility | **Still blocked** — no live webhook, no signature mechanism assumed |
| Public HTTPS + provider egress | **Still blocked** — sandbox outbound allowlist does not include Minnit organization endpoints; deploy on approved infrastructure, no bypass |
| Consenting recipient sees reply / production Stop behavior | **Still blocked** — zero third-party chat requests/messages in this delivery |

## Executed acceptance checks

`python -B control-plane/tools/run_checks.py --ui`:

- **87 Python tests PASS**: existing 60 plus 27 diagnostic/transport/HTTP regressions.
- **20 DOM checks PASS**: 18 using the authenticated local server and two explicitly injected-response UI checks for armed approval/disarm. Not a real rendered-browser test.
- JavaScript syntax PASS. Source-bound passing receipt at `control-plane/data/test_results.json`.

New cases cover configuration refusal/endpoint pinning/header injection, webhook independent auth before parsing, browser-origin refusal, malformed/oversized/type rejection, atomic scope errors, timestamp/edit/noncommand handling, persistent restart/replay/crash state, concurrent duplicate intake and approval, durable cooldown, age/run/arm expiration, intent-before-network, ledger capacity refusal, exact form/header/fixed reply, redirect refusal/bounded response, timeout/HTTP result classification, raw secret redaction, operator-only APIs, arbitrary-message refusal, Stop all/bound Stop/Delete, and in-flight Stop serialization.

The tests use synthetic values and a fake provider transport/opener. No real provider transport success is inferred from these checks. A failed initial fixture used an empty API URL; fixed to a pinned synthetic organization URL. A test assertion inside the exception-redacting transport seam was moved outside it so failures cannot be swallowed as an unknown outcome.

Release checks: build explicit-allowlist archive with manifest/CRC, clean-extract tests, verify every manifest hash, and identical standalone rebuild. Exact ZIP SHA-256 is in `artifacts/orbit-control-plane-v0.4.0.zip.sha256` (kept separate to avoid self-referential hashes).

## Remaining engineering / handoff

Read `control-plane/README.md` for all server-only environment keys, launch/setup, controlled staging, API paths, private DB backup and safe rotation. No credential values should be supplied in chat. Minnit remains **8/12 evidence gates**, not 100% or a success probability: implementation work does not fabricate the four missing live evidence gates. Other platform contracts remain at their prior evidence levels; no unknown protocols were invented.

Single operator/process only. stdlib HTTP server is not a production edge; add hardened HTTPS termination, secret-aware proxy logging, operational auth/rate controls, hard wall-clock transport cancellation, load tests and retention management before broader deployment. A slow/trickling response can delay Stop beyond the per-I/O timeout; Stop prevents new dispatch after returning, not recall of a message already sent. Do not run parallel application processes over the same DB. DB loss/rollback/manual deletion is not exactly-once delivery. No scheduler autonomously researches, pushes, runs campaigns or completes future work.
