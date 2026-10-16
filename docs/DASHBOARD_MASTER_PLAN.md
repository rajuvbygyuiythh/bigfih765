# Master plan · plan-first dashboard reset · 2026-10-16

## 1. Owner decision and what starts now

New instruction: plan the whole system first, remove the current dashboard, study the other project dashboards, preserve one-site lock/unlock clarity. Start with source-based review + this complete module/form/delivery plan. Current default dashboards are retired; a **read-only plan/status page** stands in while the replacement is designed. Old source and rollback tools remain, no destructive deletion. This does not re-open provider approval, enable locked sites, or authorize ordinary-message provider automation.

Evidence: `research/dashboard-review-2026-10-16/REPORT.md`. Reviewed Go/Wails, EVA desktop and Textual representative UI sources; not every project line, not rendered/running source apps. Design inference: dense, practical dark operator workspace, sidebar, separated controls/forms, session feed, obvious Start/Stop—not another standalone TXT-lab page. Exact visual preference is proposed, not established.

## 2. System architecture

```text
Operator web workspace
  ├─ Home / Sites / Messages / Sessions / Settings / Logs
  └─ same-origin authenticated API (no browser provider secrets)
       ├─ SiteWorkflow: immutable scope approval + sequential evidence gates
       ├─ lifecycle/controller: instance/run/session isolation + Stop
       ├─ reply engine: validated TXT + local sequence state
       ├─ site adapter: intake → intent → outcome ledger → guarded sender
       └─ SQLite: minimal state/dedup/evidence; source-bound local test receipt
```

One shared shell, adapters per supported site; never clone an entire dashboard per site. 100+ instances is an architecture ambition, not validated capacity or 100 implemented adapters. Delivery %, adapter state and message outcome are independent. Provider network/secrets stay server-side; no automatic startup, no invented send contract.

## 3. Full screen / form specification

| Page | Forms / content | Controls and boundaries | Acceptance before calling it working |
| --- | --- | --- | --- |
| Home | Selected active site, adapter state, current step, blockers; small status strip; scoped session summary | Primary Start/Stop only for supported ready mode; global Stop available even if setup fails; label local/shadow/live separately | No generic Start for a locked/unimplemented adapter; Stop proven under failure and restart |
| Sites / Delivery | Ordered table, ACTIVE/LOCKED/DONE,8steps, evidence, next prerequisite, exact approved plan | Read current plan/hash; approval only for exact scoped plan; completion invokes existing server gate, no unlock-all/override/drag reorder | Tamper/stale revision/wrong hash blocked; one successor only after8steps+live evidence+verified release |
| Messages | One UTF-8 TXT file, line preview/count/validation, local test input and current-line report | Upload, save local script, Start/Stop/Resume/Reset local test; visible local-only badge. Future provider mode requires independently scoped supported contract | Current8KiB/200lines/1000chars bounds, text-only render, one unique local event→one line, retry no extra advance |
| Sessions | Owned integration instance selector, session/run/state table; no imported browser profiles | View permitted diagnostics; per-instance Stop; display expiry/stale state | IDs isolated by site+instance+session+run; restart stopped; no credential/cookie import widget |
| Live Chat / Reports | Consented session view, input/output provenance, generated/accepted/unknown/peer-confirmed labels | Read-only by default; no unsolicited DM/manual send box in initial DS scope; minimal synthetic/shadow view now | Never fabricate a transcript, acceptance or delivery; retention/redaction agreed before private live transcripts |
| Settings | Saved non-secret instance name, exact configuration requirements, sanitized preflight, timing only where supported | Explicit save/cancel; never overwrite unsaved form state during polling. Private env provisioned outside browser | API/operator auth, same-origin, bound slot, no secret return/log/URL; validation before mutation |
| Logs / Tests | Bounded local/shadow/provider outcomes, latest receipt/freshness, failure reason and next step | Filter per site/instance/run; safe report export later; no raw capture export | Sensitive values redacted before storage/export; stale receipts visibly stale; local PASS≠live GREEN |

**Navigation proposal:** Home · Sites · Messages · Sessions · Live Chat · Settings · Logs/Tests. Optional networking/advanced diagnostics under Settings, not copied wholesale. Desktop-class layout, responsive sidebar/table fallback, keyboard focus, labelled disabled states; no remote font/CDN requirement.

Style proposal: neutral dark base + restrained green status accent, compact tables/toolbar, little decoration. Source Go olive/green and EVA purple are references; final palette/layout are still a proposal. No replacement operational dashboard has been built in this planning turn.

