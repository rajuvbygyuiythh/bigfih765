# Chat-platform discovery and automation feasibility

**Review date:** 2026-10-15 UTC
**Status:** passive public-source screening; runtime/security audit and live delivery NOT performed.
**Deliverables:** this report and `sites.json` (machine-readable field-level evidence). `validate_matrix.py` checks artifact consistency, not third-party functionality.

## Decision first — what to build, and what not to claim

**First engineering candidate: Minnit in an owner-controlled or explicitly authorized room.** Official docs explicitly connect incoming-message webhooks with a bot reply API, and separately document guest access. It is the clearest supported adapter route among the reviewed candidates. Custom webhooks require Community+; the underlying organization API is Basic+. Verify actual entitlement before committing costs. This is a conditional recommendation, not an owner-approved purchase or a working integration. [1](https://docs.minnit.chat/bot/) [2](https://docs.minnit.chat/organizations/api/) [4](https://docs.minnit.chat/chat-settings/guests/)

**Backup: DeadSimpleChat in an authorized customer room.** Its official bot workflow and managed-user provisioning are suitable for an adapter, but advanced API docs specify Business-plan access. The tutorial's free-account setup is not proof that the required production API entitlement is free. [7](https://deadsimplechat.com/support/rest-api/bots/post-send-message-bot) [8](https://deadsimplechat.com/support/platform-guides/new-join-modal-guide) [9](https://deadsimplechat.com/support/bots/quiz-bot-using-action-buttons)

**Crucial product boundary:** these services provide chat infrastructure for a community you operate. They are **not demonstrated replacements for Chitchat's existing random-stranger audience**. If the non-negotiable goal is to automate chats with an existing stranger pool, this research has **not established a candidate that is both permitted and working**. Do not silently substitute an empty owned room for that requirement.

**Existing-audience enquiry shortlist:** Chatblink, StrangerMeetup and Chatiw, for operator-approved integration enquiries only. Their product overlap does not establish bot permission, supported protocol access, successful login or message delivery. No claim that any is easier to bypass or “bot-ready.”

## Scope and method actually executed

- Public-source search and official documentation/page-text retrieval; primary terms reviewed where listed.
- Ten detailed records: nine alternatives plus a Chitchat baseline. Earlier stranger-site policy research is linked below rather than represented as newly repeated tests.
- Findings have separate labels: `documented`, `observed_page_text`, `unknown`, `not_tested`, `not_measured`. A public UI label is not a tested feature; a documented endpoint is not a captured network request.
- Some pages were retrieved in chunks; this is not a claim to have read every linked document. RumbleTalk guest-login guide and Chatzy FAQ/create-page leads include search-result evidence, not completed interactive flows.
- No account creation, signup POST, guest join, token issuance, API mutation, message delivery or security scanner run occurred. **Messages sent: zero.** No third-party transcripts or user profile records are reproduced here.
- Sandbox direct outbound networking is restricted. The available search/page tools return public text, not raw response headers or an interactive third-party browser/DevTools session. This prevents honest runtime measurements in the current environment.

### Requested tools/methods not executed

Shodan, Censys, crt.sh, Wayback, Wappalyzer, BuiltWith, WhatWeb, raw TLS/cipher testing, JA3 measurement, browser XHR/Fetch/WS capture and browser-storage inspection were **not run**. This was not a Google 100-page review. Earlier GitHub license/source research remains a separate report; this pass did not clone/test third-party bot implementations. No installed capture plugin, model upgrade, background daily scheduler or synthetic “live proof” is being claimed.

## Feasibility matrix

Ranking concerns supported integration fit, **not weaker security**. “Existing community” describes the advertised product, not measured user availability.

| Site | Product/audience fit | Automation evidence | Current decision | Live chat proof |
| --- | --- | --- | --- | --- |
| Minnit | Owned community rooms, not verified random pool | Official receive webhooks + send bot API | First authorized-room candidate | Not tested; [details](#site-1) |
| DeadSimpleChat | Owned community rooms | Official bot API/webhooks and user provisioning | Backup; verify entitlement | Not tested; [details](#site-2) |
| RumbleTalk | Owned group chats | Official reads + SYSTEM-message sends | Partial; reply/private parity unknown | Not tested; [details](#site-3) |
| Chatwee | Owned/embedded community | Official SSO/JS runtime control | Partial; full bot send/receive unknown | Not tested; [details](#site-4) |
| Chatblink | Advertised existing random/room community | No supported bot contract verified; Turnstile visible | Operator enquiry only | Not tested; [details](#site-5) |
| StrangerMeetup | Advertised random chat/public rooms | No approved bot API; access varies by mode | Operator enquiry only | Not tested; [details](#site-6) |
| Chatango | Embeddable public groups | No supported bot contract verified | Not first; mixed-age scope | Not tested; [details](#site-7) |
| Chatzy | Private/public configurable rooms | Behavior-modifying user scripts explicitly restricted | Exclude default script route | Not tested; [details](#site-8) |
| Chatiw | Advertised existing guest text/private chat | Guest form visible; no supported bot API verified | Operator enquiry only | Not tested; [details](#site-9) |
| Chitchat reference | Existing random-chat baseline | Historical archive is not current permission/proof | Reference only | Not tested; [details](#site-10) |

## Security and storage — explicit coverage of requested fields

For **every site**, raw response headers (including HSTS/X-Frame-Options), TLS version/cipher/certificate chain, actual CSP, live WAF behavior, runtime cookie flags, localStorage and IndexedDB remain **not measured**. HTTPS source URLs do not establish a TLS security grade. JA3 fingerprints **client** TLS behavior; it is not a server-strength metric. No “no CAPTCHA” or “no WAF” conclusion is drawn from missing public evidence.

Specific public evidence:

| Site | Security/authentication clues actually available | Browser storage evidence |
| --- | --- | --- |
| Minnit | Documented embedding allowlist, room password, SSO and guest controls; not observed headers/CSP | Cookie names/purposes documented; actual values, flags, domain and TTL unobserved |
| DeadSimpleChat | Public/provisioned/members permission model; private API-key auth documented | Server-side managed-user/member concepts documented; no browser inventory |
| RumbleTalk | Admin key+secret to expiring bearer token documented | Message retrieval API implies retained messages within its documented scope; browser storage unknown |
| Chatwee | Owner-secret SSO register/login documented | `chatwee-SID-[CHAT_ID]` session cookie documented; flags unmeasured |
| Chatblink | Retrieved signup/login page contains Cloudflare Turnstile links/text | No runtime storage inspected; Turnstile does NOT establish a WAF configuration |
| StrangerMeetup | Anonymous-mode advertising differs from public-room account requirement | Unknown |
| Chatango | Owner-configurable anonymity and per-user rate controls advertised | Unknown |
| Chatzy | Explicit technical restrictions, room-access options, social-provider references | No actual storage inspection; confidentiality terms are not an encryption/storage audit |
| Chatiw | Guest-entry form and cookie notice visible | Cookie use stated; names/flags unknown |
| Chitchat | Current terms discuss moderation, restrictions and account responsibility | Historical source is not evidence of current cookies/storage |

The per-site entries below cite each underlying finding. No security scores assigned.

## Individual site dossiers

<a id="site-1"></a>

### 1. Minnit

https://minnit.chat/

**Decision:** `documented_integration_candidate` — Explicit receive-event + bot-reply path reduces private-protocol dependence.

**Auth and provisioning**

- **guest:** **documented:** Guests can view/talk by default; room owner can disable or require nicknames. Guest IDs are disposable, not registered accounts. [4](https://docs.minnit.chat/chat-settings/guests/)
- **login:** **documented:** Registered/guest authentication cookies documented; SSO integration is described for an existing host user base. [5](https://docs.minnit.chat/cookies/) [6](https://docs.minnit.chat/integration-guide/)
- **auto_signup:** **documented:** No platform account auto-signup tested. Owner-managed guest access/SSO is distinct from registering provider accounts. [4](https://docs.minnit.chat/chat-settings/guests/) [6](https://docs.minnit.chat/integration-guide/)

**Features:** **documented:** Rooms/channels, embedding, bot responses, join/leave events and owner-controlled access. [1](https://docs.minnit.chat/bot/) [6](https://docs.minnit.chat/integration-guide/)

**Network / API evidence:**

- **documented:** Organization-specific HTTP API endpoint from dashboard; X-Key header; action-based POST requests. API Basic+; message/join/leave webhooks Community+. Custom reply bots are explicitly described. [2](https://docs.minnit.chat/organizations/api/) [3](https://docs.minnit.chat/chat-settings/webhooks/) [1](https://docs.minnit.chat/bot/)
- **XHR/Fetch/WS runtime:** none captured. Endpoints above are documentation/navigation evidence only, not observed browser transport.

**Security / storage:**

- **documented_controls:** **documented:** Embedding-domain allowlist, optional SSO/guest restrictions and room passwords; CSRF cookie purpose documented. These are not measured CSP/header results. [6](https://docs.minnit.chat/integration-guide/) [5](https://docs.minnit.chat/cookies/)
- **cookies:** **documented:** Documented names include r_auth_v, g_auth_v, minnitid, minnitcsrf and connid-chat; no values or actual cookie attributes inspected. [5](https://docs.minnit.chat/cookies/)
- Remaining headers/TLS/CSP/WAF/CAPTCHA/storage fields: unknown unless explicitly identified above; see `sites.json`.

**Next actual checks:** Owner-controlled organization/room; Confirm Community+ entitlement for custom webhooks; Configure API key via environment/secret store, not chat; Verify webhook authenticity/replay handling and rate limits; Two consenting synthetic participants.

**Audience limitation:** No built-in Chitchat-equivalent stranger pool established.

**Live-chat test:** NOT RUN. No sent/received/peer-ack evidence.

<a id="site-2"></a>

### 2. DeadSimpleChat

https://deadsimplechat.com/

**Decision:** `documented_integration_candidate` — Official bot/webhook workflow and managed users; entitlement must be confirmed.

**Auth and provisioning**

- **guest:** **documented:** Public room permission allows username-based join; provider provisions a guest_ identifier. Provisioned/members-only modes differ. [8](https://deadsimplechat.com/support/platform-guides/new-join-modal-guide)
- **login:** **documented:** SSO/basic username and provisioned-user identifiers/access tokens documented; privileged users require separate consideration. [8](https://deadsimplechat.com/support/platform-guides/new-join-modal-guide)
- **auto_signup:** **documented:** Create Users API/dashboard/CSV provisioning is documented for the customer account; not public provider-account mass signup. [8](https://deadsimplechat.com/support/platform-guides/new-join-modal-guide)

**Features:** **documented:** Room roles, public/provisioned/members permissions, bot messages, targeted/private bot responses and action-button webhooks. [8](https://deadsimplechat.com/support/platform-guides/new-join-modal-guide) [9](https://deadsimplechat.com/support/bots/quiz-bot-using-action-buttons) [7](https://deadsimplechat.com/support/rest-api/bots/post-send-message-bot)

**Network / API evidence:**

- **documented:** POST /consumer/api/v2/bot/:botId/chatroom/:roomId/message; auth query carries private key. Bot/join webhooks documented. API docs label Advanced API Business Plan. No live API call made. [7](https://deadsimplechat.com/support/rest-api/bots/post-send-message-bot) [9](https://deadsimplechat.com/support/bots/quiz-bot-using-action-buttons)
- **XHR/Fetch/WS runtime:** none captured. Endpoints above are documentation/navigation evidence only, not observed browser transport.

**Security / storage:**

- **documented_controls:** **documented:** Room permission levels and scoped bot/room access checks documented. Auth-in-query requires URL redaction in our proxy/logging; not a demonstrated vulnerability. [8](https://deadsimplechat.com/support/platform-guides/new-join-modal-guide) [7](https://deadsimplechat.com/support/rest-api/bots/post-send-message-bot)
- **server_side_hints:** **documented:** Provider documents provisioned users and room membership state; database product/schema and retention not established. [8](https://deadsimplechat.com/support/platform-guides/new-join-modal-guide)
- Remaining headers/TLS/CSP/WAF/CAPTCHA/storage fields: unknown unless explicitly identified above; see `sites.json`.

**Next actual checks:** Owner-controlled room/customer account; Verify Business plan/API entitlement before purchase; Configure bot and authenticated inbound-webhook handling; Confirm event types and delivery/retry contracts; Two consenting synthetic participants.

**Audience limitation:** Managed rooms are not an existing random-stranger audience.

**Live-chat test:** NOT RUN. No sent/received/peer-ack evidence.

<a id="site-3"></a>

### 3. RumbleTalk

https://rumbletalk.com/

**Decision:** `partial_integration_candidate` — Official REST APIs exist, but system-message route is not necessarily the desired conversational/private-message interface.

**Auth and provisioning**

- **guest:** **documented:** Owner-enabled guest nickname login described; user/member login and SSO also described. [13](https://rumbletalk.com/blog/index.php/knowledge-base/how-do-i-join-a-chat/)
- **login:** **documented:** Admin integration key+secret exchanged for expiring token, used as bearer auth. Actual token issuance not tested. [11](https://dev.rumbletalk.com/rest/authentication)
- **auto_signup:** **documented:** Managed-user capabilities documented at overview level; no provider signup automation or user creation call executed. [10](https://dev.rumbletalk.com/rest)

**Features:** **documented:** Group rooms, managed users, moderation, reading messages and sending system messages. [10](https://dev.rumbletalk.com/rest) [12](https://dev.rumbletalk.com/rest/messages)

**Network / API evidence:**

- **documented:** POST https://api.rumbletalk.com/token; POST /chats/{chatId}/messages sends a SYSTEM message. Documented read route uses fast=true; old read route deprecated. Not proof of ordinary-user/private-DM parity. [11](https://dev.rumbletalk.com/rest/authentication) [12](https://dev.rumbletalk.com/rest/messages)
- **XHR/Fetch/WS runtime:** none captured. Endpoints above are documentation/navigation evidence only, not observed browser transport.

**Security / storage:**

- **server_side_hints:** **documented:** Stored chat message retrieval is documented; exact datastore, retention and browser storage not inspected. [12](https://dev.rumbletalk.com/rest/messages)
- Remaining headers/TLS/CSP/WAF/CAPTCHA/storage fields: unknown unless explicitly identified above; see `sites.json`.

**Next actual checks:** Owner room/API credentials; Clarify ordinary reply vs system-message requirement; Check supported inbound events/SDK and plan; Consented delivery test.

**Audience limitation:** No shared random-stranger pool established.

**Live-chat test:** NOT RUN. No sent/received/peer-ack evidence.

<a id="site-4"></a>

### 4. Chatwee

https://chatwee.com/

**Decision:** `partial_integration_candidate` — Good documented SSO boundary; need supported message receive/send bot contract.

**Auth and provisioning**

- **guest:** **documented:** FAQ documents guests, chat account, Facebook and SSO options; actual deployed availability must be checked. [17](https://chatwee.com/faq)
- **login:** **documented:** SSO login returns session ID; host forwards session via chatwee-SID-[CHAT_ID] cookie. [15](https://chatwee.com/http-api/sso-user/login)
- **auto_signup:** **documented:** Official /v2/sso-user/register provisions a host user in Chatwee database using chatId/clientKey; not anonymous provider-account signup. [14](https://chatwee.com/http-api/sso-user/register)

**Features:** **documented:** Public/private/group chats, room management, 1:1-only configuration and embedded/full-screen UI documented. [17](https://chatwee.com/faq)

**Network / API evidence:**

- **documented:** chatwee-api.com/v2/sso-user/register and /login; clientKey authentication documented. JS runtime control via static.chatwee-api.com/script.js. Full bot send/receive coverage not established by reviewed docs. [14](https://chatwee.com/http-api/sso-user/register) [15](https://chatwee.com/http-api/sso-user/login) [16](https://chatwee.com/javascript-api)
- **XHR/Fetch/WS runtime:** none captured. Endpoints above are documentation/navigation evidence only, not observed browser transport.

**Security / storage:**

- **cookies:** **documented:** chatwee-SID-[CHAT_ID] stores session ID according to SSO docs; flags/TTL/domain not measured. [15](https://chatwee.com/http-api/sso-user/login)
- **server_side_hints:** **documented:** SSO user creation explicitly stored in provider database; no engine/schema inference. [14](https://chatwee.com/http-api/sso-user/register)
- Remaining headers/TLS/CSP/WAF/CAPTCHA/storage fields: unknown unless explicitly identified above; see `sites.json`.

**Next actual checks:** Owner-controlled chat and integration secret; Confirm conversational bot support with provider; Review entitlement/cookie handling; Consented delivery test.

**Audience limitation:** Community embed, not a verified random pairing service.

**Live-chat test:** NOT RUN. No sent/received/peer-ack evidence.

<a id="site-5"></a>

### 5. Chatblink

https://www.chatblink.com/

**Decision:** `permission_and_runtime_unverified` — Existing random/room feature overlap, but no supported bot contract and auth challenge visible.

**Auth and provisioning**

- **guest:** **unknown:** Anonymous guest join was not established by retrieved signup/login page. [18](https://www.chatblink.com/)
- **login:** **observed_page_text:** Retrieved page contains email/password signup and login plus Continue with Google link; successful flow not exercised. [18](https://www.chatblink.com/)
- **auto_signup:** **not_tested:** No supported auto-signup API verified. Turnstile markup is present; no form was submitted or challenge solved. [18](https://www.chatblink.com/)

**Features:** **observed_page_text:** Retrieved homepage links Random Chat, Talk to Strangers and Chat Rooms. Actual feature operations not tested. [18](https://www.chatblink.com/)

**Network / API evidence:**

- **unknown:** Google sign-in navigation link is visible; no supported messaging/auth API or WS contract verified. Navigation URL is not a captured XHR endpoint. [18](https://www.chatblink.com/)
- **XHR/Fetch/WS runtime:** none captured. Endpoints above are documentation/navigation evidence only, not observed browser transport.

**Security / storage:**

- **captcha:** **observed_page_text:** Cloudflare Turnstile challenge/widget text and links appear in retrieved page. Does not establish challenge outcome for a particular browser. [18](https://www.chatblink.com/)
- Remaining headers/TLS/CSP/WAF/CAPTCHA/storage fields: unknown unless explicitly identified above; see `sites.json`.

**Next actual checks:** Operator integration approval; Permitted account and manual completion of required human verification; Sanitized runtime trace or authorized browser capability; Two consenting test accounts.

**Audience limitation:** Existing community advertised; no audience size/availability or automated delivery verified.

**Live-chat test:** NOT RUN. No sent/received/peer-ack evidence.

<a id="site-6"></a>

### 6. StrangerMeetup

https://strangermeetup.com/

**Decision:** `permission_and_runtime_unverified` — Strong product overlap, but no approved bot API; anti-bot positioning and mode-specific access.

**Auth and provisioning**

- **guest:** **observed_page_text:** Homepage advertises anonymous/no-registration service, but says PUBLIC ROOMS require an account. Modes must be checked separately. [20](https://strangermeetup.com/)
- **login:** **observed_page_text:** Registration/member paths advertised; successful login and auth mechanism untested. [20](https://strangermeetup.com/)
- **auto_signup:** **not_tested:** No supported signup/provisioning API located in reviewed material; no signup requests sent. [20](https://strangermeetup.com/) [21](https://strangermeetup.com/terms)

**Features:** **observed_page_text:** Random stranger chat, public rooms and membership/friend notifications advertised; homepage says it keeps bots out. [20](https://strangermeetup.com/)

**Network / API evidence:**

- No supported message/API contract established in the reviewed material.
- **XHR/Fetch/WS runtime:** none captured. Endpoints above are documentation/navigation evidence only, not observed browser transport.

**Security / storage:**

- Remaining headers/TLS/CSP/WAF/CAPTCHA/storage fields: unknown unless explicitly identified above; see `sites.json`.

**Next actual checks:** Operator approval and supported integration details; Separate random-mode vs public-room test scope; Consented test accounts and capture environment.

**Audience limitation:** No ready-to-automate audience or successful chat session established.

**Live-chat test:** NOT RUN. No sent/received/peer-ack evidence.

<a id="site-7"></a>

### 7. Chatango

https://chatango.com/

**Decision:** `permission_and_runtime_unverified` — No supported bot API established; room-owner restrictions apply. Published terms allow users 13+, so historical adult/contact funnel must not be transplanted.

**Auth and provisioning**

- **guest:** **observed_page_text:** Homepage says administrators decide whether signup is needed. Actual room restrictions not inspected. [22](https://chatango.com/)
- **login:** **observed_page_text:** Homepage exposes login/signup paths; auth protocol untested. [22](https://chatango.com/)
- **auto_signup:** **unknown:** No official provider signup API verified; third-party bots/tutorials are not evidence of permission. [22](https://chatango.com/) [23](https://chatango.com/page?full_terms)

**Features:** **observed_page_text:** Embeddable group chats, moderation, per-user message-rate controls and optional anonymity advertised. [22](https://chatango.com/)

**Network / API evidence:**

- No supported message/API contract established in the reviewed material.
- **XHR/Fetch/WS runtime:** none captured. Endpoints above are documentation/navigation evidence only, not observed browser transport.

**Security / storage:**

- Remaining headers/TLS/CSP/WAF/CAPTCHA/storage fields: unknown unless explicitly identified above; see `sites.json`.

**Next actual checks:** Provider and room-owner approval; Explicit safe user/content scope; Supported integration contract; Consented participants.

**Audience limitation:** Publicly visible groups do not grant access to automate each group.

**Live-chat test:** NOT RUN. No sent/received/peer-ack evidence.

<a id="site-8"></a>

### 8. Chatzy

https://www.chatzy.com/

**Decision:** `restricted_scripts_not_first_target` — Explicit user-script restriction; no documented approved bot receive/reply integration verified.

**Auth and provisioning**

- **guest:** **documented:** FAQ describes private chats for known people/website visitors; room access/password/email settings vary. No live join tested. [25](https://www.chatzy.com/faq.htm) [26](https://www.chatzy.com/advanced.htm)
- **login:** **observed_page_text:** Retrieved terms page links login/signup and social providers. Provider flows not exercised. [24](https://www.chatzy.com/terms.htm)
- **auto_signup:** **documented:** No supported automation signup API verified; technical restrictions prohibit scripts modifying behavior and temporary-email accounts. [24](https://www.chatzy.com/terms.htm)

**Features:** **documented:** Quick/virtual rooms, invitations, commands and configurable permissions; references to third-party APIs concern integrations such as video/social providers, not an exposed bot API. [24](https://www.chatzy.com/terms.htm) [25](https://www.chatzy.com/faq.htm)

**Network / API evidence:**

- No supported message/API contract established in the reviewed material.
- **XHR/Fetch/WS runtime:** none captured. Endpoints above are documentation/navigation evidence only, not observed browser transport.

**Security / storage:**

- **server_side_hints:** **documented:** Terms treat chat contents as confidential. This is a policy statement, not a verified storage/encryption implementation. [24](https://www.chatzy.com/terms.htm)
- Remaining headers/TLS/CSP/WAF/CAPTCHA/storage fields: unknown unless explicitly identified above; see `sites.json`.

**Next actual checks:** Explicit operator exception or supported alternative API.

**Audience limitation:** Private-room product is not equivalent to random matching.

**Live-chat test:** NOT RUN. No sent/received/peer-ack evidence.

<a id="site-9"></a>

### 9. Chatiw

https://www.chatiw.com/

**Decision:** `permission_and_runtime_unverified` — Guest-style text workflow visible; no supported bot API. Terms restrict unapproved commercial use and solicitation.

**Auth and provisioning**

- **guest:** **observed_page_text:** Retrieved homepage shows nickname, age, gender, country/state and Start Chat Now; advertises no email/confirmation required. Form not submitted. [27](https://www.chatiw.com/)
- **login:** **documented:** Terms also describe registered-member passwords. Guest UI and member auth are separate, untested paths. [28](https://www.chatiw.com/disclaimer_and_tos.php)
- **auto_signup:** **not_tested:** A no-registration form does not establish a supported guest API or permission for automated account creation. No request executed. [27](https://www.chatiw.com/) [28](https://www.chatiw.com/disclaimer_and_tos.php)

**Features:** **observed_page_text:** Homepage advertises text/private conversations, photo sharing and mobile use. No messages or uploads tested. [27](https://www.chatiw.com/)

**Network / API evidence:**

- No supported message/API contract established in the reviewed material.
- **XHR/Fetch/WS runtime:** none captured. Endpoints above are documentation/navigation evidence only, not observed browser transport.

**Security / storage:**

- **cookies:** **observed_page_text:** Homepage displays a cookie-use notice; cookie names, values and flags are not known. [27](https://www.chatiw.com/)
- Remaining headers/TLS/CSP/WAF/CAPTCHA/storage fields: unknown unless explicitly identified above; see `sites.json`.

**Next actual checks:** Operator approval for intended automation; Permitted synthetic guest/member test scope; Runtime capture environment; No unsolicited message delivery.

**Audience limitation:** Guest form is not evidence of successful chat access or reliable bot integration.

**Live-chat test:** NOT RUN. No sent/received/peer-ack evidence.

<a id="site-10"></a>

### 10. Chitchat reference

https://www.chitchat.gg/

**Decision:** `reference_only` — Baseline for architecture comparison, not a verified new integration. Current terms restrict reverse engineering, bypass and automated content access.

**Auth and provisioning**

- **guest:** **not_tested:** Not re-tested in this research pass. Historical project behavior is not current authentication evidence. [29](https://www.chitchat.gg/terms/)
- **login:** **documented:** Terms describe account responsibility and 18+ eligibility; no session created. [29](https://www.chitchat.gg/terms/)
- **auto_signup:** **not_tested:** Not tested or approved; historical source is not provider permission. [29](https://www.chitchat.gg/terms/)

**Features:** **documented:** Current terms describe instant messaging and chat/video moderation; historical archive not runtime-certified. [29](https://www.chitchat.gg/terms/)

**Network / API evidence:**

- No supported message/API contract established in the reviewed material.
- **XHR/Fetch/WS runtime:** none captured. Endpoints above are documentation/navigation evidence only, not observed browser transport.

**Security / storage:**

- Remaining headers/TLS/CSP/WAF/CAPTCHA/storage fields: unknown unless explicitly identified above; see `sites.json`.

**Next actual checks:** Current permitted integration and authorized runtime verification.

**Audience limitation:** Existing source ZIP does not prove current service compatibility.

**Live-chat test:** NOT RUN. No sent/received/peer-ack evidence.


## Concrete first experiment — Minnit, conditional on authorized access

This is the next **experiment**, not a completed project and not an authorization to enroll in a paid service.

1. **Access gate:** authorized organization and test room, required webhook entitlement and private API secret configured through deployment secrets (not pasted into chat/Git). Confirm webhook authenticity/secret options, replay behavior, retry guidance and rate limits. Verify current plan requirements; do not purchase anything automatically.
2. **Smallest useful scope:** two consenting test participants in one allowed room/channel; a clearly disclosed command/mention-triggered bot; existing reply/state architecture reused only after source inspection. No arbitrary unsolicited auto-DMs or contact harvesting.
3. **Documented inbound boundary:** handle `chat_message` webhook batches; normalize IDs and sender/room/channel scope; deduplicate by source message ID, not just equal text; discard irrelevant events and bot-self messages. Do not publish webhook IPs or transcripts. This event shape is documented, not runtime-captured. [3](https://docs.minnit.chat/chat-settings/webhooks/)
4. **Documented outbound boundary:** dashboard-provided endpoint + `X-Key`, action `sendmessage`, room/channel and disclosed bot identity. The official bot example uses this path. Do not fabricate a universal API host or borrow another organization's key. [1](https://docs.minnit.chat/bot/) [2](https://docs.minnit.chat/organizations/api/)
5. **Engine boundaries:** adapter → normalized message → dedup/state → disclosure/refusal/exit policy → reply engine → guarded delivery → confirmed/failed/unknown record. Keep core logic separate from platform auth/event schemas.
6. **Offline regression cases:** duplicate IDs; same text with different IDs; batched and malformed events; own-message loop; wrong room/channel; replay; expired key; 429; network timeout; unknown delivery without blind resend; shutdown and stale queues. These tests have not been implemented/run in this research pass.
7. **Live acceptance:** participant A sends a unique synthetic command; verify exactly one inbound event; bot submits one reply; verify API result and participant B's actual view; compare IDs/timestamps; test a repeated event and a separate same-text message; then stop. A successful HTTP response alone does not prove user-visible delivery. Webhook receipt alone does not prove successful reply delivery.
8. **Completion gate:** do not label COMPLETE_FOR_SCOPE until authorized live acceptance passes. If access/runtime capability is absent, status is BLOCKED (integration) or OFFLINE_VALIDATED only after real offline tests. No scheduler or daily success guarantee.

### If the existing stranger audience is mandatory

Keep Minnit/DeadSimpleChat out of the product-equivalence claim. The next route is an operator-approved integration for an existing-audience candidate, **not** guessing private WS endpoints or bypassing Turnstile. Ask the operator for the allowed bot identity, test-room/accounts, supported protocol, rate limits and two-party test procedure. There is currently no live-verified target. A self-hosted MIT project can demonstrate matching and transport, but supplies no existing audience either.

## Policy and operational cautions

- A signup or guest form being visible does not establish permission or a working API. Managed-user provisioning in an owned chat is different from mass creation of provider accounts.
- Chatblink forbids bots for mining/spam; that restriction is not a blanket finding that every benign bot is prohibited, nor affirmative permission for this project. StrangerMeetup says it keeps bots out. Chatzy explicitly restricts behavior-modifying user scripts. Chatango bans spam and has a 13+ minimum; do not reuse an adult/contact-solicitation workflow there. Chatiw restricts unapproved commercial endeavors/solicitation. See their cited terms/page findings.
- Chatwee and DeadSimpleChat documentation places secrets in query parameters. Keep those requests server-side; redact complete query strings from logs/proxies/error traces. This is an implementation caution, **not a demonstrated vendor vulnerability**.
- Never publish session values, auth headers, user IPs, actual transcripts or raw HAR. If authorized capture becomes available, derive minimal redacted fixtures; make no claims about uninspected server internals.
- No CAPTCHA solving/bypass, stealth fingerprinting, bulk signup, scraping of unrelated users or unsolicited stranger messaging was performed.

## Reuse of earlier research

The previous report, [`../../docs/RANDOM_CHAT_RESEARCH_2026-10-15.md`](../../docs/RANDOM_CHAT_RESEARCH_2026-10-15.md), screens eleven commercial alternatives and five GitHub references, including restrictive bot policies and license caveats. It is earlier public/source screening, not extra live-tested candidates. Knowledge-pack architecture remains context, not an already-working SDK. This new report does not alter existing knowledge ZIPs or claim to complete the daily site project.

## Validation and handoff

From repository root:

```sh
python research/chat-platforms-2026-10-15/validate_matrix.py
```

The validator checks JSON structure, source-reference integrity, field completeness, unknown-field values and the truthful not-run delivery status. These are **artifact checks only**, not API, browser, TLS, security or user-chat tests.

Executed results: validator PASS (10 dossiers, 29 source references, 102 explicit unmeasured fields). Four negative checks also PASS: it rejected a false live-test success, an invented TLS value, an undefined source ID and a missing authentication field. ZIP CRC/extracted-copy validation is checked during packaging. No application or remote-service test is implied.

The research ZIP contains this report, `sites.json`, `validate_matrix.py` and the earlier report at its original relative path. No credentials, saved sessions, raw page dumps or actual chat captures are included.

## Sources

These references support documented/page-text findings, not live test claims. Documentation is subject to change. Not every linked page was read end-to-end; none was an interactive authenticated session.

- [1](https://docs.minnit.chat/bot/) — `minnit_bot`
- [2](https://docs.minnit.chat/organizations/api/) — `minnit_api`
- [3](https://docs.minnit.chat/chat-settings/webhooks/) — `minnit_hooks`
- [4](https://docs.minnit.chat/chat-settings/guests/) — `minnit_guests`
- [5](https://docs.minnit.chat/cookies/) — `minnit_cookies`
- [6](https://docs.minnit.chat/integration-guide/) — `minnit_embed`
- [7](https://deadsimplechat.com/support/rest-api/bots/post-send-message-bot) — `dsc_send`
- [8](https://deadsimplechat.com/support/platform-guides/new-join-modal-guide) — `dsc_join`
- [9](https://deadsimplechat.com/support/bots/quiz-bot-using-action-buttons) — `dsc_bot`
- [10](https://dev.rumbletalk.com/rest) — `rumble_api`
- [11](https://dev.rumbletalk.com/rest/authentication) — `rumble_auth`
- [12](https://dev.rumbletalk.com/rest/messages) — `rumble_messages`
- [13](https://rumbletalk.com/blog/index.php/knowledge-base/how-do-i-join-a-chat/) — `rumble_login`
- [14](https://chatwee.com/http-api/sso-user/register) — `chatwee_register`
- [15](https://chatwee.com/http-api/sso-user/login) — `chatwee_login`
- [16](https://chatwee.com/javascript-api) — `chatwee_js`
- [17](https://chatwee.com/faq) — `chatwee_faq`
- [18](https://www.chatblink.com/) — `chatblink_home`
- [19](https://www.chatblink.com/terms-of-use) — `chatblink_terms`
- [20](https://strangermeetup.com/) — `stranger_home`
- [21](https://strangermeetup.com/terms) — `stranger_terms`
- [22](https://chatango.com/) — `chatango_home`
- [23](https://chatango.com/page?full_terms) — `chatango_terms`
- [24](https://www.chatzy.com/terms.htm) — `chatzy_terms`
- [25](https://www.chatzy.com/faq.htm) — `chatzy_faq`
- [26](https://www.chatzy.com/advanced.htm) — `chatzy_create`
- [27](https://www.chatiw.com/) — `chatiw_home`
- [28](https://www.chatiw.com/disclaimer_and_tos.php) — `chatiw_terms`
- [29](https://www.chitchat.gg/terms/) — `chitchat_terms`
