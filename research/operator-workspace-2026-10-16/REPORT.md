# Approved operator workspace · 2026-10-16

## Decision / boundaries

Owner said **“ok approve”** after the master dashboard plan. Recorded independently in `docs/DASHBOARD_APPROVAL.json`: plan SHA256 `23da052a4007f00b2c4a29447bda04d7bf0130447877fdef4453a64ae3fe4d93`, reference `owner-chat-2026-10-16-ok-approve-operator-dashboard`. This is actual chat approval for presentation/tools, not a test fixture or a new provider scope. The master plan itself is preserved unchanged. Approval recording is trusted operator coordination, not a cryptographic owner-identity mechanism.

DeadSimpleChat remains **2/8 =25%, Step3partial**; seven successors locked, queue revision unchanged. UI work does not finish a sequential step, complete live intake or unlock a successor. DS-DIAG-v1/frozen hash and GOALS unchanged. No provider requests, account/key configuration, live callbacks, sender, room replies or peer-delivery proof.

## Delivered

New original `static/workspace.{html,css,js}` replaces the interim planning landing as the default CLI/factory home. Practical dark neutral/green operator layout, fixed desktop sidebar, compact status strip, separate pages, keyboard focus/skip link, responsive mobile navigation, always visible authenticated global Stop. No remote fonts/images/scripts/CDN dependency.

| Page | Actual implemented behavior |
| --- | --- |
| Home | Real workflow ACTIVE site, delivery percentage/eight-step strip, exact scope approval status, local selected-session replies, DS sender count0, sanitized live blockers, next locked successor. Never a fake acquisition/connected metric. |
| Sites & delivery | Canonical eight-site order/state/steps/next requirement, current provider hash/reference and read-only exact plan via authenticated API. No approve/unlock/reorder/start-all controls. |
| Messages | Native UTF-8 TXT upload, editable draft/sample, bounds/validation, ordered text-safe preview, tested existing ReplyTester API; explicit Start/Stop/Resume/Reset; per-input one line; EOF; same-event retry after uncertain response. No provider routing. |
| Sessions | New authenticated metadata-only GET `/api/reply-test/sessions`, up to50 rows; select saved local script/run without auto-start, local session Stop, DS-only saved slot table/Stop. No cookie/profile import or locked-site setup selector. |
| Live chat | Read-only mirror of this tab's **local** observed transcript (last60 bubbles). Distinguishes generated/API accepted/peer delivered. Historical raw user input is not stored/restored; real provider transcript not captured. |
| Settings | DS-only non-secret configuration label creation/inspection. Private slot selection does not change server environment/binding. Sanitized env/setup blockers and private loader instructions. Existing protected shadow arm/disarm/register controls; disabled until configured/approved. No key/room-secret/browser credential form. |
| Logs & tests | Latest30 selected local events +30 shadow intents, filter, secret-free intent outcomes, source-bound receipt freshness/time; stale/failed proof explicitly UNVERIFIED. No raw capture/transcript export. |

Existing `/api/instances` is reused, not renamed as a real account API. New metadata index excludes scripts, user inputs, event hashes/history and file names; fetching a selected script still requires the already-existing authenticated session endpoint. Session persistence/restart-stop and current limits remain unchanged. Only active approved DS creates/starts a local test or receives UI setup controls; server workflow/auth/origin gates remain authoritative.

Per-DS-slot Stop (and deleting its bound slot via preserved API) now also disarms associated shadow intake; local/global Stop remain available despite workflow reads failing. Stop is an acknowledged state-change command, not recall or a guarantee against a later explicit request from another client. No automatic retry/start/rearm. Session selection clears transient input/transcript; polling never overwrites unsaved script or configuration drafts.

Browser token stays in memory only, password input clears; no local/session storage, URL token, API-key UI, HTML interpolation or user-generated DOM markup. Mutation/error handling preserves same-event retry IDs; unverified/missing workflow fails closed for work while authenticated global Stop remains usable. Single process/operator development server, not a multi-user production service or security certification.

## Routes / launch

