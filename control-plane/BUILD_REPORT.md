# First control-plane milestone — 2026-10-15

**Status: OFFLINE_VALIDATED.** Original local implementation; no historical project code copied and no third-party platform integration claimed.

## Delivered scope

Central fleet dashboard, persistent instance configurations, synthetic lifecycle controls, global stop, filtered fleet/activity view, isolated run IDs/state, local heartbeat scheduler, bounded deduplication/logs, optional operator token and API validation. Minnit/DeadSimpleChat configuration slots deliberately refuse live start.

## Executed checks

- `python -B -m unittest discover -s control-plane/tests -v`: **15 passed**.
- `node --check control-plane/static/app.js`: **passed**.
- `npm test --prefix control-plane`: **8 DOM + real local HTTP checks passed**, including token login, safe name rendering, create/start/check/log, two-instance stop isolation, global stop, filter/search, activity/delete and disabled platform start controls.
- Preview bound to `0.0.0.0:8080`; a request using a preview-style Host returned HTTP 200. Browser code uses relative URLs. Seeded preview records are synthetic, not actual connected platforms.
- Source ZIP packaging includes CRC, deterministic-build and extracted-copy test checks; see the handoff result for exact checksum.

## Important regression coverage

Atomic duplicate-event handling under 40 concurrent submissions; late-event rejection after run rotation; no automatic worker resume after database reopen; stopped-instance deletion gate; unsupported live adapter refusal; wrong token and cross-origin mutations rejected; request-size/JSON/static-path validation. Counters and logs are runtime-only and bounded.

The 100-configurations test validates an application cap, **not** concurrent platform capacity. jsdom checks execute DOM logic but do not render the design in an actual browser. No remote credentials, live messages, acquisitions, production load test or Snap API operation used.

## Run / maintenance

Use `README.md`. Entry point: `app.py`; domain logic: `core.py`; UI: `static/`; tests: `tests/`. Python runtime needs no external packages. Node/jsdom is optional test tooling only. Runtime DB, environment files and `node_modules` are excluded from source ZIP/Git.

## Next implementation gate

One supported live adapter with its real auth, verified inbound-event contract, guarded delivery/acknowledgement and cancellation; authorized two-party delivery test before enabling its start action. Production authentication/RBAC, secret management, durable queues and deployment hardening remain separate work. This milestone is not a full live-site project or an acquisition operation.
