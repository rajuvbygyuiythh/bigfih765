# Orbit control plane · v0.1.0

Runnable first milestone: a central web dashboard, SQLite-backed instance configuration and isolated synthetic worker lifecycles. **Status: OFFLINE_VALIDATED.** This is a local control-plane implementation, not a completed Minnit/DeadSimpleChat connector or acquisition operation.

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

Optional flags: `--host`, `--port`, `--db`. The database defaults to `runtime/control.db`, relative to `app.py`, not the working directory. `--port 0` selects a free port and prints the assigned port. No third-party credentials are requested or stored.

## Implemented

- Responsive fleet view, search/status filters, per-instance activity and workspace audit view.
- Create/delete configurations; server-side 100-configuration cap. **This is not a claim of 100 live platform connections or tested production capacity.**
- Start/stop synthetic workers; idempotent start, per-run identity and heartbeat; stop-all control.
- Synthetic event checks, atomic deduplication and stale-run rejection. No outbound messages or external socket connections.
- Independent instance state: stopping one instance does not stop another.
- SQLite configuration persistence. Restart restores configurations **stopped**, never auto-resumes them.
- Runtime-only logs/counters, bounded to 100 events per instance and 200 audit entries. Deduplication window: latest 1,000 unique event IDs per run. Older IDs are not a durable idempotency guarantee.
- Optional server-side operator token, same-origin mutation checks, strict JSON/body-size validation, CSP, no-store and static-file allowlist. UI renders instance names as text, not HTML.
- Minnit/DeadSimpleChat configuration entries visibly marked not connected; starting them fails closed. These are not stubbed “successful” live connections.

A single local scheduler maintains virtual worker heartbeats; workers are **not separate OS processes**, browser sessions or live platform connections. Synthetic checks do not generate chat conversations or acquisition counts.

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

Verified in the development environment: **15 Python unit/HTTP tests + 8 DOM/local-HTTP checks passed**, JS syntax passed. The Python tests exercise persistence/no-auto-resume, isolation, idempotency, duplicate/stale events, bounded memory, concurrent deduplication, lifecycle APIs, token checks, preview-origin behavior, payload rejection, and unsupported adapter refusal. A 100-config creation test is not a concurrent-load benchmark.

## API

`GET /api/info` is public and reports mode/auth requirement. Remaining routes require `Authorization: Bearer <operator token>` when configured.

| Method | Path | Input/result |
| --- | --- | --- |
| GET | `/api/state` | Fleet, counters, recent audit; acquisitions explicitly `null` |
| POST | `/api/instances` | JSON `{ "name": "Sandbox", "adapter": "simulator" }` |
| POST | `/api/instances/{id}/start` | `{}`; returns current run ID |
| POST | `/api/instances/{id}/stop` | `{}`; idempotent stop |
| POST | `/api/instances/{id}/check` | JSON `event_id` + current `run_id`; synthetic processing only |
| GET | `/api/instances/{id}/logs` | Bounded runtime-only events |
| DELETE | `/api/instances/{id}` | `{}`; must be stopped |
| POST | `/api/stop-all` | `{}`; stop every local worker |

Mutation body limit is 16 KiB; JSON objects only. Browser mutations must be same-origin. Static paths are allowlisted; there is no generic file server, proxy or webhook receiver.

## Architecture / next implementation boundary

- `app.py`: HTTP transport, request/auth/origin validation and scheduler lifecycle.
- `core.py`: SQLite config repository, atomic instance state, bounded logs, synthetic event checks.
- `static/`: dependency-free UI; no external CDN requests.
- `tests/`: core/HTTP tests and optional DOM integration.

New live adapters must supply their actual authentication, event normalization, supported inbound verification, rate/expiry handling, delivery acknowledgement and cancellation contracts. Keep secrets server-side and separate from this configuration API. Add tests and authorized delivery evidence before enabling a live start path. No private endpoints are guessed here.

## Limits

Single operator/single process; no user accounts, roles, secret manager, durable event queue, distributed workers, guaranteed delivery, campaign/outreach engine, live platform adapter or Snap integration. Python's standard-library HTTP server is a development server, not a production edge server. Add production authentication/authorization, deployment hardening and measured load tests before broader deployment. No acquisition traffic was generated. The previous research/knowledge ZIPs are unchanged.
