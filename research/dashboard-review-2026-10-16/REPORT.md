# Dashboard source review · 2026-10-16

## Request and scope

Owner: “plan all form first”, retain lock/unlock rules, remove current dashboard and analyze other project dashboards to understand preferred style. This turn starts analysis/planning and retires the previous default, **not a final replacement dashboard or a provider scope expansion**.

Reviewed representative UI families, not every repository or every line. Existing root inventory covers 23 repositories; source-specific UI review below is fresh. No project application/dependency from these archives was executed. No settings/session/cookie/credential/chat-data/capture contents were inspected. Source-only scratch files stay in ignored `.runtime/dashboard-review`; original archive unchanged. Source findings are not proof the old apps work today or the owner's final visual preference.

## Evidence

| Family / pinned source | Targeted files / observed sections | Findings |
| --- | --- | --- |
| Go/Wails, local `root-project-proxy-diagnostics-UNVERIFIED.zip`; SHA256 `600f36acc67efd0d0337e6d6d60120d97fad62f6a794ebfb5cf46bf477f4397e` | `root-project/main.go` embed/startup; `cmd/chitchatui/frontend/dist/index.html`, `styles.css`, `app.js`: navigation, home controls/stats, message modes, browser/settings forms, state refresh and chat transcript | Root actually embeds this frontend. Dark olive/green, left sidebar Home/Proxy/Message/Browser/Setting. Start/Stop in home header; compact stats above session selector/transcript. One-line-per-message sequence and separate configuration page. JS separates state polling from unsaved form fill; versioned chat refresh rejects stale response. |
| Python EVA desktop, [cccccchhtt11@5250d6100844b47df31b7f19ba18111607015cf8](https://github.com/rajuvbygyuiythh/cccccchhtt11/tree/5250d6100844b47df31b7f19ba18111607015cf8) / `EVA_Bot_full_project_CDP_dashboard_capture_verified.zip` | `papipapi/entry/main.py`: theme lines65–95; sidebar/topbar/navigation/runtime setup275–459; selected dashboard/settings controls and method declarations | Qt/PySide-style dark blue/purple control center. 240px sidebar; Dashboard, Live Chat, Sessions, Pictures, Accounts, Settings, Logs. Large Start/Stop kept visible; CPU/RAM mini monitor, live status strip, stacked pages and explicit session state. |
| multi-site Textual terminal UI, [multiplechat@c24e1f94174b458860f0a16c4725adc59a6fe40e](https://github.com/sff96918-byte/multiplechat/tree/c24e1f94174b458860f0a16c4725adc59a6fe40e) / `multi-site-bot.zip`; SHA256 `5600f8eb5db938e3a52cf34dcdd8e4a469efdc46580fdfc95bc6497cfdf6b002` | `dashboard/cli.py`: compose/navigation/settings/tables, mount refresh schedule and selected message/log refresh; `src/main.py`: assembly context (prior report plus source loaded) | Not a web UI. Overview/Control/Settings/Logs/Fixed SMS plus modes/DB/threads/proxy/SMS/debug/leads. Per-site lifecycle, compact tables, fixed-file assignment with line progress, bounded views needed. Many panels could overwhelm a small owner-facing first version. |

An initial source-selection probe of `version1cc/refer project.zip` found no files matching the narrow GUI filename filter; no semantic GUI review is claimed for that archive. No second-site protocol research performed. Historical sibling variants were not exhaustively re-reviewed; read coverage is these representative interfaces plus existing pattern documents.

## Reproducible selected UI file hashes

```text
3167c1c1dd6ef2eb8fe91872eecac416961b06d5b14c4a93e39c34bf8e181b5c  Go index.html
686e308caeb66b7169b2118e515f3648b12eb6917799f29d41ec1489376d76b2  Go styles.css
1b53d9f810e0e45b7e7c7cedb0e146ee3e135f53e56171fed9b54c0987f3104e  Go app.js
999e4e27809142811991f1d9a22b1a17310fafc53d904859b9c09e2c6de20228  EVA entry/main.py
80b7681dc3a5024c6881fb15c51d8d2a02aa101edbc81bc9021f7c0ed3c8c0a6  Textual dashboard/cli.py
9f4fe5fd1303c682f981d68445fcd9165c10d6e239dc0075e5db5a1fa7907a51  Textual src/main.py
```

## Inferred preference → proposed design, not yet confirmed

- Practical **operator workstation**, not a marketing/analytics wall or standalone TXT wizard.
- Fixed sidebar, dark neutral background, one restrained accent; compact readable controls and clear disabled reasons.
- Home holds lifecycle/status; Messages, Sessions/Live Chat, Settings and Logs are separate. Site queue must be prominent, not hidden in technical diagnostics.
- Big visible Stop, small truthful counters, per-session reports. Keep implementation progress distinct from service connection and message delivery.
- Preserve TXT self-test as a tool inside Messages, not the entire app. Do not wire its ordinary-message engine to the approved DS one-shot adapter.
- Do not copy archived secrets-in-forms, silent autostart, unredacted transcripts/debug exports, lead-count claims, proxy/bypass behaviors or every advanced panel. Source patterns only; original implementation, no upstream source redistribution.
- Exact palette/density remains proposed: Go's muted green vs EVA purple differs. Suggest neutral dark + restrained green to keep status clear; visual preference is not assumed proven.

## Implemented retirement and checks

Production CLI/factory default is now `planning`, a neutral read-only plan/status document with actual authenticated `/api/workflow` data. `/`, `/test`, `/operations` in default planning mode no longer show previous dashboards. `/plan` always serves this page. No start/approve/unlock/setup/write API added. Token is memory-only, cleared from input, never in URL/storage.

Prior code is **preserved, not deleted**: explicit `/legacy/operations`, `/legacy/test`; old `--home operations|tester` remain opt-in regression/rollback modes. Their existence is not a new design endorsement; API auth/queue gates unchanged. Browser assets remain allowlisted; no docs/private environment/source folder is served. Existing legacy DOM tests deliberately opt into legacy mode.

Full roadmap/module forms/acceptance: `docs/DASHBOARD_MASTER_PLAN.md`. DeadSimpleChat remains2/8=25%, Step3partial, seven locked. No provider or frozen-plan changes. Actual `python -B control-plane/tools/run_checks.py --ui`: **150 Python + 39 DOM/local-HTTP PASS**, all three JS syntax checks PASS, source-bound receipt fresh. Five new Python and six new real local-HTTP/jsdom checks cover default retirement, explicit legacy preservation, authentication, unchanged queue and read-only/no-token-storage behavior. Existing suites retained. Rendered-browser visual review of the replacement remains future work.

Operational verification: default planning preview started on0.0.0.0:8080, all four default page routes smoke-checked with a preview-style Host; actual workflow remains DS25%/seven locked, shadow disabled/zero sends. Future package validated in memory:59allowlisted members/CRC PASS with new plan/review/assets/tests, no upstream source/private/runtime data; no ZIP written. Frozen DS plan hash/canonical queue match baseline, GOALS unchanged, no tracked files deleted.
