# Supported-contract milestone · v0.2.0 · 2026-10-16

**Status: OFFLINE_VALIDATED.** Original implementation of local contract inspection and source-backed research progress; live platform automation is not complete.

## Delivered

- Existing fleet/configuration/synthetic lifecycle controls retained.
- Minnit documented message-batch normalization, edits separated, room/identity/bounds validation, secret-free send specification.
- DeadSimpleChat documented action-button normalization (bot question is not user text), send specification and API-accepted/rejected/unknown classification.
- Versioned two-site research catalog and all 12 checklist gates per site.
- Source-bound test receipts; missing/stale/failed evidence reopens test gates.
- Dashboard research view, citations, findings, pending checklist and editable synthetic contract workbench.
- Git-backed source review of the provided multiplechat snapshot: 740 file entries inventoried, 26 Python files syntax-parsed, detailed selected method review in seven files. No claim to have read every non-source capture/profile file.

## Actual checks

`python -B tools/run_checks.py --ui` from this directory:

- **43 Python core/HTTP/contract/research tests passed**.
- **12 jsdom + real local HTTP checks passed**; not real-browser rendering or third-party delivery.
- JavaScript syntax passed.

Tests include room isolation, repeated-text/different-ID preservation, malformed/oversized payloads, sensitive-extra filtering, edit/action semantics, stale/failing receipts, API auth/origin checks and zero-network contract inspection. Existing worker isolation, restart behavior, bounded diagnostics and concurrent synthetic dedup checks remain covered.

## Progress interpretation

Each selected scope has 6/6 documentation/design review gates. A fresh successful receipt completes two regression gates: **8/12 = 67% checklist completion**. Four live gates remain pending: provider-compatible inbound verification, authorized access/entitlement, implemented real adapter + staging, and two-party visible delivery/stop acceptance. These are not estimates of effort, success probability or whole-site coverage.

Minnit acknowledgement/rate/message details and channel representation remain deployment questions. DeadSimpleChat ordinary-message schemas, action occurrence identity and the example's extra auth header remain questions. No provider behavior is fabricated to close those gates.

## Packaging / handoff

See `README.md`. Source ZIP v0.2.0 includes the application, tests, evidence catalog/receipt and authored reports/inventory. Runtime DB, dependency directories, raw source ZIPs, browser profiles, actual transcripts and secrets are excluded. Older ZIPs are preserved unchanged. Packaging validates CRC, deterministic bytes, extracted-file matching and extracted-copy tests/receipt freshness.
