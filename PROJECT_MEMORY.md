# Project memory — শুরু এখান থেকে

## ACTIVE SESSION — 2026-10-16 approved operator workspace implemented

- **Latest owner:** “ok approve” accepts master dashboard plan. Actual UI-scope approval recorded separately in `docs/DASHBOARD_APPROVAL.json` (reference `owner-chat-2026-10-16-ok-approve-operator-dashboard`, SHA23da052a4007f00b2c4a29447bda04d7bf0130447877fdef4453a64ae3fe4d93). Master plan itself unchanged. Do not ask approval again or mistake this for provider scope expansion/live acceptance.
- **Active/progress:** DS only, **2/8=25%, Step3partial**. Seven successors LOCKED. Canonical queue/machine block/revision and frozen approved DS-DIAG-v1 unchanged; UI work does not award Steps3/5 out of sequence. Order DS→Minnit→RumbleTalk→Chatwee→Chatblink→StrangerMeetup→Chatango→Chatiw.
- **New default:** `app.py`/factory now home `workspace`, original `static/workspace.{html,css,js}`. Dark operator layout based on approved Go/EVA-inspired plan; seven pages Home, Sites/Delivery, Messages, Sessions, Live Chat, Settings, Logs/Tests. Functional actual API status/controls, not a mockup. `/`, `/workspace`, default `/operations` and `/test` use new shell (`/test` opens Messages). `/plan` preserved read-only; explicit `--home planning|operations|tester` and `/legacy/*` retained, no files deleted or retired default restored.
- **Local tools migrated:** TXT upload/editor/sample, ordered safe preview, explicit Start/Stop/Resume/Reset, per-input next line, EOF, same-event uncertain retry, local report polling. Existing ReplyTester engine/limits reused; new GET `/api/reply-test/sessions` returns bounded metadata only (max50, no scripts/raw input/event hashes). Saved session selection restores script/state, never starts. Live Chat is read-only last60 tab-local bubbles, no historical inputs/provider transcript persisted. Drafts survive polling.
- **Settings/control:** DS-only non-secret slot creation/selection/table/Stop; selection never changes private env binding. Existing sanitized preflight + shadow controls, disabled by default; no browser provider secrets or locked-site setup. Per-bound-DS-slot Stop/delete now disarms shadow (HTTP regression extended). Global Stop remains usable even when workflow reads fail; no auto retry/rearm. No approve/unlock override/control in new UI.
- **Truth/privacy:** generated/local, provider API acceptance and peer-delivery remain distinct. DS sender absent, external sends0, no provider request/setting/key/callback or GREEN. Token memory-only/cleared input, no storage/URL token or raw HTML rendering; server auth/origin/body/queue guards unchanged. Default preview is public synthetic/sample-only, never enter private data. Single-operator stdlib dev server, production hardening still needed.
- **Tests:** final full command with --ui --browser: **159 Python +55 DOM/local-HTTP +7 real Chromium smoke PASS**, four app JS syntax checks PASS, source-bound receipt must remain fresh. New9Python+16DOM checks; real response discarded once for retry and injected workflow-read outage are labelled; two old injected cases retained. Real Chromium covers keyboard/native upload/Unicode/Stop/all7panels at1440/390/320px, no page errors/external page requests/viewport overflow. Not full accessibility/security/load audit. Fixed missing Bangla glyphs using self-hosted OFL Noto Sans Bengali; font/license/provenance in report. Browser tooling/libs/screenshots only ignored .runtime, not app dependencies/release.
- **Next:** owner can self-test new workspace; continue only scoped DS auth/callback/sender/unknown-outcome engineering. Irreducible live prerequisites remain owned provider account/entitlement/room/bot, compatible callback identity/header contract, permitted egress/HTTPS staging and consenting witness. No ordinary-message TXT→provider wiring, no next unlock, no repeated generic approval loop.
- **Last baseline:** `9259d92`; current tested/pushed workspace delivery is HEAD (`git log -1`). Report `research/operator-workspace-2026-10-16/REPORT.md`, source UI review and master plan preserved. Preview old planning process stopped; final restarted `orbit-operator-workspace-6fe31a69` runs0.0.0.0:8080 with provider flags0/blank demo token. Recheck on continuation. Not Step8, no new ZIP; GOALS/frozen plans unchanged. Final --ui --browser receipt fresh; in-memory package69allowlisted members/CRC/private exclusions PASS (no archive written). Default workspace/aliases/preview-style Host + final JS/font bytes smoke PASS; queue25%/seven locked and shadow off/zero sends confirmed. Both approved hashes and queue machine block unchanged.


