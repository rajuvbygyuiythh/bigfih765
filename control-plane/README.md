# Orbit control plane · v0.4.0

Central web dashboard, SQLite-backed instance configuration, synthetic lifecycles and an **opt-in Minnit single-room diagnostic connector**. **Status: OFFLINE_VALIDATED; live validation pending.** Diagnostic intake and sending are implemented and locally tested, not live-connected or an acquisition operation. Fleet Start is still synthetic-only; use the separate **Minnit diagnostics** view for this narrow test flow.

## Run

Python **3.9+**, standard library only. No pip install required.

```sh
cd control-plane
python -B app.py
```

Open `http://127.0.0.1:8080` on the machine running the server. From an extracted project directory, use `python -B app.py` directly.

For Arena's preview, bind to all interfaces:

```sh
python -B app.py --host 0.0.0.0 --port 8080
```

The browser uses relative `/api/` URLs; the server accepts the preview host. No browser request targets sandbox localhost.

Default launch is an **unauthenticated synthetic demo**. Do not expose it as a production or privileged service. For operator-token protection, set `CONTROL_PLANE_TOKEN` in the server environment before starting; enter it into the dashboard's token dialog. Do not paste a production secret in chat or commit it. The token stays in browser memory (not localStorage); refresh requires login again. Use HTTPS through the deployment proxy.

Optional flags: `--host`, `--port`, `--db`. The database defaults to `runtime/control.db`, relative to `app.py`, not the working directory. `--port 0` selects a free port and prints the assigned port. Default mode needs no third-party credentials. Optional Minnit credentials are read only from the server environment, never stored in SQLite or accepted through the UI.

## Implemented

- Responsive fleet view, search/status filters, per-instance activity and workspace audit view.
- Create/delete configurations; server-side 100-configuration cap. **This is not a claim of 100 live platform connections or tested production capacity.**
- Start/stop synthetic workers; idempotent start, per-run identity and heartbeat; stop-all control.
- Synthetic event checks, atomic deduplication and stale-run rejection. Synthetic checks make no outbound messages or external socket connections; the separate diagnostic sender requires explicit setup and approval.
- Independent instance state: stopping one instance does not stop another.
- SQLite configuration persistence. Restart restores configurations **stopped**, never auto-resumes them.
- Runtime-only logs/counters, bounded to 100 events per instance and 200 audit entries. Deduplication window: latest 1,000 unique event IDs per run. Older IDs are not a durable idempotency guarantee.
- Optional server-side operator token, same-origin mutation checks, strict JSON/body-size validation, CSP, no-store and static-file allowlist. UI renders instance names as text, not HTML.
- Minnit/DeadSimpleChat configuration entries visibly marked not connected; starting them fails closed. These are not stubbed “successful” live connections.

A single local scheduler maintains virtual worker heartbeats; workers are **not separate OS processes**, browser sessions or live platform connections. Synthetic checks do not generate chat conversations or acquisition counts.

## Site research and onboarding

Open **Site research**: all nine shortlist alternatives, Chitchat and two upstream source references are tracked (**12 records**). Search/filter by site name, local contract, missing contract, restricted or reference phase. **Eight site types** accept inactive configuration; restricted/reference types reject configuration creation through UI and API. The synthetic sandbox is separate and remains the only runnable worker.

Use **Add configuration** on a research card to preselect the correct site. A saved slot has no live connection. Or create the eight baseline slots before starting the server:

```sh
python -B tools/seed_workspace.py
```

The seed utility is repeatable: it preserves existing names/configurations, creates only missing site types and starts no workers. Use `--db` to match the server's custom database path.

**Four** offline inspectors exist: Minnit message batches, DeadSimpleChat button actions, RumbleTalk REST history snapshots and Chatwee SSO results. RumbleTalk's outbound specification is a **system** message limited to 2,000 UTF-8 bytes, not private-DM parity. Chatwee returns redaction/presence flags only, never a session ID or chat message; no chat-send API is invented. No inspector sends a request to any platform.

Progress requires a passing receipt covering **that specific contract**. The four narrow implemented scopes reach **8/12 = 67% checklist completion**, not success probability or production readiness. Unknown protocols cannot borrow the shared suite's passing status. Chatzy/references show **N/A** rather than a misleading implementation percentage. Fleet live starts remain disabled; the separately guarded diagnostic path is described below.