```sh
python -B control-plane/app.py --host 0.0.0.0 --port 8080 --db .runtime/orbit-preview.db
```

Default home `workspace`: `/`, `/workspace`, `/operations`, `/test` use new shell (the `/test` path selects Messages). `/plan` remains read-only. Explicit `--home planning` and `--home operations|tester`, plus `/legacy/operations` and `/legacy/test`, preserve planning/old regression views. Old source remains; no deletion/reversion to the old default.

Default shared preview uses empty operator token, synthetic/sample data only, both provider features off. Never use real/private data in this public demo. For private authorized use preserve existing strong-token/private-env setup and production HTTPS/redaction requirements; no credentials were supplied/read/created in this turn.

## Regression / rendered browser

Actual full validation: **159 Python +55 DOM/local-HTTP +7 real Chromium smoke checks PASS**, all four app JS syntax checks PASS. Fresh source-bound receipt records each suite. Nine new Python checks cover bounded metadata privacy/lifecycle/restart and default shell/auth/static/unchanged queue. Sixteen new workspace DOM checks exercise seven pages, real local APIs, native FileReader, Unicode, text safety, Stop/resume/reset/EOF, same-event retry, session index, DS-only setup, draft retention, blockers and honest logs/receipt. One case deliberately discards an actual HTTP response after server execution; another injects a local workflow-read outage. Existing23operations/10lab/6planning checks retained (two old injected cases remain labelled).

`tools/browser_smoke.cjs` is an optional real Chromium check, invoked using `run_checks.py --ui --browser` with `NODE_PATH` pointing at external `playwright-core` and `CHROMIUM_EXECUTABLE` pointing at an installed browser. Test boots its own temporary authenticated server/DB, never uses provider credentials. Actual checks: wrong/correct auth, keyboard navigation, saved seven locks/25%, native TXT upload/Unicode send, global Stop, all seven panels at1440/390/320px with no document-level horizontal overflow, blocked shadow controls, zero JS page exceptions and zero external page requests. Normal browser web security/CSP retained; screenshots inspected locally. This is a smoke/layout pass, not complete accessibility/OS/browser/security/load certification.

For this sandbox only, browser tooling was installed under ignored `.runtime/browser-check` using npm `playwright-core` + `@sparticuz/chromium` (153); bundled NSS/NSPR libraries supplied missing sandbox system libraries. First launch failed on package default-export/missing shared libs; corrected without provider/security/egress bypass. Browser binaries, scratch downloads, libs and screenshots stay out of source/release. App runtime remains Python stdlib; no new production npm dependency.

A Bengali rendering issue in the bare browser environment was fixed with self-hosted **Noto Sans Bengali**, SIL OFL1.1. Font and full license are explicit allowlisted static assets; browser check verifies the face actually loads for Bangla, not just string preservation. Pinned source: [google/fonts@b9b4b56be4f67f120752a756f39299b47366223c/ofl/notosansbengali](https://github.com/google/fonts/tree/b9b4b56be4f67f120752a756f39299b47366223c/ofl/notosansbengali). No remote request is required by the app.

## Remaining

Provider contract/header/callback authenticity and owned question registration, entitlement/account, allowed egress/HTTPS staging, guarded one-shot sender/outcome ledger and consenting witness remain. No live GREEN, successor unlock or new Step8 ZIP. Future source-package allowlist includes new UI/tests/browser-check/approval/report/font+license, never private/runtime data or browser tooling. Validate payload/CRC in memory only in this turn; portable release/extracted-copy validation remains Step8. Continue only DS adapter completion after UI self-test; do not expand ordinary-message automation or work another site.

Final operations: sample-only default preview restarted on0.0.0.0:8080 with both provider flags off and blank demo token. `/`, `/workspace`, `/operations`, `/test` preview-Host routes serve the new shell; JS/font served bytes match final source, receipt current, actual queue25%/seven locked, shadow off/zero sends. Both approved hashes/canonical queue verified unchanged. Future payload built in memory only:69allowlisted members, CRC/private exclusions PASS, no release written. Source backup pushed on fixed Arena branch; no GOALS edits or tracked deletions.
