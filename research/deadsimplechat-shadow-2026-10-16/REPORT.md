# DeadSimpleChat setup and shadow intake · 2026-10-16

**Status: locally validated shadow receiver; no provider sender, live identity proof or GREEN.** Owner reconfirmed “approve”; original DS-DIAG-v1 approval remains valid and unchanged. Work continues only on DeadSimpleChat; seven later sites stay locked. This is Step 3 partial, not completed integration.

## Delivered code

- `server_env.py`: explicit `--env-file` loader. Only eight named DS/operator configuration variables, owner-only regular file mode 600, no symlink following, validated opened inode/owner/permissions, 16 KiB maximum, literal UTF-8 KEY=value, unique names, no shell execution/interpolation, no automatic loading. Validate before mutation; existing process environment wins (including intentionally empty values). Errors and return data contain no file contents/secrets.
- Root `.env.example`: empty safe placeholders/documentation only. **No actual `.env.local` or credential created/read in this turn.** API key is optional for shadow observation and is never transmitted; leave it empty until a supported sender contract is ready.
- `deadsimplechat.py`: one saved DS instance + one explicit room/bot, owner authorization assertion, independent strong operator/URL-secret checks; disabled/disarmed by default. No network library, provider sender, query-key URL construction or arbitrary message send exists.
- Protected server-to-server `/hooks/deadsimplechat/{independent-secret}` route, possession check before JSON parsing, no browser origins, no query string, existing JSON/16 KiB body guards. **A URL secret is not a vendor signature/identity proof.** This prepares an isolated shadow endpoint for authorized synthetic diagnostics; no provider setting/webhook is configured here. Real callback compatibility/authenticity must be established before live acceptance.
- Explicit operator registers an owned question + consenting user during a 15-minute shadow window. Intent lifetime up to five minutes. Fixed action ID `orbit_diagnostic_ping_v1`; match bot, room, user, action type/id and identical enclosing/parent question IDs.
- Dedup key hashes bot/room/question/user/action, not button definition ID and not run ID. SQLite unique key + serialized transaction; one registered intent can match once. Repeated callbacks update a suppression counter, not a new event/send. This does not claim per-click occurrence uniqueness.
- Tombstones survive expiry, disarm, rearm and restart; old bindings cannot be registered anew. Registered intents cancel on restart, sessions never auto-arm. 5,000-record cap fails closed rather than evicting replay protection. IDs/user text/IP/history/secrets are not persisted in the shadow ledger.
- Queue scope approval checks gate arm/register/receive. Stops always remain available. Global Stop all / queue completion / server shutdown disarm the shadow service. HTTP/operator and shadow credentials must match; factory rejects authentication-policy mismatch.
- Small dashboard adds an optional collapsed **Advanced · DeadSimpleChat setup / shadow intake** panel: sanitized blockers, arm/disarm, question/user registration, shadow counts/outcomes, always explicit “no provider replies”. TXT self-test remains independent; callbacks cannot advance its script cursor.

## Setup, without posting secrets

1. Owner creates an ignored `.env.local` outside public artifacts, using `.env.example` field names. Use independent high-entropy operator and webhook secrets, exact owned room/bot IDs and the saved DS instance ID from authenticated `/api/state`. Never copy real values into chat, issues, reports, captures or Git.
2. Keep `DS_SHADOW_ENABLED=0` / `DS_AUTHORIZED_ROOM=0` until deliberately enabling an authorized **shadow-only** test. Enabling is an operator assertion, not proof of room ownership or provider identity.
3. Set owner-only permissions (`chmod 600 .env.local`). Launch explicitly:

```sh
python -B control-plane/app.py --host 0.0.0.0 --port 8080 --home tester --db .runtime/orbit-preview.db --env-file .env.local
```

Do not prefix that private launch with the public demo's empty CONTROL_PLANE_TOKEN environment override. Process variables intentionally win over the file. Restart to pick up changes; no secret hot-reload or auto-sourcing.

4. Authenticate the small dashboard using its configured operator token. Expand Advanced: resolve named blockers, arm shadow intake, and register only your owned question/consenting user's identifiers. Private IDs are hashed in the ledger; form inputs are cleared after registration. No API key/URL secret is accepted through the dashboard.
5. For an authorized synthetic server diagnostic only, the hook path is `/hooks/deadsimplechat/{your-independent-secret}`. Do not publish the URL or log it in a reverse proxy. No HAR is requested. Browser HAR usually cannot show server-to-server callbacks. No actual provider callback URL is configured or claimed verified by this delivery.

The platform's exact extra Authorization-header requirement remains unresolved, and this sandbox's outbound allowlist does not include provider API hosts. A permitted deployment/entitlement/account and provider-compatible callback authentication must be established before live integration. There is **no env flag that enables sending or marks GREEN**, even if DS_API_KEY is present.

## API

- GET `/api/deadsimplechat/setup`: sanitized preflight, fixed live blockers, counts/latest 30 intent outcomes, no secrets/raw participant identifiers. Polling never probes the provider.
- POST `/api/deadsimplechat/shadow/arm`, `/disarm`: explicit local receiver lifecycle.
- POST `/api/deadsimplechat/shadow/register`: exactly question_id, test_user_id, current run_id. No arbitrary action/message/recipient/send fields.
- POST `/hooks/deadsimplechat/{secret}`: supported button-action shadow match only. Returns shadow_matched_no_send or shadow_ignored, never provider accepted/delivered.

## Actual tests

`python -B control-plane/tools/run_checks.py --ui`: **145 Python + 33 DOM/local-HTTP checks PASS**, both JS syntax checks PASS, source-bound receipt retained. New 13 Python checks cover private-file allowlist/literal parsing/precedence/atomic refusal/permissions/symlinks/limits, disabled/independent-secret configuration, exact scope/parent/action matching, unknown intent, duplicates/concurrency, expiry/rearm/restart/tombstones, privacy, actual local HTTP secret-before-body/browser-origin/scope guards, no TXT cursor advancement and global Stop.

The additional lab DOM assertion verifies missing-config blockers and disabled shadow controls without falsely showing provider-connected. Of 33 DOM checks, two legacy enabled-state checks explicitly inject responses; the rest use local HTTP. No real rendered browser, provider callback, request/key usage or peer-visible delivery tested. No new scope approval was invented by unit-test fixtures.

## Handoff

Do not confuse a code-complete shadow matcher or local TXT lab with an authenticated live connector. Step 3 remains partial pending provider compatibility/auth evidence; all external acceptance gates stay pending, progress 25%. API auth ambiguity, supported question-ID registration, callback identity/routing/retry behavior, entitlement/egress, actual sender and consenting witness/Stop evidence remain. Never attach the TXT engine to guessed ordinary-message events.

Single operator/process development server; production HTTPS edge, secret-aware access logs, secret management and measured security/load hardening remain required. Runtime DB/locks/private env stay out of Git/ZIP. Source push is this turn's backup; not Step 8, so all old ZIPs are preserved and no new release ZIP is claimed. Future packaging includes code/tests/report and the safe example template only; extracted-copy readiness is deferred to Step 8.

Final operational checks: restarted sample-only preview on 0.0.0.0:8080, root/test/operations HTTP 200, sanitized setup disabled with zero sends and approved queue still 25%/seven locked. Future package built/CRC-checked **in memory only**, 52 allowlisted members including new modules/tests/template/report; no private env/runtime/DB/node_modules included, no release ZIP written. Approved plan SHA and GOALS unchanged; no tracked file deleted.
