# Evidence-first engineering operating standard

Owner preference recorded: 2026-10-15 UTC. Apply alongside the confirmed one-site delivery workflow in `../knowledge-pack/docs/DAILY_SITE_DELIVERY.md`.

## 1. Purpose and capability boundary

The owner wants stronger planning, targeted site analysis, networking diagnostics, accuracy, memory and testing. Implement that preference as a disciplined engineering process, not a claim of self-modification.

An agent cannot promise to upgrade its underlying model, acquire unrestricted tools, install arbitrary skills, maintain perfect memory, work autonomously every day or guarantee success on every target. This document does not install a plugin, create a capture service or implement a new site integration. Use only tools actually available and authorized in the active session; verify missing capabilities before depending on them.

## 2. Target and scope first

For each cycle, record:

- One confirmed platform/URL and the owner-approved user journey.
- Required features, explicit non-goals and acceptance tests.
- Supported/permitted integration, access constraints and test participants.
- Baseline source snapshot, dependency/runtime requirements and evidence gaps.
- The smallest complete scope and the conditions that would block delivery.

“Understand all site data” means understand the relevant integration lifecycle, not collect unrelated users' data or copy an entire service. No next target is selected by this document.

## 3. Evidence ledger and uncertainty

Every important technical claim should have a record:

```text
claim:
classification: owner_requirement | observed | inferred | tested | unknown
source_url_or_path:
snapshot_or_timestamp:
observation_or_command:
actual_result:
limits_or_counterevidence:
next_check:
```

These labels are not mutually exclusive: a tested observation can still have limited scope. Search snippets, README claims and API permission metadata are leads, not substitutes for primary text, license files or actual operations. Do not invent confidence percentages. Recheck stale assumptions and resolve conflicting evidence explicitly.

## 4. Network investigation, when available and permitted

Before claiming realtime capture, confirm that the session has a browser/CDP/proxy or supplied sanitized trace, permission for the investigation, and synthetic/consented participants. If absent, report the limitation; public-page research is not a live network capture.

For the relevant flow, inspect:

1. Actual transport: HTTP polling, raw WebSocket, Socket.IO and WebRTC are not interchangeable.
2. Session establishment, scope and authorization expiry, without publishing credential values.
3. Match/conversation identity, event schemas, message IDs and sender attribution.
4. ACK behavior, failed versus unknown delivery and ordering guarantees.
5. Disconnect/reconnect, conversation rotation, late messages and cleanup.
6. Rate limits, documented retry guidance and safe stop conditions.

Keep raw sensitive traces out of Git and deliverable ZIPs. Derive minimal redacted schema fixtures. Do not add token harvesting, CAPTCHA bypass, evasion, bulk unsolicited messaging or unauthorized probing. Network visibility is not itself permission to automate a service.

## 5. Reusable architecture and practical tool choice

Keep site adapters separate from reply decisions, conversation state, delivery tracking, persistence and diagnostics. Reuse an implementation only after inspecting its actual source/license and regression behavior. The knowledge pack is documentation, not a ready-made engine.

Choose the simplest adequate toolchain for the target. Add a dependency or external integration only when it solves a demonstrated gap; review its license, version, permissions, resource cost and failure behavior. Never install dependencies as an import side effect or assume a connector is available without checking it.

Useful reusable “skills” are repository artifacts: tested fixtures, adapter contracts, troubleshooting notes, explicit setup scripts and regression cases. They are not new model abilities or automatically installed plugins.

## 6. Separate design, implementation and review passes

These are workflow passes, not a claim that extra agents/models were spawned:

- **Design:** identify contracts, failure modes, boundaries and acceptance cases.
- **Implementation:** make the smallest coherent change and keep side effects explicit.
- **Review:** challenge assumptions, inspect the diff, exercise failures and compare results to acceptance criteria.

Parallelize independent research/checks only when tools support it. Do not run competing mutations of shared state. Prefer one reliable single-worker path before adding concurrency.

## 7. Test/fix loop with real outcomes

```text
reproduce -> isolate root cause -> minimal fix -> regression test
 -> required suite/build -> authorized integration, when required
 -> clean/extracted package smoke check -> evidence-backed handoff
```

Applicable cases include duplicate events, legitimate repeated text, missing bot DOM messages, stale queued replies, state reset, late ACK, unknown delivery, reconnect, expired authorization, refusal/exit, privacy redaction and completed shutdown.

Do not repeatedly rerun the same failed operation without a changed hypothesis or condition. Capture the actual blocker and next check. Offline validation must remain distinct from live integration validation. No generic self-test guarantees all future platform behavior.

## 8. Durable memory, not perfect memory

Keep confirmed requirements in `PROJECT_MEMORY.md` and `knowledge-pack/GOALS.md`; per-site decisions, adapter versions, fixtures, failures and test results belong with the corresponding implementation. Record changed decisions and their reasons, not just the latest conclusion.

At a new session, reread the relevant files and current source. Do not assume personal memory persists. Minimize stored conversation content and never use Git as a secret store. New discoveries should improve a reproducible artifact or regression test, not merely produce a claim that the agent “learned permanently.”

## 9. Delivery standard and stop conditions

Deliver source, setup/run instructions, example configuration, tests/results, fixed defects, remaining limitations and packaging evidence. Use `../knowledge-pack/templates/SITE_DELIVERY_REPORT.md`.

Daily one-site delivery is the owner's cadence target. It does not remove permission, scope or quality gates. Report BLOCKED or OFFLINE_VALIDATED when appropriate, rather than redefining incomplete work as COMPLETE_FOR_SCOPE. Work occurs during active sessions unless an actual scheduling system is explicitly implemented and configured.

## 10. Current state

- This operating standard is documentation only.
- No new model/tool/plugin/LLM service or automated skill installer was added.
- No realtime site traffic was captured in this update.
- No next site has been selected or implemented.
- Begin the next build by confirming one target, essential scope and permitted access; then execute the existing daily-delivery workflow.
