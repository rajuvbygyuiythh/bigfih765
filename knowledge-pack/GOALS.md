# Owner goals and decision boundaries

## A. Confirmed by the owner

The owner asked, in Banglish, to:

- Read the main/root files and method systems across the GitHub projects.
- Retain reusable understanding so similar projects can be built later.
- Put methods, patterns, systems, logic, chat-system explanations and future-use information in a separate GitHub repository.
- Provide one ZIP containing that knowledge.
- Make the handoff clear enough for another agent to understand the building goal and how the existing chat systems work.
- **Latest clarification (2026-10-15): aim for one site per day with a complete, scoped project**, not a continuing list of research-only suggestions. Use the existing knowledge to assess, think, plan, implement, test, fix and package each selected site integration.

### Main operating goal: one site, one complete scoped delivery

Reuse the common chat engine, conversation state, settings, diagnostics and lifecycle where appropriate; implement and test the selected site's adapter and explicit feature requirements. Research is an input to delivery, not a substitute for a working project.

The daily cadence is the owner's target, not a guaranteed 24-hour completion or an autonomous scheduled service. Site selection, permission/access and achievable scope must be checked for each cycle. If blocked, provide the exact blocker and runnable work completed; do not describe an offline scaffold or untested adapter as a complete live integration.

Operational checklist: [DAILY_SITE_DELIVERY.md](docs/DAILY_SITE_DELIVERY.md). No next site has been selected by this clarification alone.

Communication preference evidenced by the conversation: informal Bangla/Banglish, collaborative and practical.

**Plain-language goal:** “আগের কাজগুলোর usable knowledge রেখে এমনভাবে project বানাতে চাই, যাতে নতুন agent দ্রুত context পায় এবং similar platform-এর জন্য পরিষ্কার architecture ধরে কাজ এগোতে পারে।”

## B. Observed in historical source, not automatically a new requirement

The previous code contains:

- Go desktop dashboards with browser/profile worker lifecycle and diagnostics.
- Python GUI/CLI chat automation with local rule/flow engines and template pools.
- Optional supervisor/resource-governor boundaries.
- Browser DOM tracking and separate headless/WebSocket experiments.
- Telethon-based per-user event processing and local reply selection.
- Capture/protocol reference material and unrelated Reddit account-checking tooling.
- Conversation stages, state flags, reply provenance, pending replies and anti-repeat logic.

These observations explain existing projects. They do **not** authorize every behavior for a future app or imply the owner wants every historical feature copied.

## C. Useful design preferences inferred from the code

These are proposed defaults to confirm, not established owner instructions:

1. Keep a working single-worker mode before scaling.
2. Keep chat logic independent of the site transport.
3. Make settings and reply data editable without rewriting the UI.
4. Expose readable status/logs and a reason for each reply decision.
5. Preserve state per conversation and avoid duplicate processing/sending.
6. Make optional acceleration fail gracefully rather than blocking basic use.
7. Keep entrypoints/install/start procedures understandable for non-experts.

## D. Unresolved before the next build

| Decision | Current status |
| --- | --- |
| Target website/platform and supported integration | Not specified. |
| Desktop, web dashboard, CLI or messaging app | Not specified. |
| Exact required features and priority | Not specified. |
| Local rules/templates, LLM, or hybrid reply generation | Not selected. |
| Whether any proactive messaging is allowed | Not specified; default to user-initiated/consented interaction. |
| Number of users/workers and resource budget | Not specified. |
| Operating system, hosting, packaging and deployment | Not specified. |
| User identity/bot disclosure, age/consent rules and data retention | Must be defined before release. |
| API access, account authorization and platform terms | Must be verified for the chosen platform. |

## E. Definition of a successful handoff

A new agent can explain the owner goal, identify the closest baseline family, find a method/source snapshot, describe conversation routing and state, list known defects, and propose a testable next milestone **without confusing assumptions with requirements**.

This document is the starting context, not a finished specification for an unnamed future site. Record confirmed new decisions in the next-project brief rather than silently rewriting historical observations.