## 4. Exact order and what “done” means

This table is a sequencing map, **not new research/setup on locked sites** and not a guarantee each target supports the desired transport. Runtime authority remains `SITES.md`/SiteWorkflow.

| Order | Site | Current state | Work permitted now / after unlock |
| --- | --- | --- | --- |
|1|DeadSimpleChat|ACTIVE,2/8=25%, Step3partial|Finish approved DS-DIAG-v1: registered consenting question/user/action, at most one fixed disclosed diagnostic room reply. Shadow no-send code exists; real sender/auth/staging still blocked.|
|2|Minnit|LOCKED|Only after DS acceptance/handoff: revisit existing diagnostic artifacts against current account/contract, define/approve its scoped delivery, then sequential gates.|
|3|RumbleTalk|LOCKED|After Minnit: verify supported owned-room scope/entitlement; history/system-message evidence is not an authenticated live webhook.|
|4|Chatwee|LOCKED|After RumbleTalk: verify actual permitted feature scope; SSO-only findings are not chat send support.|
|5|Chatblink|LOCKED|After Chatwee: recon/permission/feasibility first; no adapter/compatibility promise.|
|6|StrangerMeetup|LOCKED|After Chatblink: same supported-contract feasibility gate.|
|7|Chatango|LOCKED|After StrangerMeetup: same supported-contract feasibility gate.|
|8|Chatiw|LOCKED|After Chatango: same supported-contract feasibility gate.|

Chatzy remains restricted. Chitchat/Joingy/Isexychat are references, not unlocked targets. If a site has no authorized viable contract, keep its gate blocked and report the material decision; do not silently mark done or skip it. All-site roadmap visibility is allowed; parallel recon/code/configuration is not.

For every site:1Recon →2scoped plan/contract + owner approval →3intake →4outbound →5dashboard integration →6real authorized staging →7regression →8ZIP+SHA256+handoff. Completion also requires actual live acceptance and all independent gates. Dashboard work supporting the active DS site does not itself completeStep3 or5.

## 5. Concrete implementation batches after plan-first review

1. **This turn:** review representative old dashboards, write screen/form architecture and queue/acceptance map, retire default old views, maintain read-only actual queue, test/push. No provider call or queue advancement.
2. **Replacement shell:** original sidebar/status/header with only active DS capabilities, responsive/focus states, real queue detail, visible Stop. No pretend functional controls, hidden override or unlocked next-site card.
3. **Messages + local reports migration:** reuse tested ReplyTester/API; one TXT sequence, local test embedded as a module, stable unsaved-form state and concurrency guards. Not a live provider bot.
4. **Settings + diagnostics:** use existing private-loader/preflight/shadow APIs, named blockers and server-only secret provisioning. Preserve Stop/intent lifecycle, show source-bound receipt and limited outcomes.
5. **DS adapter completion:** resolve documented auth-header/callback identity/question registration, implement approved guarded one-shot sender and unknown-outcome ledger. Requires permitted provider egress + authorized account/entitlement/HTTPS deployment; credentials never chat/Git. These are material external prerequisites, not solved by redesign.
6. **Live validation and handoff:** consenting witness, exactly one fixed reply, duplicate/restart/expiry/Stop evidence, real browser layout/accessibility verification, full regression, clean-extract package/manifest/hash. Only then guarded unlock of Minnit.

## 6. Test and release gates

- Keep existing domain/HTTP/legacy UI suites as regression, not discard prior functional code to match a new mockup.
- Add planning-route default/retirement tests; real local HTTP auth/read-only queue tests; no secret browser storage or write calls; actual seven locks unchanged.
- Replacement UI needs keyboard/mobile/desktop rendering checks; jsdom does not prove visual layout. No rendered-browser test claimed now.
- Source-bound receipt must match final code. No GOALS or approved DS plan edits, file deletion, fake GREEN, provider calls or new Step8 archive in this turn.
- Future package allowlist includes plan/review/new assets/tests; private env, raw captures/runtime DB and downloaded upstream source remain excluded. Validate in memory now, create ZIP only atStep8.

## 7. Handoff / next action

Read this plan and review report before building the replacement shell. Latest implementation baseline `cf2397a`. Keep DS-DIAG-v1 hash `dc8a906cd04c6293c54d347f1a910767202a890f8dbbc45b9206c1a80edb01f8` unchanged; redesign is a presentation change, not approval for general TXT-based provider messaging. The owner invited starting analysis/planning now; do not respond with another generic “shall I proceed?” loop.
