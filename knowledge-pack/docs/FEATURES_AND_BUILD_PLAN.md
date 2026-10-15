# Features and next-project build plan

**Latest owner-confirmed working target:** one selected site per day with a complete scoped project. Use [DAILY_SITE_DELIVERY.md](DAILY_SITE_DELIVERY.md) to apply these gates during each delivery cycle; do not substitute research alone or skip validation to meet the cadence.

## 1. Select features; do not assume all are required

| Capability | Historical evidence | Next-build status / caution |
| --- | --- | --- |
| Desktop dashboard | Go Wails; Python GUI | Candidate; choose UI with owner. |
| CLI / offline chat preview | Go CLI; Python run_chat.py | Strong starting point for a mock first milestone. |
| Browser adapter | Rod/ChromeDP or Python browser workers | Only if permitted and needed; target-specific contract required. |
| API / event transport | Go API/realtime; Python headless | Prefer supported APIs; captured protocol is not stable documentation. |
| Local rules/templates | Python and Go EVA; Telegram local engine | Candidate; use neutral reviewed content. |
| Conversation memory | Per-conversation dictionaries/models and Telegram DB | Minimize and define retention. |
| Non-repeating replies | Pool/line tracking | Candidate; test exact repetition and exhaustion. |
| Incoming-event dedup | Python tracker; Go IDs; Telegram dedup | Required when transport can duplicate events. |
| Per-user serialization | Telegram asyncio locks | Useful for state consistency; add bounds/cleanup. |
| Worker start/stop | App lifecycle and ThreadManager | Require completed cleanup, not just a stop request. |
| Multiple browser profiles | Go worker planning; Python scheduler | Optional; start with one authorized worker. |
| Resource supervision | Optional Python EngineBridge/governor | Optional; verify binaries and safe fallback. |
| Settings persistence | Go UI store; Python config paths | Candidate; validate and migrate config schema. |
| Live status / diagnostics | App events and launch logging | Recommended; redact before writing to disk. |
| Capture/protocol debugging | CDP tool families | Dev-only, consented synthetic sessions; not default user analytics. |
| AI/LLM replies | Some historical modules/docs mention AI | New decision required; inspected tgbot active flow is local-only. |
| Image/media messaging | Historical GUI/media components | Optional; needs explicit user consent and policy requirements. |
| Historical outreach/contact funnel | EVA templates/state flags | Not a default requirement; no blind migration. |
| Account credential checking/token harvesting | Reddit historical tooling | Not a feature to port; use supported authorized account management. |

## 2. Preferred dependency direction

```text
UI / CLI -> Application service -> Engine + Transport + Store
                                -> Policy + Observability
```

- UI does not own transport reconnect rules or reply selection.
- Engine does not open browsers, install packages or send messages.
- Transport does not decide product goals or content policy.
- Store does not serialize credentials into ordinary diagnostics.
- Scheduler does not share one mutable conversation across unrelated users.
- Optional accelerators do not silently change product behavior.

This is a recommendation synthesized from historical boundaries, not a claim every old module already follows it.

## 3. Staged implementation gates

### Gate 0 — Goal and authorization

Fill the brief: platform, owner-authorized integration, user interaction model, UI, required feature list, hosting/OS, policy and retention. Outcome: a short confirmed scope and explicit non-goals.

### Gate 1 — Offline core

Implement neutral incoming-message model, per-conversation state, deterministic reply decisions, mock transport and a console preview. Acceptance: a synthetic conversation can start, process a message and stop without a network request.

### Gate 2 — Reliability

Add deduplication, conversation reset, response provenance, pool validation and guarded delivery outcomes. Acceptance: duplicate events never create duplicate decisions; unknown delivery does not blindly resend.

### Gate 3 — Persistence and policy

Add schema-versioned settings/state, bounded history, globally applied consent/content checks and redaction. Acceptance: refusal/exit stops the relevant behavior immediately; sensitive values cannot reach logs or exports.

### Gate 4 — Authorized integration

Implement one adapter for the chosen platform. Confirm API contracts, rate limits, authorization expiry and reconnect handling. Acceptance: only a small explicitly authorized test, with actual result recorded. Do not claim another site's capture proves this adapter works.

### Gate 5 — UI

Bind a thin UI to application operations. Show current worker state, last error, cancellation progress and reply reason without exposing secrets. Acceptance: UI state reflects backend outcomes; not optimistic success on a failed operation.

### Gate 6 — Bounded scaling

Add configured worker limits, per-session serialization, queues with backpressure, timeouts and awaited shutdown. Acceptance: single-worker mode still works; stop leaves no owned child processes or background tasks.

### Gate 7 — Delivery

Pin dependencies; run appropriate unit/contract/build checks; package clean source and example config only. Record commit/hash, exact validation commands, failures and release notes. Never label a package “verified” solely because its filename says so.

## 4. Decision-log template

```text
Date / author:
Decision:
Confirmed requirement or recommendation:
Source reference / snapshot:
Alternatives considered:
Reason / trade-offs:
Validation performed:
Remaining risks:
```

## 5. Definition of done for a new feature

- Owner requirement or explicitly accepted recommendation is traceable.
- One clear implementation boundary and no hidden install/start side effects.
- Tests cover normal, duplicate, failure, cancellation and policy cases.
- Logs/exports contain no secrets or unnecessary personal data.
- Actual validation results are recorded, including what could not run.
- Relevant docs and example configuration are updated.
- Changes to old behavior are intentional and explained, not inherited accidentally.
