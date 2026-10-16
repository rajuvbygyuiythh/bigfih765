# Minnit diagnostic gap closure · v0.4.0 · 2026-10-16

**Status: OFFLINE_VALIDATED; authorized live staging pending.** This release implements the previously missing receiver/sender/durable-state slice, not just another site list. No third-party request/message was sent.

## Delivered

- Opt-in single-authorized-room/channel Minnit diagnostic service, server-environment-only credentials and strict documented organization endpoint pinning.
- Dedicated shared-URL-secret webhook, checked before body parsing; not a provider signature. Strict room/name/channel, body/batch/age/run/window validation; edits/noncommands never produce replies.
- SQLite durable unique hashed event identities, pending/submitting/outcome ledger, intent commit before network and persistent cooldown. No transcripts/IPs/profiles/keys/raw response storage.
- Operator approval required for every fixed disclosed pong to a fresh `!orbit ping`; no arbitrary messages, campaign flow or automatic retries.
- Real HTTPS/form/X-Key transport implementation; redirects/proxy inheritance refused, bounded response and socket timeout; accepted/rejected/unknown kept distinct from peer delivery.
- Restart disarm/crash recovery, stale-work invalidation, Stop all/bound Stop/Delete integration and in-flight dispatch serialization.
- Separate dashboard controls/confirmation and sanitized latest-50 ledger; fleet Start remains synthetic-only. Twelve-site registry and four offline inspectors retained.
- Exact official Minnit sendmessage example ACK/10,000-character limit recorded; local safety limits remain independently labeled.
- Reproducible allowlisted source/test/evidence ZIP, manifest and old backups preserved.

## Verification

`python -B tools/run_checks.py --ui`: **87 Python tests + 20 DOM checks PASS**, JS syntax PASS. Of the DOM checks, 18 use local HTTP and two use explicit synthetic injected responses for enabled diagnostic UI states. Python covers the complete local HTTP intake/approval pipeline with a fake provider; transport request/response behavior is mocked. No real browser render or vendor-delivery test. Receipt is bound to current source and catalog.

Release verification includes CRC/manifest checks, tests in a clean extracted copy and a byte-identical rebuild using the packaged helper. Current SHA-256 is in the release sidecar. Full methodology and limitations: `reports/MINNIT_DIAGNOSTICS.md` in the ZIP or `research/minnit-diagnostics-2026-10-16/REPORT.md` in the repository.

## Still required

Authorized room/account/paid-plan entitlement, approved publicly reachable HTTPS deployment with provider egress, live callback/secret/channel/ACK compatibility and consenting witness delivery/Stop evidence. This sandbox's outbound allowlist excludes Minnit organization endpoints. No credential or access value is requested in chat. The four live evidence gates remain pending, so the narrow scope remains 8/12 checklist gates, not a performance percentage.

Single operator/process, development HTTP server; no production edge/RBAC/distributed workers, hard wall-clock network cancellation, exactly-once recipient guarantee or acquisition engine. Stop waits for the current attempt; five-second timeout is per I/O, so slow/trickling responses may delay it. Runtime DB backups must stay private and outside release/Git. Setup and controlled staging: `README.md`.
