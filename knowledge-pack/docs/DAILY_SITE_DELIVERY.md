# Daily site delivery — main working goal

**Owner-confirmed cadence target, 2026-10-15:** “daily one site with full project.”

Meaning: for each selected site, aim to finish one bounded, usable project by reusing the existing core and building the site-specific integration. Do not spend every cycle producing only another site list. “Daily” is a desired cadence, not a guaranteed deadline, automatic recurring task or permission to call untested code complete.

## 1. Read and align

Read `GOALS.md`, `CHAT_SYSTEM.md`, `PROJECT_PATTERNS.md` and `SECURITY_AND_LIMITATIONS.md`. Preserve the distinction between historical observations and current owner requirements. The knowledge ZIP contains documentation and declarations, not a ready-to-run common engine; actual source must be inspected or implemented before reuse.

Current baseline understanding:

- Python EVA: `new_conversation()` / `reply(message, state)` with separate pending replies and response provenance.
- Go desktop: app lifecycle, worker configuration, browser adapter boundaries and settings/status operations.
- Visible DOM mode, direct API workers and headless event clients are separate execution paths; do not claim parity without tests.
- Durable logic: conversation identity/state, deduplication, reply routing, bounded scheduling, guarded delivery and redacted diagnostics.
- Non-portable logic: auth/session contract, matching lifecycle, site event schemas, ACK behavior, DOM selectors and site-specific policy.

## 2. One-site delivery cycle

| Gate | Work | Evidence required to proceed |
| --- | --- | --- |
| Select | Confirm one target URL and the required features. | Filled next-project brief; explicit non-goals. |
| Assess | Check permitted integration, environment/access, protocol or SDK and main risks. | Documented evidence; no invented endpoints. |
| Plan | Select one baseline and decide reused vs new modules. | Source/hash references, adapter contract, acceptance cases. |
| Implement | Build the core/adapter/config and required UI/CLI path. | Runnable source, explicit setup, no import-time installation. |
| Test | Exercise synthetic fixtures first, then any authorized integration. | Exact commands/results, not only screenshots. |
| Fix | Repair defects found; retest the affected behavior and shared core. | Passing reruns or an honest remaining-failure list. |
| Package | Produce clean source/config examples, dependencies and run instructions. | Extract-and-run/package checks appropriate to the project. |
| Handoff | Deliver source/ZIP, verification report and maintenance map. | Traceable files/commit, known limits and next action. |

Do not guess a required feature from historical intimate/outreach templates. Define the new product's user interaction, disclosure and policy before porting behavior.

## 3. Reuse versus site-specific work

Proposed boundaries, not a claim these modules already exist as a reusable library:

```text
common core
  conversation state + reply decisions + deduplication
  lifecycle + persistence + diagnostics + global policy
                         |
                     adapter contract
                         |
selected site
  permitted auth + match lifecycle + event normalization
  delivery/ACK + reconnect + close/reset
```

Avoid a fresh monolithic bot for every site. Also avoid carrying all old versions into each build. Verify the chosen engine and add regression fixtures before reuse; if the existing source is unsuitable, write a small original implementation behind the same boundary.

## 4. “Full project” definition of done

A project can be called complete **for the agreed scope** only when:

- The target and required features have been confirmed, including what is intentionally excluded.
- Source, dependency/setup instructions, example configuration and the intended start command are included.
- The selected interface is supported/permitted and all required access is available.
- Each required feature has an explicit acceptance case and actual result.
- Start, receive, reply, conversation reset and stop behavior work where in scope.
- Duplicate input, late events, reconnect, expired authorization and ambiguous delivery are handled where relevant.
- A new conversation cannot receive a queued reply belonging to an old one.
- Policy/refusal/exit decisions run before applicable actions; sensitive values do not enter logs or exported artifacts.
- Owned workers/tasks/processes shut down cleanly.
- Unit/contract/build checks appropriate to the implementation run and their results are recorded.
- If live delivery is required, an authorized integration test has actually passed; offline tests alone are not sufficient.
- The delivery ZIP/source has been checked from an extracted or clean environment, with remaining limitations clearly stated.

No “perfect forever”, “undetectable”, “works on any site” or “verified” claims without corresponding evidence.

## 5. Honest status labels

- **READY:** target, permitted interface, scope and access are sufficient to implement.
- **IN_PROGRESS:** implementation or required validation remains.
- **BLOCKED:** a named permission/access/contract/environment issue prevents progress; include the next owner action.
- **OFFLINE_VALIDATED:** synthetic tests passed; required live integration has not passed yet. Not a complete live project.
- **COMPLETE_FOR_SCOPE:** all agreed acceptance gates passed; limitations are stated.

Do not change “full project” into “research report” or “demo” silently to meet the daily target. If a site is unsuitable, explain why and ask the owner to approve a different scope/target.

## 6. Daily handoff

Use [SITE_DELIVERY_REPORT.md](../templates/SITE_DELIVERY_REPORT.md). Report:

1. Target, approved scope and baseline snapshot.
2. Reused modules, new adapter and implementation changes.
3. Tests/build/integration commands with actual outcomes.
4. Fixed defects and remaining failures/blockers.
5. Source/commit, ZIP and privacy/packaging checks.
6. Site-update maintenance points: schema, event mapping, selector or version assumptions.
7. Whether the next site is selected. Do not start a different target without confirmation.

## 7. Next action and scheduling boundary

The next site is **UNSELECTED**. The owner has clarified the workflow, not authorized a specific site's feature set or a background service. Continue in an active session once a target and essential requirements are supplied. Record the confirmed decisions so a later agent can resume without inventing context.
