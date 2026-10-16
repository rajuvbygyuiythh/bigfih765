# Work roadmap

## Latest workstream override — Europe browser shortlist, 2026-10-16

Owner approved all eight Europe website tasks and requested no repeated approval/unlock prompts. Their assessment/implementation backlog is now unlocked independently of the historical runtime queue below. Use `tools/europe_tasks.py` to read all packets. Public recon is documented; no adapter or live contract is established. Three primary policy pages reviewed: 6obcy unofficial-client/ads restrictions, Bazoocam commercial/advertising restrictions, Chaat conditional bot tolerance with+B and resource/session rules. Next is Chaat contract investigation; review the remaining five policies independently. Never convert owner work approval into third-party permission or bypass restrictions. Preserve GOALS and historical DS/other-provider acceptance gates. No auth/demo loop.

Scope: supported/authorized integrations and consenting tests. Mission remains unchanged in `GOALS.md` (alias to the existing knowledge-pack mission). Active queue and percentages: `SITES.md`. No batch research, file deletion, force push or rebasing published work.

| Step | Deliverable / exit gate |
| --- | --- |
| 1 Recon | One site's primary docs, observed vs unknown contracts, runnable diagnostic code + tests; no invented protocol |
| 2 Contract design | Explicit event identity, auth, room scope, ACK/failure/Stop policy; unresolved live assumptions stay gated |
| 3 Intake | Protected narrow intake, strict schema, durable dedup/identity; malformed/replay tests |
| 4 Outbound | Guarded opt-in transport and one-shot intent/outcome ledger; never blind retry ambiguous sends |
| 5 Dashboard | Server-only configuration, status, operator controls, secret-free diagnostics |
| 6 Integration | Authorized staging; consenting witness; API acceptance != delivered; block rather than fabricate access |
| 7 Regression | Failure/restart/race/privacy cases, source-bound full suite; no false live PASS |
| 8 Handoff | ZIP + sha256 in artifacts, manifest/clean-extract checks, source/evidence/run instructions; preserve old artifacts |

Each turn: read PROJECT_MEMORY → SITES → SKILLS → GOALS → PLAN; code/test/push on the fixed Arena branch; update memory/queue and append CHANGELOG. Delivery percent = completed steps / 8, independent of the older twelve-gate evidence checklist. Steps may contain multiple implementation turns; do not award completion for a scaffold alone.

Sequential lock rule: only the ACTIVE site in SITES may advance. All other targets stay LOCKED. Complete all eight steps and live acceptance, then use `site_queue.py complete-and-next` to unlock exactly one successor. Do not pick another QUEUED/BLOCKED site as a workaround, skip steps or unlock everything. The current lock-feature request does not advance site delivery progress.

Current gate: **DeadSimpleChat plan APPROVED; Step 3 partial; local TXT lab + disabled shadow intake/private setup implemented.** Read `research/deadsimplechat-plan-2026-10-16/PLAN.md` (DS-DIAG-v1). Owner explicitly approved and requested a small TXT web tester; approval is recorded for unchanged DS-DIAG-v1. The local requested addition is implemented and authorized, but does not silently change the live provider scope. Exact plan approval → setup/verification → actual GREEN → guarded unlock/start of Minnit. Step 3+ and runtime diagnostic setup require the approved current plan hash. A changed scope requires re-approval. Never promise 100% future success or mark GREEN from local/mock tests. Owner now requested plan-first dashboard reset: read `docs/DASHBOARD_MASTER_PLAN.md` and UI review report. Owner subsequently said “ok approve”; approved original operator shell/local tools are now default `workspace`, with read-only plan still at `/plan`. Dashboard approval is recorded separately in `docs/DASHBOARD_APPROVAL.json`, not DS provider approval or live GREEN. Old dashboards are retired from default, preserved as explicit legacy routes/modes. The small tester is `/legacy/test` (or explicit `--home tester`); live reporting there means local events only. Next is private authorized configuration and provider auth/callback/staging verification; shadow matching is not live delivery. `.env.example` is a safe template; explicit `--env-file` loads owner-only private values, never shell-sources them. No sender exists, no next-site unlock. Do not copy Minnit webhook auth, infer normal-message schemas, turn button definitions into unique occurrences, or guess whether the extra Authorization header is required. No capture requested in Step 1: first establish exactly which evidence Step 2 actually needs. Credentials, if later necessary, are entered by the owner in ignored `.env.local`; tools do not automatically source it.

User-requested system OUTPUT FORMAT was not present in the supplied instructions. Until supplied, use only one concise handoff block containing SITE, STEP, PROGRESS, CODE, TEST, PUSH, NEXT; Bangla/Banglish values are preferred. Do not claim this fallback originated in a system prompt.

Dashboard implementation order: source review/full form plan → original operator shell → Messages/local TXT migration → Settings/status/reports → finish scoped DS adapter → actual live acceptance/regression/package → unlock Minnit only. The all-site sequence map is planning visibility, not authorization for parallel locked-site research or implementations. Approved shell/local tools implemented with159Python+55DOM+7Chromium smoke PASS; scoped provider integration/live gates remain unresolved.
