# Project memory — শুরু এখান থেকে

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
