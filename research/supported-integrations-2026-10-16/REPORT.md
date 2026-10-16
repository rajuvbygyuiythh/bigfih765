# Supported integration analysis and tested local contracts

Review: **2026-10-16**. Selected sites: **Minnit** and **DeadSimpleChat**. Delivery status: **OFFLINE_VALIDATED**; supported-flow desk review and local contract workbench delivered, live platform automation not complete.

## 1. Scope and exact progress definition

The first build scope is an owned/explicitly authorized chat room, a disclosed bot and user-initiated interaction. These services provide chat infrastructure, not a verified existing random-stranger audience. No mass outreach or arbitrary private-protocol implementation is included.

Six desk-review gates are complete for each selected scope: product/scope, authentication/entitlement, guest/user flow, inbound schema, outbound schema, lifecycle/error design. Two local regression gates complete only when a successful receipt matches the current source. Four live-integration gates remain pending.

**Current result after the passing suite: 8/12 = 67% checklist completion for each site.** This is NOT a probability that automation will succeed, not a security-audit coverage score, and not a claim to have implemented 67% of the provider's features. Documentation/design review is 6/6 for the narrow scope stated here; unresolved provider details are explicitly recorded below.

`control-plane/data/site_catalog.json` is the versioned source of the dashboard checklist. `data/test_results.json` records actual local test exits, timestamp and source fingerprint. Missing, failed or stale receipts revert the two local-test gates to pending. The UI refreshes this evidence from the server every two seconds; it does not conduct autonomous new research or push changes in the background.

## 2. Minnit: A–Z integration path

### Product, room setup and identity

