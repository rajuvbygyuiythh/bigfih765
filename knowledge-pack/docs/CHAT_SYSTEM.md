# Chat system: observed logic and future design

Read together with `PROJECT_PATTERNS.md`. **Observed** means visible in selected source at the recorded snapshot, not proven at runtime. **Recommended** means proposed for the next build, not already implemented everywhere.

## 1. The important separation

A chat system is not just a function that chooses a line:

```text
transport receives site/platform event
 -> normalize identity, conversation ID, message ID, author and timestamp
 -> reject duplicates / irrelevant events
 -> load the correct conversation state
 -> evaluate global policy and stop conditions
 -> route to a reply category / stage / engine
 -> choose reply + optional extra messages
 -> validate and deliver through the transport
 -> record confirmed outcome, updated state and redacted diagnostics
```

Existing families implement different portions of this pipeline. Some mutate state at reply-selection time, before transport acknowledgement. A future design must distinguish **generated**, **queued**, **sent**, **confirmed** and **unknown** delivery outcomes.

## 2. Python EVA public interface — observed

Representative archive: `chatfilehere/eva_bot_sms_detect_fixed.zip`.

```python
from chat.rule_bot import ChatRuleBot
bot = ChatRuleBot()
state = bot.new_conversation()
reply = bot.reply(message, state)
extra_replies = bot.get_pending_replies(state)
```

This is an interface illustration, not runnable code in this knowledge-only repository. The source API mutates `state`. `run_chat.py` is an offline REPL using the same flow engine. The GUI/browser integration sends the resulting messages separately.

`chat/rule_bot.py` selects `flow` by default via `EVA_ENGINE`. `legacy` wraps `RuleEngine.init_conversation()` / `decide_reply()`; the newer flow implementation inherits `EvaFlowBot`. Keeping the wrapper API stable lets GUI/CLI/transport code avoid knowing the engine's internals.

## 3. Conversation state — observed

`eva_flow.py:474` initializes a dictionary with these groups:

| State group | Representative fields | Meaning |
| --- | --- | --- |
| Stage | `stage`, `flirty_state`, `sequence_step`, `flow_type` | Current routing stage and legacy/display compatibility. |
| Extracted facts | `user_age`, `user_gender`, `user_country` | Facts parsed from user text; not verified identity. |
| Gating | `blocked`, `asked_snap`, `ask_next`, `snap_pivoted`, `snap_nudges` | Historical share/ask/stop control flags. |
| Progress | `misses`, `bot_reply_count` | Stage fallback progress and response count. |
| Anti-repeat | `io_used`, `pools_used`, `last_bot_pool` | Previously selected categories/lines. |
| Memory | `user_messages`, `bot_messages`, `transcript` | Conversation history in memory. |
| Multi-message output | `pending_replies` | Extra selected replies to drain after the main reply. |

Facts extracted by regex are uncertain. Do not treat a parsed age as identity verification. History here also creates a data-retention concern; persistence and retention need explicit product decisions.

## 4. State machine — observed

Historical Python flow:

```text
NEW
 ├─ age/gender input or category -> WAIT_COUNTRY
 ├─ country question            -> WAIT_COUNTRY
 └─ otherwise greeting          -> WAIT_AGE_GENDER

WAIT_AGE_GENDER
 ├─ age/gender captured          -> WAIT_COUNTRY
 ├─ country question            -> WAIT_COUNTRY
 └─ category/fallback attempts  -> eventually WAIT_COUNTRY

WAIT_COUNTRY
 ├─ country answer              -> MIDDLE
 ├─ country question            -> category response, usually stay
 └─ other/fallback input        -> eventually MIDDLE

MIDDLE
 ├─ category match              -> category response
 ├─ no match                    -> fallback question pool
 ├─ response cap / repeated exit-> END
 └─ top-level terminal routing  -> END

END -> closing reply in the inspected engine
```

References: `_stage_first_sms:706`, `_stage_wait_age_gender:728`, `_stage_wait_country:775`, `_stage_middle:813`.

The diagram is simplified. Global routing runs **before** stage routing, so not every turn passes through every stage. A production transport should generally cease replying when the conversation is closed; the engine's END branch returning a closer is not itself a delivery stop guarantee.

## 5. Router priority — observed, not a recommended safety policy

In `eva_flow.py:_reply_core` the inspected order is:

1. Strip empty lines and let the **last** input line drive routing.
2. Clear old pending extras and append the input to in-memory history.
3. Extract profile facts and mark an underage `blocked` flag if applicable.
4. If already END, return a closing response.
5. Check terminal/share routing, apply the share block and move to END.
6. Check a historical adult-question category; prepare a main reply plus one queued extra.
7. If `ask_next` is set, issue the historical ask response.
8. Handle negative responses after an ask; inspected legacy behavior has one retry before END.
9. Dispatch by stage.

