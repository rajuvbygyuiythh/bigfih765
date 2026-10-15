# ZIP re-read and main-goal alignment — 2026-10-15

## Confirmed update from the owner

> daily one site with full project

The owner asked that subsequent thinking, planning, fixes and implementation follow this goal, using the linked knowledge ZIP as the starting context.

Recorded interpretation: target one selected site per day and deliver a complete project for an explicitly agreed scope. Reuse the relevant common chat-system patterns instead of creating unrelated monolithic projects. Research should support implementation, not indefinitely replace it. Daily cadence remains a target, not a guarantee or an autonomous recurring job.

## Input and review evidence

Input: `artifacts/project-build-knowledge-2026-10-15.zip` in the original bigfih765 review repository.

SHA-256: `c4df2f020f0ca4bd98527b911e00c16e269ae48bcc28c6b3cc4b051818ec2e0e`.

ZIP integrity was checked. The narrative documents, agent instructions, goals, chat system, architecture, build gates, limitations, publication/build notes, templates and handoff scripts/tests were re-read. The JSON inventories were parsed for structure, coverage and relevant method locations; **10,046 declaration entries are not 10,046 independently reviewed implementations**.

Input inventory coverage:

- 23 source repository records.
- 19 archive records.
- 916 indexed source-file occurrences across archive versions.
- 10,046 declaration entries, including repeated/versioned source and class entries.

This re-read did not execute historical bots, capture a new site's HTTP/WS traffic, repair the archived ws_bot.py or verify a production integration.

## Core understanding carried forward

1. EVA conversation state and reply decisions can be separated from browser/event transports. Pending replies and reply provenance need explicit handling.
2. Go desktop lifecycle and profile-worker planning are useful patterns, not a drop-in implementation for every platform.
3. API workers, headless socket clients and visible DOM show mode have different lifecycles; matching names do not establish behavioral parity.
4. Deduplication must distinguish duplicate delivery from separate legitimate identical messages.
5. Old queued replies must not leak into a new conversation. Generation, queueing, sending and confirmed/unknown outcomes are different states.
6. Site auth, session expiry, event schema, ACK, matching and reconnect contracts require per-site evidence and tests.
7. Historical intimate/outreach categories, refusal nudges or partial age flags are not automatically approved requirements or a universal policy implementation.
8. Existing source and dependency readiness must be checked; the knowledge pack itself is documentation, not a runnable engine.

## Changes made to preserve the goal

- Updated owner goal, incoming-agent instructions, README and project-memory notes.
- Added `DAILY_SITE_DELIVERY.md` with stage gates, definition of done and status labels.
- Added a one-site delivery-report template and updated the next-project brief/start prompt.
- Added a root `AGENTS.md` to direct future agents to the latest goal.
- Kept the input ZIP unchanged; the refreshed daily-goal pack is a separate ZIP.

## Next step

**Next site: UNSELECTED.** No new site-specific app was started in this clarification turn. Confirm one target and essential scope/access, then use the documented delivery cycle. If a required integration test is blocked, report the blocker instead of calling the site complete.
