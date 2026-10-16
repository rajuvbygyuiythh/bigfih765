# Remaining-site onboarding · v0.3.0 · 2026-10-16

**Status: OFFLINE_VALIDATED.** Registry/onboarding and local documented-subset work delivered, not twelve working live bots.

## Delivered

- Shared capability registry: 12 research/reference records, eight configurable site types, plus the separate synthetic sandbox.
- All original shortlist alternatives now appear in Site research. Chitchat/Joingy/Isexychat are reference-only; Chatzy is restricted. UI and direct API reject their configuration creation.
- Search/phase filters and site-specific Add configuration. Slots are inactive; unsupported starts fail closed.
- Repeatable seed utility creates only missing inactive site types, preserves existing configurations and starts no worker.
- RumbleTalk local REST-history inspector and secret-free SYSTEM-message specification; UTF-8 byte limit enforced. No webhook/private-DM equivalence claimed.
- Chatwee local SSO-result inspector redacts the SID and never treats it as a user message. Chat send remains unsupported.
- Per-platform proof coverage prevents unknown/unimplemented sites from inheriting test-gate completion. Reference/restricted entries show N/A.
- Reproducible allowlisted source/evidence packager and SHA-256 manifest; old ZIPs preserved.

## Executed regression scope

`python -B tools/run_checks.py --ui`:

- **60 Python core/HTTP/contract/catalog/bootstrap tests**.
- **17 jsdom + actual local HTTP checks** (not rendered-browser or third-party tests).
- JavaScript syntax check.

Coverage includes both new shapes, multibyte message boundaries, session redaction, missing/invalid schemas, unknown-site refusal, specific-platform proof, inactive-config persistence, seed idempotency, restricted API rejection, registry-derived dropdowns, research filters and card-to-configuration flow. Final PASS/FAIL and timestamp are written by the actual test runner to `data/test_results.json`, bound to current source. Packaging also runs extracted-copy checks, manifest/CRC/byte matching and deterministic rebuild validation.

## Progress / remaining work

Four narrow local scopes: 8/12 checklist gates with fresh proof. Chatblink: 1/12; StrangerMeetup/Chatango/Chatiw: 2/12. These are documented review/planning/test milestones, not performance/success/effort estimates. Chatzy and references: N/A.

All real connectors remain unimplemented/unconfigured. Appropriate supported contracts, authorization/entitlement, actual adapter implementation/staging and consenting peer-delivery/stop evidence are still required. No credentials, remote messages, acquisition traffic, campaign engine or autonomous scheduler used.

## Handoff

Run instructions: `README.md`. Full per-site next steps: `reports/SITE_ONBOARDING.md` in the release, or `research/site-onboarding-2026-10-16/REPORT.md` in the repository. The original upstream review and two-site analysis are historical snapshots, not rewritten claims that every source/runtime operation has been tested.