**Important limitation:** the inspected flag restricts a share branch, but adult-category routing is elsewhere. This review does not establish a universal age/content gate. The pending-ask branch can run regardless of input meaning, and the legacy refusal path can nudge after a refusal. These are historical observations, **not approved design defaults**. For a future build, global safety/consent/exit checks must take priority and a refusal should be respected immediately.

Do not copy historical intimate content, persuasive funnel rules or persona claims into an unrelated site. Use neutral application-specific responses and disclose automated interaction.

## 6. Trigger matching and response pools — observed

- `data/input/` categories provide trigger phrases.
- `data/output/` categories provide response pools.
- `TriggerMatcher` normalizes/matches triggers; category scan order affects which response wins.
- `_pick:935` applies pool-level and line-level no-repeat logic and resolves supported placeholders.
- Non-repeatable spent pools are redirected to a fallback pool in the inspected implementation.
- A line is avoided until exhaustion; immediate repeated selection is avoided when alternatives exist.
- Missing pools use a short fallback response rather than raising in that path.
- Debug metadata records the selected file/line and routing reason.

For a new app: define category priority explicitly, use deterministic seeded tests, validate placeholders before delivery, and decide whether a missing required pool should fail closed instead of producing a generic message.

## 7. Incoming-message deduplication — observed

`browser/chat_reader.py:MessageTracker` uses a stable message ID when available; otherwise speaker + normalized text. A Counter tracks repeated occurrences so two identical legitimate incoming messages can both be processed. `snapshot` initializes a baseline, `sync` computes new items, and `reset` starts fresh.

This avoids the old assumption “increment a message count after sending.” It does not prove correctness under every DOM reorder, virtualization or trimming scenario. Test those situations separately.

The Go live runner additionally tracks conversation identity, seen IDs, queued IDs and pause/rotation state. The Telegram path uses event-ID dedup plus a duplicate-text time window, then a per-user lock.

## 8. Other implementations — observed

### Go EVA and desktop

`internal/bot/eva_chat.go` has a separately implemented engine: `LoadEVAChatEngine`, `NewEVAChatSession`, `Reply`, `ReplyWithOptions`. Browser/API lifecycle stays outside it. The Go implementation includes its own reply options such as configured usernames; do not assume exact parity with the Python engine just because concepts are similar.

### Python headless variant

In `version1cc/refer project.zip`, `HeadlessChatClient` owns the socket/event queue. `HeadlessWorker.run` dispatches normalized event dictionaries into match/message lifecycle handlers. Transport reconnection and conversation resets must remain distinct concerns.

### Telegram

`tgbot/main.py` handles Telethon events, maintains user history, serializes a sender's work with an asyncio lock, and invokes local routing/reply logic. The inspected entry flow is local-only despite the archive name. Adding an LLM would be a new requirement, not a discovered dependency of the active reply path.

## 9. Recommended neutral contract for a new project

The following is **proposed**, not an existing class copied from the source:

```text
IncomingMessage:
  platform, conversation_id, message_id, author_id, text, received_at

ConversationState:
  version, conversation_id, status, facts, consent, history_window,
  processed_message_ids, used_reply_ids, pending_deliveries

ReplyDecision:
  allowed, reason_code, next_state, messages,
  provenance(category/template/version), should_close

DeliveryResult:
  delivery_id, outcome(confirmed|failed|unknown), remote_message_id
```

Recommended interfaces:

```text
Transport.receive() / send() / close()
Engine.decide(message, state, policy) -> ReplyDecision
Store.load(conversation_id) / save(state) / record_delivery(result)
Lifecycle.start() / stop_and_wait()
```

Keep unknown delivery outcomes from causing blind retries. Store only the minimal conversation history needed. For a rules/LLM hybrid, the same policy and delivery gates must apply to both reply paths.

## 10. Required offline scenarios before site integration

1. Greeting with no profile facts; direct question as the first message.
2. Multiple lines received together; explicitly decide whether to process all or just the last.
3. Same message event delivered twice; same text delivered as two distinct real events.
4. Bot's own message missing from the DOM; old history reappearing after reconnect.
5. Conversation ID change while replies are queued.
6. Missing category, exhausted pool and unresolved placeholder.
7. Unknown age, underage disclosure, refusal, consent revocation and exit request.
8. Pending extra replies interrupted by a stop or conversation change.
9. Failed send versus unknown send outcome; restart during pending delivery.
10. Expired authorization, reconnect, concurrent start/stop and final worker cleanup.
11. Logs containing token-looking values, email, message content or session identifiers.

Use neutral synthetic messages and a mock transport. This pack contains documentation and lookup tools, not an implemented or verified new chat application.
