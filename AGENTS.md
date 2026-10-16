# Project context for incoming agents

Read `PROJECT_MEMORY.md`, then `knowledge-pack/GOALS.md`, `knowledge-pack/docs/DAILY_SITE_DELIVERY.md`, `knowledge-pack/docs/CHAT_SYSTEM.md` and `knowledge-pack/docs/SECURITY_AND_LIMITATIONS.md` before planning or coding.

## Owner-confirmed working goal

Aim for **one selected site per day with one complete, scoped project**: assess -> plan -> implement -> test -> fix -> package -> handoff. Reuse verified common chat logic/state/lifecycle and implement the site-specific adapter. Do not replace delivery with repeated broad site lists once a target and scope are agreed.

Daily cadence is a target, not a completion guarantee or an automatic background schedule. Current local contract scopes are Minnit, DeadSimpleChat, RumbleTalk history/system messages and Chatwee SSO-only; the full shortlist is tracked in the capability registry, not live-enabled; live access is not configured. Ask only for requirements/access that actually block implementation; do not invent endpoints or claim an offline scaffold is a completed live integration.

## Larger operation goal — owner update, 2026-10-15

The owner wants one dashboard managing 100+ site/integration instances and targets 50,000 daily Snap user acquisitions. Treat these numbers as business ambitions, not measured performance, achievable guarantees or instructions to send unsolicited messages. Follow `docs/SCALE_OPERATION_GOAL.md`. Keep the daily complete-scoped-delivery workflow as the execution unit. Differentiate integration instances from distinct platform adapters; reuse a tested adapter across authorized instances instead of creating unnecessary forks.

Resolve routine engineering gaps independently using supported alternatives, and report material blockers briefly while continuing useful work. Do not repeatedly request a target URL when discovery is assigned to the agent. Do not turn this preference into permission to bypass anti-bot protections, disregard access restrictions, automate bulk unsolicited promotion, fabricate acquisition metrics or claim work runs in the background.

## Engineering operating standard

Read `docs/ENGINEERING_OPERATING_STANDARD.md`. The owner wants stronger evidence-led targeting, planning, network diagnostics, reusable techniques, testing and durable project notes. Apply explicit evidence/uncertainty labels, separate design/implementation/review passes and a reproduce -> fix -> regression-test loop. Use only available/authorized tools. Do not claim model self-upgrades, perfect memory, automatic skill installation, live capture or autonomous scheduling that has not actually been implemented.

## Evidence and delivery

The knowledge pack documents 23 source repositories and 19 archives. It is not a runnable common engine and does not prove all historical code was read or tested. Source/method references require inspection of the chosen snapshot. Preserve honest distinction between observations, owner requirements and recommendations.

Use supported/permitted integrations and synthetic/consented test data. Never publish credentials, cookies, saved sessions, private transcripts or raw capture payloads. Keep global policy, refusal/exit handling and bot disclosure explicit. Do not port credential-checking, token-harvesting, spam or bypass functionality from historical material.

End a delivery with actual commands/results, fixed defects, remaining blockers, source/ZIP and run instructions. Use `knowledge-pack/templates/SITE_DELIVERY_REPORT.md`; no feature is verified merely because a file or interface exists.

## Latest implementation boundary — v0.4

Minnit now has a **disabled-by-default single-room diagnostic connector**, not just an offline inspector. Read `control-plane/minnit.py`, its tests, README's server-only setup/staging section and `research/minnit-diagnostics-2026-10-16/REPORT.md`. Intake only queues fresh opt-in `!orbit ping`; a separate authenticated operator action sends one fixed disclosed pong. Persistent SQLite dedup/intent/outcome state never implies peer delivery. Keep the independent URL secret distinct from vendor-signature authentication. Fleet Start is still synthetic-only; other sites remain at prior evidence levels. No credentials or provider egress are configured here, and the sandbox host allowlist excludes Minnit endpoints. Do not claim a live pass or erase pending live gates based on mocks. Never package runtime data/secrets.