Run and save actual test evidence:

```sh
python -B tools/run_checks.py --ui
```

Use `npm ci --ignore-scripts --no-audit --no-fund` first if jsdom is not installed, or omit `--ui` to run Python and JS-syntax checks only. The receipt at `data/test_results.json` is bound to a fingerprint of source/tests/catalog. Changed code or failed/missing proof reopens the local-test gates. The dashboard reloads catalog/receipt on its two-second refresh; it does not perform background research or automatically push to GitHub.

Current selected scopes and unresolved provider details are in `data/site_catalog.json`. In the repository, detailed reports are `research/supported-integrations-2026-10-16/REPORT.md` and `research/multiplechat-review-2026-10-16/REPORT.md`. The current ZIP includes these plus the remaining-site onboarding report under `reports/`. They are authorship/review artifacts, not source ZIP imports.

## Minnit single-room diagnostics (v0.4)

**Implemented, disabled by default.** This is not a general bot or promotion engine. It receives a fresh `!orbit ping`, stores an eligible one-shot intent, and waits for the operator to approve exactly `[Orbit diagnostic bot] pong - requested test only.`. Intake itself never sends. No arbitrary reply text, bulk approval, automatic retries or acquisition flow exists.

### Server-only configuration

Use a protected deployment environment/secret manager, outside Git and release ZIPs. The app does **not** auto-load `.env` files. Never paste values into chat, the inspector, an issue or a screenshot. Run one application process per database; use a private database directory (e.g. restrictive `umask 077`).

| Environment variable | Meaning |
| --- | --- |
| `ORBIT_MINNIT_DIAGNOSTICS=1` | Explicit feature enablement |
| `ORBIT_MINNIT_AUTHORIZED=1` | Operator asserts this is an authorized owned test room with consenting participants; not independent ownership verification |
| `CONTROL_PLANE_TOKEN` | Independent high-entropy operator token, at least 32 characters |
| `MINNIT_INSTANCE_ID` | ID of one saved Minnit configuration (from `/api/state`); not a provider room ID |
| `MINNIT_API_URL` | Dashboard-provided `https://YOUR-ORG.minnit.org/page/api`; only this documented host/path pattern is accepted |
| `MINNIT_API_KEY` | Organization API key for the authorized account; header only, never in a URL |
| `MINNIT_WEBHOOK_SECRET` | Independent cryptographically random URL-safe secret, 32–128 characters; never reuse either other credential |
| `MINNIT_CHAT_ID` / `MINNIT_CHAT_NAME` | Exact stable provider room ID and current room name; both checked on incoming messages |
| `MINNIT_WEBHOOK_CHANNEL` | Exact incoming channel value, within the documented-subset ID syntax |
| `MINNIT_SEND_CHANNEL` | Explicit outgoing channel value; do not assume an inbound numeric value maps to an outbound name |
| `MINNIT_USERNAME` | Your authorized disclosed diagnostic-bot account username, not an impersonated participant |

Generate high-entropy secrets on the deployment host using a secure generator (Python `secrets.token_urlsafe(32)` is suitable), not predictable sample strings. Required plan/access: official docs identify organization API and custom webhooks as paid-plan features; confirm current entitlement in the dashboard before purchasing or enabling anything.

Restart the server after setting environment variables. In the provider's owned-room settings, set the message webhook URL to `https://YOUR-DEPLOYMENT/hooks/minnit/YOUR-WEBHOOK-SECRET`. Register it for this room only. **This URL-secret check authenticates possession, not Minnit's cryptographic identity.** No documented signature is assumed. Use HTTPS, suppress/redact hook paths in reverse-proxy/CDN access logs, and keep the secret out of analytics/referrers. The Python server does not log request URLs, bodies or headers. This sandbox's outbound host allowlist does not include Minnit organization endpoints: live validation needs an authorized deployment with provider HTTPS egress and a publicly reachable HTTPS callback. No network-policy bypass is implemented.

### Controlled staging procedure

