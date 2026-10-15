# Repository architecture and reusable patterns

Static review: **2026-10-15 UTC**. Start with [PROJECT_MEMORY.md](../PROJECT_MEMORY.md) for the Bangla handoff. Machine-readable source locations and hashes are in [repository-inventory.json](repository-inventory.json).

## Scope and evidence

All 23 repositories returned by `gh repo list rajuvbygyuiythh --limit 1000` were inventoried. Nineteen ZIP archives were inspected without running their contents. Root manifests, selected entry/core implementations, method declarations and source-content comparisons informed this document. This is **not an exhaustive line-by-line review, security audit or runtime certification**.

Python source was parsed with the standard-library AST parser, not imported. The scan covered 486 first-party Python file occurrences representing 173 distinct content hashes. Third-party dependency directories and generated bindings were excluded from the method scan. Go declarations were indexed textually; that is not Go type-checking. Archive hash comparison is byte-level, not an assertion that differently packaged projects behave differently.

Credential files, stored sessions, raw network/message logs, personal conversation history, large reply datasets, images and captured DOM bodies were not read. Some dependency manifests and example-independent source were read. References below identify paths **inside archives**; these paths are not extracted application files in this checkout. The original ZIP in the original `bigfih765` review checkout was not modified and is not redistributed in this knowledge pack.

## 1. Repository coverage

All names link to their GitHub repository. Detailed root-file/blob and archive hashes are in the inventory.

