# Owner-approved local TXT reply dashboard · 2026-10-16

## Owner decision and boundary

Owner explicitly said “ok approve” and requested a small web dashboard for self-testing: upload one TXT file and advance through reply lines after each user message, with a live report. Recorded explicit approval of **unchanged DS-DIAG-v1**, SHA-256 `dc8a906cd04c6293c54d347f1a910767202a890f8dbbc45b9206c1a80edb01f8`, in canonical SITES with non-secret owner-chat reference. No inferred approval, hidden purchase or credential entry.

The additional request directly authorizes the **local self-test dashboard** built here. It does not silently replace the approved provider scope: DS-DIAG-v1 remains a one-shot fixed-response provider diagnostic. The TXT conversation flow has **no provider transport/callback/outbound request path**. Extending it to ordinary DeadSimpleChat user messages requires verified supported event/identity/auth/delivery contracts and a revised provider plan, not guessing missing schemas or silently treating repeated clicks as messages. No irrelevant HAR or secret values requested.

## What the owner can test now

Open `/test`, or launch `app.py --home tester` for a dedicated small homepage.

1. Select a UTF-8 `.txt` file (up to 8 KiB). Each non-empty line becomes a reply; blank lines are skipped, CRLF/BOM supported. At most 200 lines / 1,000 characters per line. Nothing replies on upload.
2. Click **Start test**. Nothing auto-sends at start either.
3. Type a user message and Send/Enter. It returns **line 1 only**. Type another message: line 2 only. Shift+Enter adds a user-input newline.
4. At the last line, local script completes and Send disables. No wraparound/automatic loop.
5. Stop prevents new local messages. Resume continues from the cursor with a fresh run. Reset explicitly returns to line 1 and stays stopped/ready until Start.
6. View live local report (one-second polling): line count, generated/remaining replies, run, duplicate suppression and recent local events. External messages remain zero; provider disconnected; peer delivery not tested.

A three-line sample is available so a file is not necessary for the first UI smoke test. Real TXT upload is also exercised in DOM/local HTTP tests, not just a mocked uploader. This is a functional local conversation tester, **not completed DeadSimpleChat integration or site GREEN**. The seven later targets remain locked.

## Implementation and data boundaries

- `reply_tester.py`: SQLite-backed script/cursor/run/event state shared with Controller lock. One user input consumes exactly one line. Same event+same input retry returns the same reply, even after the last line, without advancing again. Same event with different input rejects. Distinct legitimate repeated text consumes successive lines.
- Commit cursor and event atomically with a SQLite write transaction. Report labels this honestly as **local reply generated**, not recipient delivery. Restart restores scripts/cursor but disarms waiting sessions. Stop/reset invalidate old runs.
- Per-session random IDs, independent scripts/cursors, maximum 50 stored sessions / 1,000 events per session. No automatic eviction; capacity fails closed. Single application process/operator, not a distributed/live scale claim.
- Reply templates are stored only in ignored runtime SQLite; uploading filenames and plaintext user input are not stored. Input digest is retained solely to reject conflicting idempotency keys. Reports expose neither input digest nor user messages. Chat bubbles are tab-local; sessionStorage keeps only the random local session ID. Operator token is memory-only; login supports restoration afterwards.
- Every script/message is rendered with textContent; HTML-looking lines are literal, never executable. UTF-8/line/control/body limits apply. No dependency/runtime package added.
- Existing Bearer/same-origin/JSON/body/CSP/static-allowlist guards reused. Queue approval/active-site checks gate create/start/message under the queue lock. Stop/reset/report remain usable when a site is locked. Global Stop all also stops local testers.
- Default public preview is an unauthenticated **synthetic/sample-only demo**, not private hosting. Do not upload secrets, personal transcripts or real private data. For private use configure operator token + HTTPS and restrict access. Keep runtime DB and session IDs private; never commit/archive them. The server does not log URLs/headers/bodies; reverse-proxy logs require redaction/private deployment controls.

## Acceptance evidence

`python -B control-plane/tools/run_checks.py --ui`:

- **132 Python tests PASS** (13 new reply-tester domain/HTTP cases).
- **32 DOM/local-HTTP checks PASS**: existing operations 23 plus nine dedicated lab checks. Two legacy enabled-diagnostic UI checks use explicit injected responses; the nine lab checks use actual local HTTP including a FileReader UTF-8 TXT upload, no provider mock masquerading as live delivery.
- Both JavaScript entrypoint syntax checks PASS; source-bound receipt saved.

New tests cover first/no-automatic reply, ordered one-per-user progression, EOF, UTF-8/BOM/CRLF/blank lines, upload/content bounds, literal HTML, duplicate/conflicting-input/concurrent idempotency, legitimate repeated text, stop/resume/reset and stale runs, restart-disarmed persistence, session isolation, absence of raw user input/filename in DB/report, auth/origin/changed-plan blocking, home/static routes, one-second report updates and invalid-file rejection. Not a rendered-browser layout test, provider request, security audit or measured production load test.

## Reproduce / handoff

```sh
python -B control-plane/app.py --host 0.0.0.0 --port 8080 --home tester --db .runtime/orbit-preview.db
# / is the small tester; /operations retains the full queue dashboard.
# Default operations launch also serves the tester at /test.
```

API: POST `/api/reply-test/sessions` with `script`; GET `/api/reply-test/sessions/{id}`; POST `/{start|stop|reset}`; POST `/message` with `text`, `event_id`, current `run_id`. All route suffixes are below the same session path. IDs/run fields come from responses, not guessed. No API accepts a provider key, URL, arbitrary recipient or real send action.

Approved plan setup/prototype work started; DeadSimpleChat delivery remains **2/8 = 25%**, Step 3 partial. Do not award Step 3 secure provider intake or Step 4/5 whole connector completion for this local UI. Still required: authorized account/entitlement, exact provider auth/callback/identity, provider-egress deployment, live consenting witness/Stop tests, actual release acceptance. No next-site unlock.

Source/Git push is this turn's backup. This is not Step 8, so old ZIPs are preserved and no new release ZIP is claimed. Future packaging allowlist includes the new module/assets/tests/report; portable packaged workflow/live setup still needs Step 8 extracted-copy validation.
