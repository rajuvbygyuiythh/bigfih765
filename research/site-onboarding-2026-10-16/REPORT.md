# Remaining-site onboarding · v0.3.0 · 2026-10-16

## What “added” means in this release

All nine alternatives from the earlier shortlist are now in the dashboard, alongside Chitchat and the two upstream source references. **12 research records, eight configurable site types, four local contract inspectors, zero live platform connectors.** The synthetic sandbox is separate and is the only runnable worker. A saved configuration is not a connected bot.

A shared `platforms.py` registry governs backend validation, UI choices, contract labels, reference/restricted status and research capabilities. Repeating `tools/seed_workspace.py` creates only missing inactive slots; it does not rename existing configurations, start workers or contact services. SQLite records are runtime data, not published; the source-controlled registry and seed script reconstruct the baseline slots.

## Added site scopes and next steps

| Site | Added to project | Next concrete gate |
| --- | --- | --- |
| Minnit | Existing documented message-batch inspector and send specification; inactive configuration | Supported inbound verification, authorized room/entitlement, real adapter and staging/peer test |
| DeadSimpleChat | Existing button-action inspector and send specification; inactive configuration | Same live gates; ordinary-message schema remains unimplemented |
| RumbleTalk | NEW history-response inspector and system-message specification; inactive configuration | Verify owner access, limits, cursor/order behavior and real authenticated adapter |
| Chatwee | NEW redacted SSO-result inspector; inactive configuration | Obtain a supported conversation send/receive contract; SSO is not a chat-message API |
| Chatblink | NEW research record and inactive configuration | Operator-approved interface/auth/message contract; Turnstile is not bypassed |
| StrangerMeetup | NEW research record and inactive configuration | Approved route; choose anonymous random mode vs account-required public rooms |
| Chatango | NEW research record and inactive configuration | Provider/room-owner-supported interface and appropriate mixed-age scope |
| Chatiw | NEW research record and inactive configuration | Approved guest/member auth and messaging contract; no private endpoints guessed |
| Chatzy | NEW restricted tracking record; configuration creation rejected | Explicit operator exception or documented approved alternative |
| Chitchat reference | NEW reference record; configuration creation rejected | Current authorized supported contract, not historical archive assumptions |
| Joingy source reference | NEW upstream-reference record; configuration creation rejected | Current supported contract and reuse-license resolution before importing code |
| Isexychat source reference | NEW upstream-reference record; configuration creation rejected | Same; no adult/funnel templates or captured sessions imported |

## Step-by-step workflow now available

1. **Site research** lists the source-backed scope, phase, findings and all twelve gates.
2. Search by name or filter **Local contract / Contract needed / Restricted / Reference**.
3. Click **Add configuration** on a configurable site. The dialog preselects the site and saves an inactive named slot. Restricted/reference records cannot use this path, including direct API requests.
4. In the fixture workbench, choose one of four actually implemented offline inspectors. Other sites do not inherit a parser or passing test status just because their name is listed.
5. Complete each site's missing contract/access/implementation/acceptance gates before enabling any real connector. No live start path exists in this release.

## RumbleTalk: reviewed and implemented local subset

Primary sources re-read this turn:
- [Message APIs](https://dev.rumbletalk.com/rest/messages).
- [Authentication](https://dev.rumbletalk.com/rest/authentication).

Owner key+secret yields an expiring bearer token; no token is issued by this application. `GET /chats/{chatId}/messages?fast=true` is documented message history, **not** a webhook. The older read route is deprecated. Local fixtures wrap the response with `route_chat_id` as our own request-context metadata; it is not a vendor response field. Because each returned row lacks a room ID, inspection explicitly marks room-scope verification false. No real history is fetched.

The local inspector validates boolean success, row/ID/text shapes, a 100-row local cap and expected route context; it ignores token/IP/other extra fields. A secret-free `describe-send` specification represents the documented **system-message** POST, not private/direct-message parity. The limit is **2,000 UTF-8 bytes**, not 2,000 characters. Regression cases cover multi-byte boundaries. No HTTP request is submitted.

## Chatwee: reviewed and implemented local subset

Primary sources re-read this turn:
- [SSO login](https://chatwee.com/http-api/sso-user/login).
- [SSO register](https://chatwee.com/http-api/sso-user/register).

Login returns a session-ID string and docs describe `chatwee-SID-[CHAT_ID]` cookie handling. The local fixture supplies synthetic request context and a synthetic session response. Output includes only presence/redaction flags; session value/clientKey/cookies/IP are never echoed or persisted. This is neither an authenticated login nor an incoming user message. A message-send request fails closed instead of inventing a chat API from SSO documentation.

## Progress that cannot be borrowed

With fresh passing source-bound test evidence for a specific implemented contract:

- Minnit, DeadSimpleChat, RumbleTalk and the narrow Chatwee identity scope: **8/12 = 67%** checklist completion. These are different limited scopes, not four completed chat bots.
- Chatblink: **1/12 = 8%** (common lifecycle plan only).
- StrangerMeetup, Chatango and Chatiw: **2/12 = 17%** (guest-flow review plus common lifecycle plan).
- Chatzy and all reference records: **N/A**, not a misleading implementation percentage.

Percentages are completed checklist items, not effort estimates, conversion predictions, security coverage or success probabilities. A globally passing suite without per-platform coverage cannot complete a site's local-test gates. Unknown contracts remain pending; unsupported fixtures return an error. A manual catalog flag cannot enable live starts.

## Evidence and validation

Python regression tests cover new local contract shapes, UTF-8 limits, SID redaction, unknown-contract refusal, per-platform proof, registry/configuration gates and repeatable inactive seeding. DOM/local-HTTP checks cover registry-generated dropdowns, all twelve research cards, filters, reference restriction, site-specific configuration and both new inspectors. Exact totals/results are in `control-plane/BUILD_REPORT.md` and the source-bound receipt. These are not real-browser rendering, remote security audits or third-party chat tests.

Earlier findings for the other sites are carried forward with their original primary references and explicitly unresolved runtime contracts; this turn did not pretend to repeat their signup/network tests. The existing platform matrix and previous two-site/upstream reports remain historical snapshots rather than being rewritten as new evidence.

## Backup and boundaries

ZIP v0.3.0 includes original source/tests, registry/catalog, receipt, reproducible packager, inactive seed utility and authored reports/inventory. Raw captures, source archives, cookies/tokens, session profiles, runtime SQLite and dependency directories are excluded. All earlier ZIPs remain unchanged. GitHub push is a completed foreground operation only after `git push` succeeds; no automatic research/campaign/push scheduler is installed.