পর্যালোচনার তারিখ: **2026-10-15 (UTC)**
GitHub owner: [rajuvbygyuiythh](https://github.com/rajuvbygyuiythh?tab=repositories)

## আপনার অনুরোধ

আপনার project-গুলোর main/root file ও core method/flow বুঝে ভবিষ্যতে একই ধরনের project বানানোর প্রস্তুতি রাখা। আপনার সঙ্গে বাংলায় বা Banglish-এ সহজভাবে আলোচনা করা সুবিধাজনক। এই অনুরোধে নতুন app বানানো বা পুরোনো code fix করা হয়নি।

## মূল working goal — সর্বশেষ clarification

**Daily one selected site with one complete, scoped project:** assess → plan → code → test → fix → package → handoff। আগের chat engine/state/logic reuse করে site-specific adapter তৈরি করতে হবে; শুধু নতুন site list বা পরিকল্পনা নয়। Scope ও access দেখে বাস্তব ফল দিতে হবে—একদিনের guaranteed deadline বা autonomous scheduler নয়। পরের site এখনও নির্বাচিত হয়নি।

Workflow: [DAILY_SITE_DELIVERY.md](knowledge-pack/docs/DAILY_SITE_DELIVERY.md)।

## কাজের মান — সর্বশেষ preference

আপনি আরও শক্ত targeted analysis, planning, networking diagnostics, accuracy, testing ও durable memory চান। এগুলো [ENGINEERING_OPERATING_STANDARD.md](docs/ENGINEERING_OPERATING_STANDARD.md)-এ কাজের নিয়ম হিসেবে রাখা হয়েছে: source/evidence আলাদা করা, actual capture capability যাচাই, minimal relevant data, design/code/review pass এবং reproduce → fix → regression test। এটি model upgrade, perfect memory, নতুন plugin installation বা live capture হয়েছে—এমন দাবি নয়।

## কী দেখা হয়েছে

- GitHub-এ দৃশ্যমান **২৩টি repository**-র file tree দেখা হয়েছে।
- **১৯টি ZIP**-এর file inventory ও source hash তুলনা করা হয়েছে।
- প্রধান project family-গুলোর নির্বাচিত entrypoint, core method body ও method inventory পর্যালোচনা করা হয়েছে—প্রতিটি source line সম্পূর্ণ পড়া হয়েছে, এমন দাবি নয়।
- Python source-এর **৪৮৬টি file occurrence / ১৭৩টি unique content hash** syntax-parse করা হয়েছে; এতে code চালানো বা dependency import করা হয়নি।
- Capture/session/token/cookie/credential data-র contents বাদ দেওয়া হয়েছে। ZIP থেকে শুধু নির্বাচিত source/config পড়া হয়েছে; raw captures ও বড় dataset পড়া হয়নি।

## গুরুত্বপূর্ণ বোঝাপড়া

1. **Go desktop family:** Wails UI → App methods → profile workers → browser/API/DOM transport → chat engine → storage/logging। Browser backend বদলানো যায়।
2. **Python EVA family:** GUI/CLI → ThreadManager → browser worker → ChatRuleBot → flow বা legacy engine। `new_conversation()` ও `reply(message, state)` interface reusable।
3. **Headless variant:** transport/client, event queue এবং chat worker আলাদা; browser mode-এর সঙ্গে এক জিনিস নয়।
4. **Telegram family:** Telethon events → deduplication → per-user lock → local routing/reply engine → persistence। ZIP-এর DeepSeek নাম দেখে active AI provider ধরে নেওয়া যাবে না; inspected main flow local-only।
5. **Capture repositories:** application নয়, debugging/reference evidence; reusable app code-এর বিকল্প নয়।
6. **Reddit family:** account-checking tooling; শুধু static architecture দেখা হয়েছে। ভবিষ্যতের কাজেও নিজের/অনুমোদিত account ও platform rules-এর সীমা বজায় রাখতে হবে।

## নকল version ও সতর্কতা

- `bigfih765` = `v2v2cc`: ZIP byte-identical।
- `chatfilehere` = `lastch`: ZIP byte-identical।
- `reddit`-এর `(7).zip` = `(8).zip`: byte-identical।
- `root-project-pro` ও `bigfih765` পুরোপুরি এক নয়; source comparison-এ `live_chat.go` ও তার test আলাদা। নাম/তারিখ দিয়ে কোনটি শ্রেষ্ঠ ধরে নেওয়া যাবে না।
- `chatchat2222` → `eva_bot_complete.zip` → `extracted_project/papipapi/transport/ws_bot.py:252`-এ syntax error আছে। Fix করা হয়নি।
- কিছু public archive/tree-তে session/storage/token-জাতীয় filename আছে। এগুলো valid বা exposed secret কি না যাচাই করা হয়নি। প্রকাশের আগে review/redaction; বাস্তব credential প্রকাশিত হয়ে থাকলে revoke/rotate করা দরকার।
- Source পড়া মানেই app verified নয়। কোনো live login, message send, bot run, Go build বা integration test করা হয়নি।

## Owner communication / execution preference — 2026-10-15

Owner reports personal/family difficulties and wants low-friction, goal-focused help. Do not repeatedly burden them with minor technical gaps or lengthy caveats. Resolve routine engineering problems independently using suitable supported alternatives; briefly state a material limitation in one line, then continue achievable work toward the daily scoped project. Ask only when a consequential choice, required authorization/access, expense or genuinely blocking requirement cannot be resolved independently. Keep progress/results concrete. This does not authorize security bypass, unsolicited traffic/spam, fabricated evidence or claims of background/autonomous work.

## Larger operation ambition — owner update, 2026-10-15

Owner wants **100+ sites/integrations managed from one dashboard** and targets **50k daily Snap user acquisitions**. These are ambitions, not measured results, a traffic forecast or a validated capacity requirement. Preserve daily scoped delivery as the execution unit. Dashboard direction is now confirmed; runtime/hosting/budget and attribution remain undefined. See [SCALE_OPERATION_GOAL.md](docs/SCALE_OPERATION_GOAL.md). Build toward owned/authorized integrations and opt-in acquisition; owner preference to avoid research loops does not authorize bypass or unsolicited mass promotion. The goal update itself installed no service. Subsequent first implementation: [`control-plane/README.md`](control-plane/README.md), an original Python stdlib + SQLite + browser-UI control plane with isolated synthetic worker lifecycle, optional operator token, bounded logs/deduplication, stale-run rejection and global stop. Fifteen Python unit/HTTP tests and eight jsdom + real-local-HTTP checks passed; not real-browser rendering or third-party delivery. Configurations persist but restore stopped. Minnit/DeadSimpleChat entries cannot start (live adapters not implemented); acquisition remains unmeasured. Preview uses only synthetic instances. Source package: `artifacts/orbit-control-plane-v0.1.0.zip`; runtime data/secrets/dependencies excluded. This is OFFLINE_VALIDATED, not a complete live site project.

## Site discovery — 2026-10-15 update

Owner correction: owner জানেন না কোন site বেছে নিতে হবে; agent-কে discovery/recommendation করতে হবে। বারবার target URL চেয়ে discovery আটকে রাখবেন না। নতুন [research report](research/chat-platforms-2026-10-15/REPORT.md) ও [field-level matrix](research/chat-platforms-2026-10-15/sites.json)-এ নয়টি alternative + Chitchat reference আছে।

- Provisional engineering recommendation: **Minnit, owner-controlled/explicitly authorized room**, Community+ webhooks + official bot reply API; backup DeadSimpleChat (advanced API entitlement যাচাই প্রয়োজন)। এটি owner-approved target/purchase বা completed implementation নয়।
- এই owned-room services **Chitchat-এর existing stranger audience-এর equivalent নয়**। Existing-audience automation-এর কোনো permitted + live-working target এখনও যাচাই হয়নি। Chatblink/StrangerMeetup/Chatiw কেবল operator-enquiry shortlist।
- Chatblink retrieved signup/login text-এ Turnstile আছে; challenge solve/login test হয়নি। StrangerMeetup homepage-এ anonymous service ও account-required public rooms আলাদা। Chatzy behavior-modifying user scripts restrict করে।
- Public docs/page-text review হয়েছে; raw headers/TLS/CSP/WAF measurement, runtime XHR/WS, browser storage, signup/API access ও user-chat delivery হয়নি। **Zero messages sent**। Shodan/Censys/crt.sh/Wayback/WhatWeb/JA3 tools run হয়নি।
- Matrix validator passed + four deliberately invalid-record rejection checks passed; এগুলো research-artifact consistency checks, application/live-chat tests নয়। Existing knowledge ZIPs অপরিবর্তিত।

## পরের project শুরু করার নিয়ম

প্রথমে platform, UI, প্রয়োজনীয় feature, transport, data/privacy এবং acceptance test নির্ধারণ করুন। তারপর একটি নির্দিষ্ট baseline snapshot বেছে নিয়ে একটি worker + একটি conversation-এর offline test তৈরি করুন। এরপর UI, persistence ও সীমাবদ্ধ concurrency যোগ করুন। পুরোনো সব version একসঙ্গে copy করবেন না।

বিস্তারিত method map ও build checklist: [docs/PROJECT_PATTERNS.md](docs/PROJECT_PATTERNS.md)
সব repository, archive SHA-256, source reference ও method location: [docs/repository-inventory.json](docs/repository-inventory.json)

## ভবিষ্যতের কথোপকথনে

এই নোট model training বা চিরস্থায়ী ব্যক্তিগত memory নয়। নতুন session-এ এই file ও pattern document পড়তে বললে context ফিরিয়ে আনতে সাহায্য করবে। GitHub-এর source বদলালে inventory আবার যাচাই করতে হবে।

## Supported-contract milestone — 2026-10-16

- Active analysis scopes: Minnit authorized-room message contract; DeadSimpleChat authorized-room button-action + bot-send contract. Both are owned-room infrastructure, not an existing-stranger acquisition audience.
- Implemented original offline inspectors/specifications, two-site evidence catalog, source-bound test receipts and dashboard **Site research** + synthetic workbench. Six documentation/design gates plus two passing regression gates = **8/12 (67%) checklist completion**, not confidence/success probability. Live starts remain disabled; four explicit live gates remain.
- Actual tests: **43 Python + 12 jsdom/local-HTTP checks passed**, JS syntax passed. No provider credentials, platform messages or acquisition campaign.
- `multiplechat` pinned at `c24e1f94174b458860f0a16c4725adc59a6fe40e`: 740 file entries inventoried, all 26 Python files syntax-parsed; seven files' selected lifecycle/state/send/debug methods reviewed deeply. Raw captures/profile/DB contents not read/imported/repacked; no upstream code executed/copied. Findings: shares are not acquisitions, DOM Enter is not peer ACK, content-based dedup, pre-delivery state advance, cancellation/cleanup and service-wiring risks.
- Reports: `research/supported-integrations-2026-10-16/REPORT.md`, `research/multiplechat-review-2026-10-16/REPORT.md` + inventory. Source/ZIP v0.2.0 preserve sanitized findings and runnable local work; previous ZIPs unchanged. Dashboard polls evidence on refresh; no autonomous research/push scheduler.

## Remaining-site onboarding — 2026-10-16

- v0.3.0 adds all nine shortlist alternatives + Chitchat baseline + Joingy/Isexychat source references: **12 tracked records**, **eight configurable site types**, four local documented-subset inspectors and zero live platform connectors. Synthetic sandbox remains the sole runnable worker.
- Canonical `control-plane/platforms.py` drives UI/API choices, blocked reference types and local fixture capabilities. `workspace.py`/`tools/seed_workspace.py` repeatably create missing inactive slots without changing existing names or starting workers.
- New RumbleTalk inspector is a REST-history snapshot, not webhook; system-send spec enforces 2000 UTF-8 bytes. New Chatwee inspector redacts session-ID result, not a message; chat sending remains unsupported.
- Per-site test receipt coverage required; unknown transports cannot inherit another site's tests. Four narrow scopes 8/12 with fresh proof; Chatblink 1/12, StrangerMeetup/Chatango/Chatiw 2/12. Restricted/reference implementation percentages are N/A. No success-probability claim.
- Report: `research/site-onboarding-2026-10-16/REPORT.md`. Reproducible backup: `control-plane/tools/package_release.py`; old ZIPs unchanged. No raw captured sessions/upstream code imported, no unsolicited platform messages or acquisition traffic.

## Missing-gap implementation — 2026-10-16 · v0.4.0

- Filled the announced Minnit single-room diagnostic code slice: `control-plane/minnit.py`, dedicated `/hooks/minnit/{secret}`, SQLite durable hashed dedup/one-shot intents/outcomes, pinned form/X-Key sender, operator-approved fixed disclosed pong only, persistent cooldown, restart disarm/crash recovery and Stop/bound Delete integration. Intake never auto-replies; fleet starts remain simulator-only.
- Separate dashboard **Minnit diagnostics** shows sanitized server configuration blockers, timed arm/disarm, pending approval and latest 50 durable outcomes. No credentials/raw transcripts exposed or retained. A URL secret proves possession, not provider identity/signature.
- Actual local checks: **87 Python + 20 DOM checks PASS**, JS syntax PASS; two of the DOM checks explicitly inject synthetic enabled-state responses, remaining 18 use local HTTP. Transport/opener are fake in tests; no third-party requests/messages occurred. Receipt must match current source before packaging.
- Official Minnit API section refreshed: sendmessage max 10,000 characters, example success:true/Message sent. Exact live channel semantics/callback compatibility still unknown. Incoming/outgoing channels are separately configured, never guessed.
- Material live blockers: authorized room/key/plan and approved public HTTPS deployment/provider egress; this sandbox's host allowlist excludes Minnit organization endpoints. Four live gates remain pending (8/12 checklist). Do not claim live connected/peer delivered from API acceptance or passing mocks.
- Report: `research/minnit-diagnostics-2026-10-16/REPORT.md`; complete setup and controlled staging in `control-plane/README.md`. Backup v0.4.0 includes new module/tests/report via allowlist; previous artifacts preserved. Runtime DB remains private/ignored and requires stopped/private backup, never Git/ZIP.
- Limits: single operator/process, stdlib development server, no campaign/auto-retry. Stop serializes behind an existing attempt and prevents new sends after returning; the five-second timeout is per socket I/O, not a wall deadline, so trickling responses can delay Stop. Production transport/deployment hardening and consenting two-party live tests remain work, not claimed complete.