Use an organization and a room/channel controlled by the operator. Guests can talk/view by default but the owner can change restrictions. Guest accounts are disposable identities, not permission to automate provider account creation. SSO is an optional integration with an existing host user database, not a requirement to harvest browser sessions. [1](https://docs.minnit.chat/chat-settings/guests/) [2](https://docs.minnit.chat/integration-guide/)

### Entitlement and authentication

The organization API is documented for Basic+; custom webhooks require Community+. Obtain the organization-specific endpoint and API key from its settings. `X-Key` is a server-side secret. There is no generic borrowed endpoint/key and no secret input/storage in this public demo. [3](https://docs.minnit.chat/organizations/api/) [4](https://docs.minnit.chat/bot/)

### Receive contract

Official `chat_message` notifications contain a `data[]` batch. Normalize `msg_id`, `chat_id`, `channel`, `user_id`, `message` and `edited`; discard unrelated profile/IP/attachment details from the normalized fixture result. Separate edits from new-message occurrences. Join/leave/moderation events must not be interpreted as user messages. [5](https://docs.minnit.chat/chat-settings/webhooks/)

Implemented local parser checks explicit expected-room scope, identity types, text bounds, batch shape and the edited flag. It preserves separate IDs for identical text instead of deduplicating equal content. The local limits of 100 batch items / 10,000 input-text characters are defensive implementation limits, **not measured vendor quotas**.

**Open contract detail:** the docs' example channel value is numeric while the table describes a channel name. Confirm the actual deployment value rather than assuming channel name equals stable channel ID. Our local representation preserves the supplied value without claiming it is a provider-stable identifier.

### Send contract

The official bot example uses POST form fields `action=sendmessage`, `chatname`, `channel`, `username`, `message` with `X-Key`. The workbench returns a **secret-free specification only**, with the endpoint deliberately represented as dashboard-provided. It never makes a request. Our 1,000-character outgoing cap is local policy; a Minnit vendor maximum was not verified. [4](https://docs.minnit.chat/bot/)

### State, acknowledgement and failure behavior

Use platform + instance + room/channel + conversation scope for state and message IDs for deduplication. A restarted run must reject stale queued events. Normalize first; then disclosure/exit policy, explicit user action, reply generation and guarded delivery. Separate pending, rejected, API-accepted, peer-confirmed and unknown outcomes. Minnit's precise API acknowledgement schema is not established by the reviewed bot example; do not import DeadSimpleChat's success schema into this adapter.

Before a real receiver exists, confirm provider-supported inbound authentication/secret/signature and replay handling. The local inspector explicitly returns `authenticated_webhook: false`; it is not a public webhook gateway.

### Storage and runtime security

Cookie names/purposes are documented (including registered/guest authentication and CSRF cookies), but values/flags and browser storage were not inspected. A supported server-side API integration should not depend on importing the archive's browser profile. HTTPS documentation is not a measured header/TLS/CSP/WAF result. [6](https://docs.minnit.chat/cookies/)

### Finish gate

Confirm entitlement/authorized room and inbound-auth contract; implement the real bounded receiver/sender behind a single-instance adapter; run authenticated staging and two consenting participants' visible delivery/stop tests. No API key or room has been configured in this session.

## 3. DeadSimpleChat: A–Z integration path

### Product, room permissions and user provisioning

Room modes differ: public nickname joins provision a guest identifier; provisioned-only and members-only rooms require the corresponding identities/access. Create Users/dashboard/CSV provisioning manages the customer's users; it is not provider account signup automation. [7](https://deadsimplechat.com/support/platform-guides/new-join-modal-guide)

### Entitlement and authentication

The bot-send API page specifies **Advanced API: Business Plan**. A tutorial's instruction to create a free account is not proof the required API entitlement is free. Private key is documented in the `auth` query parameter. The examples additionally show an `Authorization` header without clearly resolving whether it is supplementary/required in all deployments. This discrepancy is recorded for staging, not silently guessed away. Keep any future query secret out of access logs, telemetry, exception strings and browser code. [8](https://deadsimplechat.com/support/rest-api/bots/post-send-message-bot)

### Receive contract: bounded to the documented button action

The reviewed quiz guide documents `triggeredBy: actionButtonPressed` plus `user`, `chatRoom`, `message`, and `actionButtonPressed` objects. **The enclosing message is the bot's question, not newly authored user text.** Treat the button as an action, preserving action ID and parent-message ID. The local parser does not guess the ordinary message/mention trigger schema. [9](https://deadsimplechat.com/support/bots/quiz-bot-using-action-buttons)

**Production question:** the button `_id` may identify the button definition rather than a unique click occurrence. It is retained as source identity for inspection, not declared an idempotency key for repeated clicks. Confirm a unique occurrence/delivery identifier before production deduplication. The local inspector never authorizes an automatic reply.

### Send contract and constraints

Documented POST path: `/consumer/api/v2/bot/:botId/chatroom/:roomId/message`. JSON `message` is required and at most 1,000 characters. Optional targeting/correlation fields include `userId`, `uniqueUserIdentifier`, `messageId` and `actionButtons`. The current spec inspector supports a simple message shape only, not user targeting, action-button construction or a live sender. Bot/room IDs are validated; no arbitrary host is accepted. [8](https://deadsimplechat.com/support/rest-api/bots/post-send-message-bot)

### Acknowledgements and failure semantics

Documented HTTP 200 with boolean `success: true` means API acceptance, **not another user seeing the message**. The classifier labels that `api_accepted`, peer delivery `unverified`. Known rejection statuses are rejected; timeout, unexpected body, wrong-typed success and server ambiguity are unknown. There is no blind retry. Documented errors include invalid request and missing/unauthorized bot/room. [8](https://deadsimplechat.com/support/rest-api/bots/post-send-message-bot)

### State, security and finish gate

Keep room/user/action/parent-message identities separate and never route a bot-authored question back into the user reply engine. Use the same per-run cancellation and pending/unknown delivery boundaries as the common core. Confirm inbound authenticity/replay handling, actual mention/new-message schema if that scope is later needed, rate limits, header/query behavior and current entitlement. Then implement a real receiver/sender and run authorized staging plus two-party acceptance. Browser storage/headers/TLS are unmeasured and not required to fabricate an API implementation.

## 4. Local implementation delivered

- `contracts.py`: pure payload inspection, secret-free outbound specification and outcome classification; **no network I/O**.
- `research.py`: versioned site catalog, derived checklist progress and stale-receipt invalidation.
- `tools/run_checks.py`: runs real local tests and writes a source-bound receipt atomically.
- Dashboard **Site research**: scope, percentage meaning, all 12 gates, sources, findings and pending items.
- Offline workbench: editable synthetic fixtures and local normalized output for both documented scopes.
- HTTP routes are operator-token protected when enabled and use existing same-origin mutation/body checks. Nothing accepts third-party webhook traffic or submits chat messages.

## 5. Executed tests

`python -B control-plane/tools/run_checks.py --ui`:

- **43 Python core/HTTP/contract/research tests passed.**
- **12 DOM + real local HTTP checks passed.** This is not rendered-browser or third-party testing.
- JavaScript syntax check passed.

New coverage includes ID/room/batch validation, distinct IDs with equal text, edit separation, ignored sensitive extras, bot-question/action distinction, message caps, malformed payloads, unknown delivery/no blind retry, authentication, stale/failed proof handling, progress denominators and contract-workbench UI behavior. All synthetic inputs are authored fixtures; no captured private traffic is used.

## 6. Four remaining live gates, for each site

1. Provider-compatible inbound authenticity/replay verification.
2. Authorized room, secret configuration and required plan.
3. Implemented real adapter + authenticated staging integration.
4. Consented two-party receive/reply/visible-delivery/stop acceptance.

The four labels cover actual remaining work; 67% is not an effort estimate. No live adapter start is enabled by a percentage or manual catalog flag. Existing dashboard entries remain `not_connected`.

## 7. Related source review / backup

The provided `multiplechat` source is reviewed separately at `../multiplechat-review-2026-10-16/REPORT.md`; its raw captures/browser profiles are not imported or redistributed. The source's existing site modules are not evidence that current provider permission, protocol compatibility or delivery is working. No 50-site target list or 100-live-instance claim is made by this two-site milestone.

All delivered source/evidence belongs on the fixed Arena branch. ZIP v0.2.0 contains the runnable application, tests, catalog, receipt and both new reports/inventory; runtime databases, session artifacts, source archives and dependencies are excluded.