## Continuation workflow — owner reset

Read `PROJECT_MEMORY.md`'s ACTIVE SESSION first, then root `SITES.md`, `SKILLS.md`, `GOALS.md` and `PLAN.md`. Queue source of truth is SITES; delivery-step percentages are distinct from catalog evidence gates. Current site: DeadSimpleChat, Step 1 recon delivered; Step 2 next. Every turn code/test/push and update PROJECT_MEMORY/SITES/CHANGELOG. Never delete files. Root GOALS aliases the unchanged existing mission. No raw HAR/credentials in Git, ZIP or chat; do not claim browser HAR captures backend webhook traffic. Preserve old reports/ZIPs as historical snapshots, package new artifacts at Step 8.

Owner added sequential target locks: only the ACTIVE site may advance; all seven other targets remain locked. `site_workflow.py`/`tools/site_queue.py` enforce sequential evidenced steps and one-successor unlock after actual acceptance + ZIP/checksum. SITES embeds canonical machine state and generated table. Never pick a locked/blocked alternate to evade a missing gate. Pure offline inspectors remain regression tools; live diagnostic routes honor the project lock.

Latest owner override: FULL SCOPED PLAN → explicit owner approval → setup → verified live GREEN → next unlock/start. DeadSimpleChat DS-DIAG-v1 plan is proposed, NOT approved. Wait for owner review; do not treat this planning request as setup consent. Record approval only after explicit owner action for the exact plan hash. Setup/green/next must remain separate states; a plan or mock test is not a 100% working guarantee.

Owner now explicitly approved unchanged DS-DIAG-v1 and requested a small TXT web tester. Approval is recorded, not pending. Local Reply Lab (`/test`, `--home tester`) implements line-by-line self-testing/live LOCAL reports. Do not ask again for this local feature or call it provider-connected. Multi-line ordinary-message provider automation is not silently approved by the old one-shot plan; establish supported contracts/revised scope before any such network path. Keep seven successor sites locked; DS stays 25%, Step 3 partial.

Latest continuation: DeadSimpleChat now has explicit private `.env.local` loading (`--env-file`, allowlist, mode 600) and disabled shadow intake with registered-intent dedup. Read `deadsimplechat.py`/`server_env.py` and `research/deadsimplechat-shadow-2026-10-16/REPORT.md`. No sender exists, no provider setting/credentials were configured. Shadow URL-secret possession is not provider authenticity, and local callbacks must never advance TXT lines. Keep Step 3 partial/25%, no GREEN or successor unlock until actual live acceptance.

Latest owner dashboard override (2026-10-16): plan all forms first, remove current default dashboard, study other project dashboards. Read `docs/DASHBOARD_MASTER_PLAN.md` and `research/dashboard-review-2026-10-16/REPORT.md` before replacement UI work. Default home is now neutral read-only `planning`; old operations/tester views survive only as explicit legacy routes/modes. No final replacement operational dashboard yet. Preserve GOALS, frozen DS plan and canonical locks; exact visual preference is inferred, not confirmed. Do not restore the retired default or confuse an all-site roadmap with authorization for batch site work.

Latest dashboard approval/delivery: owner said “ok approve”, recorded in `docs/DASHBOARD_APPROVAL.json` without editing the approved master plan. Default is now original seven-page `workspace` (Home/Sites/Messages/Sessions/Live Chat/Settings/Logs), not planning or legacy UI. Reused local TXT engine, new authenticated metadata-only session index, DS-only non-secret slots/private setup/shadow controls, visible Stop. Read `research/operator-workspace-2026-10-16/REPORT.md`.159Python+55DOM+7realChromium smoke PASS; optional browser requires external tooling/binary, runtime remains stdlib. Noto Bengali font self-hosted with OFL. No provider sender/traffic, Step3partial25%/seven locked. Do not restore old default, award out-of-order steps, expand TXT provider scope, or call local/layout tests live GREEN.