1. Open **Minnit diagnostics**; resolve the displayed environment/binding blockers. The UI never receives keys or the webhook URL. A saved fleet slot alone cannot send.
2. Arm a 15-minute test window. On a consenting test account in the configured room/channel, send `!orbit ping`.
3. Confirm a `pending` ledger item appears. Wrong room/name/channel batches reject atomically. Noncommands/edits/joins and commands older than five minutes or more than 30 seconds in the future are not eligible.
4. Click **Approve fixed pong**, read the confirmation and approve. Every send needs a fresh operator action and current run ID. The server enforces one attempt per event, a five-minute command age and at least 30 seconds between attempts. These are local safety policies, not verified vendor quotas.
5. Inspect `api_accepted`, `rejected` or `unknown` plus HTTP status. The official API example uses HTTP 200 with JSON `success:true`; only that is API acceptance. Unexpected/redirect/5xx/timeout responses are conservatively unknown. Raw bodies are never persisted/exposed. **Peer delivery remains unverified**, including after API acceptance; a consenting witness must check the actual room. No automated witness claim exists.
6. Disarm, use **Stop all**, or Stop/Delete the bound fleet slot. All cancel pending intents and invalidate the run. Stop serializes behind any already-dispatched attempt: it cannot recall a message. The sender has a five-second **per-socket-I/O** timeout and a 4 KiB body cap, not a hard wall-clock deadline; slow/trickling responses can delay Stop. This needs production transport hardening before broader deployment.
7. Restart: intake is disarmed; old pending work becomes `cancelled`, interrupted `submitting` becomes `unknown`. Replayed event IDs stay suppressed. Do not retry uncertain outcomes; request a new consenting test command only after checking the room.