| Repository | Contents and review scope |
| --- | --- |
| [bigfih765](https://github.com/rajuvbygyuiythh/bigfih765) | Go/Wails root-project ZIP; selected entry/core bodies and method inventory. |
| [v2v2cc](https://github.com/rajuvbygyuiythh/v2v2cc) | Byte-identical archive to bigfih765; same source review applies. |
| [root-project-pro](https://github.com/rajuvbygyuiythh/root-project-pro) | Go diagnostic variant; hash comparison and selected live-chat diff. |
| [trynowbaby](https://github.com/rajuvbygyuiythh/trynowbaby) | Go show-mode DOM variant; entry/core inventory and hash comparison. |
| [version1cc](https://github.com/rajuvbygyuiythh/version1cc) | `root project.zip`: Go baseline; `refer project.zip`: Python EVA plus headless client/worker. |
| [wbsccapture](https://github.com/rajuvbygyuiythh/wbsccapture) | Capture ZIP, 1,022 files; filenames only, no first-party application source identified. |
| [copyhere](https://github.com/rajuvbygyuiythh/copyhere) | README and memory.txt; tree only, memory content not reviewed. |
| [chatfilehere](https://github.com/rajuvbygyuiythh/chatfilehere) | Python EVA flow/browser/GUI ZIP; selected entry/core bodies. |
| [sourcfullllchitchat](https://github.com/rajuvbygyuiythh/sourcfullllchitchat) | One JPEG asset; no application entrypoint. |
| [ygyuggo](https://github.com/rajuvbygyuiythh/ygyuggo) | Empty: no default branch. |
| [chatchat2222](https://github.com/rajuvbygyuiythh/chatchat2222) | EVA variant with WebSocket launchers; selected transport code and syntax scan. |
| [wbbbbbbbbbbsck](https://github.com/rajuvbygyuiythh/wbbbbbbbbbbsck) | JSON/text capture, auth/session and protocol evidence; tree only. |
| [cccccchhtt11](https://github.com/rajuvbygyuiythh/cccccchhtt11) | EVA/CDP/dashboard capture variant; launcher body and core method inventory. |
| [chitchtapii](https://github.com/rajuvbygyuiythh/chitchtapii) | Empty: no default branch. |
| [ccht](https://github.com/rajuvbygyuiythh/ccht) | README-only placeholder; tree only. |
| [wschitchat](https://github.com/rajuvbygyuiythh/wschitchat) | ws.txt evidence/reference; tree only. |
| [wrbb](https://github.com/rajuvbygyuiythh/wrbb) | Empty: no default branch. |
| [lastch](https://github.com/rajuvbygyuiythh/lastch) | Byte-identical EVA ZIP to chatfilehere. |
| [tgbot](https://github.com/rajuvbygyuiythh/tgbot) | Telethon Telegram application; selected entry/reply source and core method inventory. |
| [updatec](https://github.com/rajuvbygyuiythh/updatec) | EVA variant; method inventory and source comparison with chatfilehere. |
| [reddit](https://github.com/rajuvbygyuiythh/reddit) | Five account-checking ZIPs; static architecture/method/dependency inventory only. |
| [didactic-system](https://github.com/rajuvbygyuiythh/didactic-system) | Older EVA legacy RuleEngine family; wrapper body and entry/core inventory. |
| [project](https://github.com/rajuvbygyuiythh/project) | README-only placeholder; tree only. |

## 2. Go desktop/browser family

Representative: `bigfih765/root-project-proxy-diagnostics-UNVERIFIED.zip`, prefix `root-project/`.

### Entry and dependency boundaries

- `main.go:23`: resolves the data directory, initializes disk diagnostics before application startup, prepares embedded frontend assets, constructs `NewApp`, then calls `wails.Run` with startup/shutdown hooks and an app binding.
- `main.go:87`: data directory is relative to the working directory. Moving the executable or changing CWD can therefore change which runtime data is used.
- `app.go:45`: `NewApp`; `app.go:597`: `StartBot`; `app.go:675`: `StopBot`; `app.go:747`: `buildBotConfigs`.
- `cmd/chitchatbot/main.go`: separate CLI entry. `cmd/chitchatui/main.go` and `cmd/chitchatui/app.go` also exist. They are not automatically equivalent to the root dashboard implementation.
- `go.mod`: module `chitchatbot`, Go 1.25.0; Wails v2, Rod, ChromeDP, Gorilla WebSocket and Badger dependencies.
- Root `package.json`: browser-free verification tooling using Node tests, jsdom and fflate; not the desktop frontend's production dependency manifest.

### Main flow

```text
Wails frontend -> bound App method -> validated settings / worker configs
  -> one goroutine per discovered profile -> bot.Run(ctx, cfg)
  -> saved authorized session, or browser login when missing
  -> realtime listener + API work cycle
  -> response engine / persisted state / activity logs
  -> cancellation and worker completion -> UI status
```

`StartBot` protects running state with a mutex, uses a cancellation context, and waits for workers with a WaitGroup. A run identifier prevents old worker completion from clearing a newer run's state. `StopBot` requests cancellation; it is not a synchronous guarantee that every browser/process has already exited.

`internal/bot/run.go:71` validates the backend and prepares per-profile state. Its loop combines API work with realtime signals and optional matching when idle. In the inspected path, an expired saved login stops the worker rather than silently refreshing it.

### Reusable interfaces

- `internal/browser/backend.go:34`: `Backend` exposes `Name`, `Start`, `CaptureSession`, `Fetch`, `Close`; factory selects Rod or ChromeDP.
- `internal/workerplan/plan.go:40`: `DiscoverProfileWorkers`; `:91`: `AssignProfileWorkers`. Discovery and deterministic assignments are separate from launching workers.
- `internal/bot/eva_chat.go:214`: `LoadEVAChatEngine`; `:660`: `NewEVAChatSession`; `:714`: `Reply`; `:720`: `ReplyWithOptions`. Chat behavior is separate from browser lifecycle.
- `app.go` exposes settings save operations, diagnostics and initial snapshots. UI commands should use these boundaries, not bypass them.

### Distinct execution paths

Do not conflate API workers with visible DOM show mode. `live_chat.go` implements the show-mode runner; `internal/browser/domchat.go` and `showmode_dom.js` provide DOM-facing behavior. The live runner has conversation identity, seen/queued IDs and pause/rotation state. That separation matters when preventing duplicate sends or uncertain delivery.

`capture/tool/capture.cjs` composes CDP, browser lifecycle, storage, redaction and event catalogs. Its source explicitly includes DOM/storage capture capability; use synthetic fixtures or consented sessions and review redaction before sharing artifacts.

### Version findings

- bigfih765 and v2v2cc archive SHA-256 values match exactly.
- root-project-pro is not byte-identical. Comparing first-party source contents to bigfih765 found only `live_chat.go` and `live_chat_test.go` changed in that scan. Other non-code files also differ.
- The inspected live-chat diff replaces the ranged/configured reply-delay fields in bigfih765 with a single delay field in root-project-pro. A name or later upload does not establish a better baseline.
- trynowbaby has 13 source-content differences relative to the bigfih765 source hash set, including browser, app, live-chat and verification files. This is an inventory comparison, not a full semantic diff.

## 3. Python EVA browser/chat family

Representative: `chatfilehere/eva_bot_sms_detect_fixed.zip`, prefix `eva-full-project/`.

### Entry and orchestration

- `entry/main.py`: `ChitchatBotGUI`, `ApplicationController`, `main`.
- `entry/cli_runner.py:25`: `CLIRunner`; shares `entry.thread_manager.ThreadManager` with the GUI path.
- `entry/thread_manager.py:465`: `start_threads` selects runtime features. One requested worker explicitly disables the Go supervisor and context pool in the inspected implementation.
- `core/engine_bridge.py:99`: `EngineBridge` describes an optional Go subprocess supervisor using newline-delimited JSON. Its source documents safe fallback if the binary is absent. The bridge's presence does not prove the executable is shipped or operational.
- `run_chat.py:34`: offline interactive REPL, constructs `EvaFlowBot`, creates conversation state, calls `reply` and drains pending replies. This does not launch the browser automation GUI.

```text
GUI / CLI -> ThreadManager -> browser worker -> incoming-message extraction
  -> per-conversation state -> ChatRuleBot -> reply and queued extra replies
  -> transport send -> logs / UI signals
```

### Stable engine API

`chat/rule_bot.py` defaults `EVA_ENGINE` to `flow`, supports `legacy`, and falls back to flow for unknown values. The flow branch inherits `EvaFlowBot`; legacy wraps `RuleEngine`.

Common boundary:

```python
state = bot.new_conversation()
reply = bot.reply(message, state)
extra_replies = bot.get_pending_replies(state)
```

`eva_flow.py:474` creates conversation state. `:500` records replies and transcript; `:527` routes the newest input line, extracts profile facts and applies stage/share logic. Text triggers and output pools are data-driven. The source includes an underage flag/share restriction, but this limited review does **not** certify comprehensive age/consent enforcement across all response branches.

Reusable lesson: keep conversation state separate from transports and keep reply provenance (`last_picked_info`, debug reason) inspectable. For a new application, use neutral product-specific content, clear bot disclosure and explicit safety rules rather than copying a persona/funnel blindly.

### Incoming-message tracking

`browser/chat_reader.py:511` defines `MessageTracker`:

- Prefer stable message IDs; otherwise speaker plus normalized text.
- Use occurrence counts, not just set membership, for repeated identical messages.
- `snapshot` seeds a baseline; `sync` returns new items; reset at a new conversation boundary.

This is more robust than incrementing a DOM message count after sending. It is still a heuristic without IDs; DOM trimming, reordering and virtualization need fixture tests before reuse.

### Variant map

- lastch's archive is byte-identical to chatfilehere.
- updatec's source hash comparison found one changed file versus chatfilehere, `browser/browser_automation.py`; the archive also has fewer source files. This does not establish equivalent behavior.
- didactic-system uses the older `ChatRuleBot -> RuleEngine.init_conversation / decide_reply` wrapper directly, without assuming the newer flow selection.
- cccccchhtt11 adds capture/launcher components. `entry/launcher.py:51` redirects windowless startup diagnostics, catches startup failures, and restores streams in `finally`.
- `browser/cdp_capture_launcher.py` separates executable discovery, temporary profile lifecycle, process startup/readiness and cleanup. `capture.py` contains CDP metadata capture handlers. Their presence is not an assurance every capture is redacted.

## 4. Python headless/WebSocket variants

`version1cc/refer project.zip`, prefix `papipapi-main/`:

- `run_headless.py` provides the command dispatcher.
- `headless/client.py`: `HeadlessChatClient` owns transport connection, event buffering and connection status.
- `headless/worker.py:129`: `HeadlessWorker.run` consumes events and isolates dispatch errors; `:149` dispatches match/message/connection lifecycle events.
- Worker state and reply decisions are separate from the socket client. Reuse that separation for authorized event-driven integrations; do not assume captured private protocol details are a supported API contract.

`chatchat2222/eva_bot_complete.zip`, prefix `extracted_project/papipapi/`:

- `run_ws_bot.py` is another launcher; `transport/chitchat_socket.py` has a different transport abstraction.
- **Confirmed static defect:** `transport/ws_bot.py:252` contains `self.session.conversation_id = return True`. Python AST parsing reports `SyntaxError: invalid syntax`. The module cannot import as packaged. No fix was made.
- The inspected source attempts dependency installation during import when socketio is missing. Avoid this pattern in new projects: install pinned dependencies explicitly at setup time, not as an import side effect.
- The launcher prints a session-token prefix. Do not preserve that behavior: redact secrets completely, including partial tokens and sensitive exception payloads.

These variants are related, not interchangeable drop-in implementations.

## 5. Telegram family

`tgbot/eva_bot_v9_0_deepseek_only_ready.zip`, prefix `eva_bot_v9_0_deepseek_only_ready/`:

- `run.py` delegates to `asyncio.run(main.main())`.
- `main.py:594` initializes persistence/indexes, constructs the Telethon client and registers incoming-message handling.
- `main.py:101`: `handle_message`; `conversation_router.py`: first-contact routing; `database.py`: user/message state operations; `reply_engine.py`: local layered replies.
- `requirements.txt`: Telethon, RapidFuzz, Rich and python-dotenv.

```text
incoming event -> event-ID dedup + duplicate-text window
  -> per-sender asyncio.Lock -> handler timeout
  -> user/profile persistence -> local routing/reply selection -> safe send
```

The main source announces local NLU/curated DB routing and AI disabled; reply_engine explicitly describes local-only replies. **Do not infer DeepSeek use from the ZIP name.** This observation applies to the inspected source path, not every possible module or configuration.

Useful patterns: serialize messages per user, allow separate users to progress concurrently, maintain task ownership and bound handler duration. Future improvements should also bound task count/dedup maps and make shutdown cleanup explicit. These are recommendations, not verified existing guarantees.

## 6. Reddit tooling: static architecture only

The v4 archives center on `reddit_stealth_final/reddit_checker.py`. The v6 package separates a Python checker, Node/browser helper and proxy bridge. Data models, result serialization, rate-limit state and progress statistics are recognizable architectural boundaries. The v4 `(7)` and `(8)` ZIPs are byte-identical.

These packages include credential-checking and token-handling functionality. No credentials, token files or account results were opened; no account checks, authentication attempts, browser sessions or token acquisition were performed. Future reuse should be limited to generic architecture such as typed results, privacy-safe reporting and rate-limit compliance. Do not turn this into bulk login checking, token harvesting or anti-abuse bypass tooling; prefer supported APIs for accounts the user owns or is authorized to manage.

## 7. Recommended next-project blueprint

This is a proposed synthesis, **not a claim that this directory structure already exists**:

```text
app/                 # desktop, CLI or web entrypoint
core/                # lifecycle, config validation, scheduling
conversation/        # state, routing, reply policy, safety checks
transports/          # authorized API, browser or messaging adapters
storage/             # settings, conversation persistence, migrations
observability/       # structured events and secret redaction
assets/              # reviewed public templates and static resources
tests/               # offline fixtures, contracts and lifecycle tests
```

1. Decide the platform, UI, required features, authorization model and success criteria in plain language.
2. Choose one source snapshot and record its hash. Do not merge every historical ZIP.
3. Define message/state/transport interfaces; separate decisions from side effects.
4. Start with one synthetic conversation and one worker. Validate duplicate input, reset, timeout, stop/start and uncertain-send behavior offline.
5. Put age/consent/content policy before all applicable reply branches. Disclose automation and keep personal data minimal.
6. Add validated configuration and persistence; keep secrets outside source archives and redact logs before disk writes.
7. Add a thin UI over application methods, not a second implementation of business logic.
8. Add bounded concurrency, per-session serialization, timeouts, cancellation and graceful cleanup.
9. Require offline tests, dependency checks and a clean build before a small, explicitly authorized integration test.
10. Record exact commands/results and known limitations. A filename containing `verified` is not evidence that this review verified it.

Recommended regression cases: repeated identical incoming messages; DOM missing the bot's own message; conversation ID change; queued extra replies; unknown and underage user handling; refusal/consent revocation; expired authorization; reconnect; concurrent start/stop; worker cleanup; missing optional supervisor; and secret redaction.

## 8. What was deliberately not done

No application source was modified. No bot or install script was executed. No dependencies were installed. No live third-party service was contacted by these applications. No Go build, Node application test suite, browser integration test or Telegram connection was run. Only static source inspection, hashing and Python parsing support the findings above.

The notes persist in this repository, not as a promise of permanent model memory. Re-open them in later sessions and re-check source snapshots when the repositories change.
