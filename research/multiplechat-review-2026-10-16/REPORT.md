# multiplechat — source review and integration findings

Source: [sff96918-byte/multiplechat](https://github.com/sff96918-byte/multiplechat/tree/c24e1f94174b458860f0a16c4725adc59a6fe40e), pinned commit **c24e1f94174b458860f0a16c4725adc59a6fe40e**. Static review date: 2026-10-16. No upstream code executed or copied into the application.

## Coverage — exact, not “all files read”

The root contains two ZIPs, not an unpacked application:

| Archive | Files (not directories) | SHA-256 |
| --- | ---: | --- |
| capture_tool.zip | 676 | `8a24fbb29917fe73385a10c43a934c10893d98c53f0e5c31e5925a4b2447045f` |
| multi-site-bot.zip | 64 | `5600f8eb5db938e3a52cf34dcdd8e4a469efdc46580fdfc95bc6497cfdf6b002` |

- **740/740 file entries inventoried**, with sizes and review classifications in `inventory.json`; both archive CRC checks passed.
- **26/26 Python source files loaded and syntax-parsed**, including scripts/tests, with declaration names and line ranges inventoried. This is not semantic correctness or a complete manual reading of every method.
- Detailed method-body review concentrated on **seven files**: `src/main.py`, `sites/joingy.py`, `sites/isexychat.py`, `src/db_reply_engine.py`, `src/thread_manager.py`, `src/fixed_sms_engine.py`, `src/debug_utils.py` (selected entrypoint/lifecycle/send/state/debug methods).
- Browser profile, cookie/token files, databases, captures, DOM snapshots, messages, screenshots and compiled files were **metadata-only**, not parsed for contents or republished. Other documentation/config entries were inventoried, not represented as fully reviewed. The user's earlier “all files” request is therefore not falsely marked complete.
- No root LICENSE and no LICENSE entry in the archive inventory were found. Public visibility is not permission to redistribute the source. We implement original, documented contracts instead of importing its ZIPs/modules.

## Observed system flow

`src/main.py` creates a shared reply engine, SQLite-backed services, fixed-template service, debug/health utilities and a **Textual CLI dashboard**, not a browser control plane. `main.py:138–169` wires two concrete runtime site branches: Joingy (HTTP transport) and Isexychat (Playwright transport). Other capture filenames do not constitute implemented site adapters.

Each site class starts sessions with its own loop/task map, exposes start/stop/stats/update_config, and has cleanup/health behavior. These are useful interface boundaries, but not a plug-and-play licensed adapter for the current dashboard. Source presence does not establish current service compatibility or authorization.

## Concrete findings and effect on our implementation

| Finding | Source evidence inside multi-site-bot.zip | Consequence / original implementation response |
| --- | --- | --- |
| “Snap lead” is counted when outgoing content contains the configured username | `sites/joingy.py:272–285`; `sites/isexychat.py:273–284` | This measures a share/send event, **not a verified acquisition/add**. Our acquisition metric stays unknown. |
| DOM send count advances after pressing Enter | `sites/isexychat.py:265–286` | No recipient-side ACK is established. Our contracts separate API acceptance from peer confirmation. |
| Fixed-template position advances before transport outcome | `src/fixed_sms_engine.py:142–146` plus site reply/send callers | Failed/unknown sends can consume sequence state. Future delivery state must commit on a defined outcome, not generation alone. |
| DOM dedup uses nickname + text | `sites/isexychat.py:216–233` | Legitimate repeated text can be dropped. Our fixture tests preserve different event IDs with equal text. |
| Stop cancels tasks without awaiting a gathered completion barrier | `sites/joingy.py:414–421`; `sites/isexychat.py:394–401` | Do not assume cancel means resources are closed. Preserve explicit run boundaries and test shutdown before real adapters. |
| Health loop uses `session` from the preceding iteration instead of popped `sess` | `sites/isexychat.py:378–390` | Static variable-reference defect in the dead-session path; not runtime-reproduced here. Avoid porting this lifecycle implementation. |
| Semaphore release is not conditional on a recorded successful acquisition | `src/thread_manager.py:112–136`; acquire bookkeeping `80–108` | Repeated/invalid release can inflate an ordinary Semaphore; cancellation while waiting needs cleanup. This is a static failure-mode analysis, not an upstream runtime test. |
| Scoped DB cache wraps an underlying engine keyed only by conversation ID | `src/db_reply_engine.py:59–78`, `100–118` | Site-identical conversation IDs can share non-restored engine state (e.g. used-line sets). Scope all identities by instance/site as well as conversation. |
| DB reply/thread services initialize but the inspected bot constructors receive the base reply engine, not those services | `src/main.py:107–135`, `158–165`, `174–175` | A service existing in a dashboard does not prove it governs worker execution/persistence. Do not claim a semaphore or DB wrapper is enforced merely because initialized. |
| Debug dump exports recent trace/log/session state | `src/debug_utils.py:566–602` | A future export must redact before persistence; do not commit raw dump/capture contents. |

These findings are **static observations/inferences**, not a claim all upstream defects have been enumerated or fixed. No upstream tests, installs, browser launch, network session or site automation were run.

## What can be added to our project

Reuse architecture concepts, not unlicensed code or captured sessions:

1. Common lifecycle contract (start/stop/stats/config), isolated by instance/run ID.
2. Normalized event interface separated from reply generation and transport.
3. Explicit per-site research evidence, missing gates and source-bound tests.
4. Bounded diagnostics with no stored credentials/transcripts.
5. Accepted/failed/unknown delivery tracking; no share-count-to-acquisition shortcut.

Implemented in the current milestone: source/evidence inventory, supported Minnit/DeadSimpleChat local contract checks, dashboard research view, and receipt-derived progress. Joingy/Isexychat private transports, adult/funnel content, proxy rotation and capture/profile data were **not imported**. A new live site requires a supported/authorized integration and current acceptance evidence; those conditions are not supplied by the archive.

## Backup boundaries

Back up this authored report and inventory, our original code, test receipt and sanitized fixtures. **Do not** back up the source ZIPs, browser profile, raw captures, token/cookie values, existing SQLite data or actual user transcripts into our Git repository/ZIP. The pinned source URL and archive hashes preserve reproducible provenance without republishing sensitive material.