SQLite retains only hashed event identity (organization/room/channel/message ID), instance/run/delivery IDs, timestamps, state and HTTP code. No text, sender identity, profile, IP, key or raw response is retained. Latest 50 records are shown; the durable ledger caps at 10,000 and fails closed rather than evicting replay protection. Database loss, rollback to an old backup, manual deletion or parallel deployments are not an exactly-once guarantee. For a private backup: first disarm, stop the server, then use SQLite's backup facility or copy the closed DB to protected storage; **never commit or ZIP runtime data**. Before destructive rotation, stop callbacks, settle uncertain outcomes and rotate the webhook secret. No automated retention deletion/compaction is supplied.

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/api/diagnostics/minnit` | Sanitized configuration blockers, armed/run/expiry and policies |
| POST | `/api/diagnostics/minnit/arm` | `{}`; validate and arm, no network request |
| POST | `/api/diagnostics/minnit/disarm` | `{}`; invalidate run and cancel pending intents |
| GET | `/api/diagnostics/minnit/deliveries` | Latest 50 sanitized durable outcomes; no raw payloads |
| POST | `/api/diagnostics/minnit/deliveries/{id}/approve` | Only `{ "run_id": "CURRENT-RUN" }`; one synchronous fixed-message attempt |
| POST | `/hooks/minnit/{independent-secret}` | Server-to-server JSON, 16 KiB maximum; authenticate before parsing; queue only |

Local acceptance covers restart/replay, concurrent duplicate intake/approval, persisted-before-network intent, wrong-scope atomic rejection, age/run/arm/cooldown guards, Stop serialization, crash outcomes, secret redaction and mocked form/header/ACK/error transport. It **does not prove** provider callback delivery/retry/Content-Type compatibility, channel routing, actual authorization/entitlement, live network behavior or peer-visible delivery. The four remaining live evidence gates stay pending (8/12 checklist, not success probability).

## Try it

1. Click **New instance**, select **Synthetic sandbox**, and save a name.
2. Click **Start**, then **Run check**. Inspect the selected instance's activity.
3. Create/start a second sandbox. Stop the first and verify the second remains running.
4. Use **Stop all**. Delete a stopped instance.
5. Optionally save a Minnit entry and confirm it cannot start. This prevents confusing local readiness with an implemented connector.

## Tests

From this directory:

```sh
python -B -m unittest discover -s tests -v
node --check static/app.js
```

Optional DOM + local HTTP integration tests require Node **18+**:

```sh
npm ci --ignore-scripts --no-audit --no-fund
npm test
```

Node/jsdom is a **test-only** dependency; the app itself requires no npm packages. The pinned version and transitive dependencies are in `package-lock.json`. `tests/ui.test.cjs` starts a temporary authenticated local server and closes it afterwards. It tests DOM interactions against real local HTTP endpoints, **not real-browser layout/rendering or third-party chat**.

Verified in the development environment: **87 Python unit/HTTP/contract/research/diagnostic tests + 20 DOM checks passed** (18 against local HTTP, two additional UI-only injected-response checks), JS syntax passed. The Python tests exercise persistence/no-auto-resume, isolation, idempotency, duplicate/stale events, bounded memory, concurrent deduplication, lifecycle APIs, token checks, preview-origin behavior, payload rejection, and unsupported adapter refusal. A 100-config creation test is not a concurrent-load benchmark.

## API

`GET /api/info` is public and reports mode/auth requirement. Operator API routes require `Authorization: Bearer <operator token>` when configured.

| Method | Path | Input/result |
| --- | --- | --- |
| GET | `/api/state` | Fleet, counters, recent audit; acquisitions explicitly `null` |
| POST | `/api/instances` | JSON `{ "name": "Sandbox", "adapter": "simulator" }` |
| POST | `/api/instances/{id}/start` | `{}`; returns current run ID |
| POST | `/api/instances/{id}/stop` | `{}`; idempotent stop |
| POST | `/api/instances/{id}/check` | JSON `event_id` + current `run_id`; synthetic processing only |
| GET | `/api/instances/{id}/logs` | Bounded runtime-only events |
| DELETE | `/api/instances/{id}` | `{}`; must be stopped |
| POST | `/api/stop-all` | `{}`; stop synthetic workers and disarm diagnostic intake |
| GET | `/api/platforms` | Shared UI/backend capability registry; zero live-ready connectors |
| GET | `/api/research` | Source-backed catalog, derived gates and test-receipt freshness |
| GET | `/api/contracts` | Synthetic fixtures; offline mode |
| POST | `/api/contracts/{platform}/inspect` | `payload` + `expected_room_id`; normalize locally, zero external requests |
| POST | `/api/contracts/{platform}/describe-send` | Secret-free shape specification only, `transmitted: false` |

Mutation body limit is 16 KiB; JSON objects only. Browser mutations must be same-origin. Static paths are allowlisted; there is no generic file server or proxy. Only the dedicated shared-secret diagnostic webhook bypasses operator Bearer authentication, using its own independent secret; it rejects browser-origin requests.

## Architecture / next implementation boundary

- `app.py`: HTTP transport, request/auth/origin validation and scheduler lifecycle.
- `minnit.py`: narrow diagnostic intake, SQLite idempotency/ledger, operator-approved HTTPS transport and lifecycle guards.
- `core.py`: SQLite config repository, atomic instance state, bounded logs, synthetic event checks.
- `static/`: dependency-free UI; no external CDN requests.
- `platforms.py`: canonical capability/configuration/reference registry.
- `workspace.py`, `tools/seed_workspace.py`: repeatable inactive-slot bootstrap.
- `contracts.py`: four pure offline inspectors/specifications; no network I/O.
- `research.py`, `data/`: evidence catalog and source-bound test receipt.
- `tools/run_checks.py`: real-test runner/receipt writer.
- `tests/`: core/HTTP/contract/research tests and optional DOM integration.

New live adapters must supply their actual authentication, event normalization, supported inbound verification, rate/expiry handling, delivery acknowledgement and cancellation contracts. Keep secrets server-side and separate from this configuration API. Add tests and authorized delivery evidence before enabling a live start path. No private endpoints are guessed here.

## Rebuild a backup

After running the checks:

```sh
python -B tools/package_release.py
```

The explicit allowlist packages source, tests, catalog/receipt and authored reports with a SHA-256 manifest. It excludes DB/session/credential files, dependency directories and upstream ZIPs. The same script rebuilds from an extracted release using `reports/`. An unchanged input snapshot produces identical archive bytes.

## Limits

Single operator/single process; no user accounts, roles, managed secret store, general-purpose queue, distributed workers, guaranteed delivery, campaign/outreach engine, validated production adapter or Snap integration. The narrow diagnostic queue/ledger is durable, but never auto-drains and does not offer exactly-once recipient delivery. Python's standard-library HTTP server is a development server, not a production edge server. Add production authentication/authorization, deployment hardening and measured load tests before broader deployment. No acquisition traffic was generated. The previous research/knowledge ZIPs are unchanged.

## Current working step: DeadSimpleChat Recon

The released v0.4.0 archive remains unchanged. The next-site workspace adds an offline recon CLI and **11 synthetic tests** (full current suite: **98 Python + 20 DOM checks PASS**); no DeadSimpleChat live send is enabled. Queue/resume: repository-root `SITES.md`, `PROJECT_MEMORY.md`, `PLAN.md`.

```sh
python -B tools/recon_site.py deadsimplechat
# Optional authorized private trace; never commit/upload raw HAR:
python -B tools/recon_site.py deadsimplechat --har runtime/authorized.har
```

Only fixed metadata for the documented bot-send route is exported; request/response bodies, credentials, cookies and IDs are not retained. This tool performs no network requests. Browser HAR normally cannot contain backend bot-send calls or incoming server-to-server webhooks. Header presence cannot resolve the documented auth-header ambiguity, and HTTP 200 alone is not API acceptance/peer delivery. No capture is requested until the next step establishes exactly what evidence is needed. Raw HAR and `.env.local` are ignored; `.env.local` is not automatically sourced. Details: `research/deadsimplechat-recon-2026-10-16/REPORT.md` in the repository (included in the next Step 8 package as `reports/DEADSIMPLECHAT_RECON.md`).

## Locked target queue — one site at a time

Open **Locked site queue**. **DeadSimpleChat is the only active/unlocked target; seven remaining targets are locked.** Order: DeadSimpleChat → Minnit → RumbleTalk → Chatwee → Chatblink → StrangerMeetup → Chatango → Chatiw. Four restricted/reference records remain outside the unlock sequence. Existing offline inspectors, research and inactive configuration slots are not deleted; unlocking a project is not authorization to run a live connector.

`SITES.md` is the canonical queue, containing a machine-readable block and its generated table. No second database/list competes with it. Restart retains locks and the current site. Do not edit just the display table. Only the active site may record its next sequential delivery step:

```sh
python -B tools/site_queue.py status
# Agent records a genuinely completed step, with the current revision:
python -B tools/site_queue.py complete-step --site deadsimplechat --step 2 --revision 0 --evidence research/YOUR-REPORT/REPORT.md
# Only after all acceptance/step/release checks pass:
python -B tools/site_queue.py complete-and-next --site deadsimplechat --revision CURRENT_REVISION
```

There is **no unlock-all/skip/force override**. Complete-and-next atomically marks the active site DONE and unlocks exactly one successor. It requires all eight evidenced steps, all twelve site-specific acceptance gates, fresh source-bound passing tests and a valid Step 8 ZIP with matching `.zip.sha256`. Steps 6–8 cannot be awarded while live acceptance remains incomplete. Percentages alone never unlock anything. Blocked access means remain on this site, not falsely mark it complete. The owner/agent must supply honest evidence; a filesystem owner can of course edit repository files, so this is a workflow guard, not a security boundary against the repository owner.

Read API: `GET /api/workflow`. Operator completion API: `POST /api/workflow/complete-and-next` with **only** `site` + current integer `revision`, existing Bearer/same-origin/body checks and an operator token of at least 32 characters. Default demo is read-only for queue mutation. Dashboard's **Complete site & unlock next** stays disabled until ready. No public step-write API is exposed. CLI/API updates use a POSIX advisory lock, atomic replacement and revision checks; mutation requires POSIX. Read-only views remain portable. Runtime lock file is ignored. Git backup still requires the agent's explicit tested commit/push, never an automatic server push.

Minnit webhook/arming/approval routes also enforce its project lock; real send dispatch holds the same queue lock as advancement. Completion cannot race an already-dispatched diagnostic send. Operator disarm/Stop remain available even while a site is locked. Previously released ZIPs remain unchanged; the next Step 8 packager includes queue module/tool/tests and SITES as `reports/SITE_WORKFLOW.md`. Packaged queue is a snapshot; active development/step evidence should be managed in the source checkout.
