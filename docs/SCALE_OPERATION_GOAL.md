# Larger operation goal and next build direction

Owner update: 2026-10-15. This records business direction, not a running implementation.

## Root goal

- One dashboard to configure, start/stop and observe 100+ owned or authorized site/integration instances.
- Business ambition: 50,000 daily Snap user acquisitions through opted-in traffic. This is not demonstrated demand, measured capacity, guaranteed conversions or permission for unsolicited promotion.
- Delivery unit remains one complete, scoped integration at a time: assess -> implement -> test -> fix -> package -> handoff.
- Resolve routine gaps independently, use appropriate supported alternatives, summarize material blockers in one line and continue achievable work. Avoid repeated discovery questions and research loops.

## Scope distinction that prevents wasted work

100 sites need not mean 100 reverse-engineered platforms or separate bots. Multiple owned sites/rooms may share one tested platform adapter with isolated configuration. Track three counts separately: supported platform adapters, configured integration instances and concurrently healthy instances.

Existing-stranger-audience automation is not equivalent to owning a chat room. Do not pretend an empty room supplies traffic. Do not implement anti-bot bypass, deceptive identities, unsolicited mass messaging, harvested contact lists or a rule that ignores provider restrictions.

## Recommended next builds

1. **Shared control plane + one Minnit test-room adapter.** Candidate selected for documented incoming webhooks and reply API, contingent on authorized access and required entitlement. Initial scope: one instance, disclosed command-triggered bot, two consenting test participants, visible delivery confirmation and working stop control. No live access configured yet.
2. **Second instance of the same adapter.** Prove tenant/room isolation, separate secrets, start/stop isolation and correct dashboard attribution before adding another platform. This is more useful than duplicating a working adapter into a second codebase.
3. **DeadSimpleChat adapter.** Use the same event/delivery contract; confirm customer API entitlement. Validate whether the common contract really generalizes.
4. **Controlled scaling: 1 -> 5 -> 20 -> 100 configured instances.** Advance only on measured load/resource/failure results. Configured count is not demonstrated simultaneous capacity.
5. **Opt-in acquisition and attribution.** Use owned-site calls to action, user-requested links and approved distribution/advertising. Attribute only events that can actually be observed; clicks and opt-ins are not confirmed Snap acquisitions.

These are recommendations, not user approval for purchases, account registration or deployment. Minnit and DeadSimpleChat do not provide a verified Chitchat-like existing stranger pool. Existing-audience candidates remain a separate operator-approved integration track; do not rank them by bypassability.

## Shared control-plane requirements

- Adapter registry plus isolated instance configuration; secrets stay server-side, outside Git and logs.
- Worker lifecycle: queued/starting/running/degraded/stopping/stopped, heartbeat and explicit failure reason.
- Per-instance work queues, bounded concurrency and backpressure; respect provider limits.
- Stable event IDs, deduplication, bot-self filtering and per-conversation state.
- Delivery ledger: pending/confirmed/failed/unknown. Do not blindly retry unknown deliveries.
- Per-instance and global stop controls, fail-closed behavior and cancellation of stale queued work.
- Dashboard RBAC, audit trail, health/error counters and resource/cost visibility.
- Consent/source records, clear bot disclosure, opt-out/exit handling and minimal data retention.
- Supported inbound authentication/replay protection. Do not promote an unverified webhook to production just because a demo accepts JSON.

Select implementation stack after checking relevant existing root/entrypoint/lifecycle code. The historical knowledge pack is architectural context, not an installed reusable engine. No stack or dependency is mandated by this document.

## Acquisition measurement

Keep source visit, requested-link click, explicit opt-in and independently verifiable acquisition as different funnel events. If the destination does not expose a supported confirmation method, label the final acquisition count unknown; never equate an outbound click with an added friend or account.

The 50k/day target must be evaluated using measured reach, conversion, cost, retention and delivery constraints. Do not manufacture percentages to make a traffic forecast look validated. A dashboard or 100 running instances does not itself create demand.

## Acceptance gates

- Single-instance authorized delivery and stop controls pass before claiming a working adapter.
- Multi-instance isolation passes before adding platforms or increasing concurrency.
- Load tests use synthetic fixtures in owned infrastructure; never generate load against unrelated public services.
- Scale claims include concurrency, duration, latency/errors, resource use and test environment.
- Release includes source, setup, configuration template, actual tests, remaining blockers and ZIP.
- Unavailable access blocks the live test, not useful local control-plane implementation. Label offline and live results separately.

## Current state

The initial goal update recorded direction only. A subsequent first milestone now exists at [`../control-plane/README.md`](../control-plane/README.md): SQLite configuration, central dashboard, isolated synthetic worker lifecycle, optional token protection, bounded activity/deduplication and global stop. Fifteen Python unit/HTTP tests and eight DOM/local-HTTP checks passed. Status: OFFLINE_VALIDATED. No live platform connector, paid plan, acquisition campaign or third-party chat delivery is implemented. The heartbeat scheduler is local synthetic infrastructure, not an autonomous daily project scheduler. Public-source research remains at `../research/chat-platforms-2026-10-15/REPORT.md`. Previous research/knowledge ZIPs remain unchanged.
