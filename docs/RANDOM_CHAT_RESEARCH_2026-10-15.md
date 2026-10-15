# Random-chat platform research — 2026-10-15 UTC

## বাংলায় সিদ্ধান্ত

Owner-এর দেওয়া `project-build-knowledge-2026-10-15.zip`-এর `GOALS.md`, `docs/CHAT_SYSTEM.md` ও `docs/SECURITY_AND_LIMITATIONS.md` আগে পড়া হয়েছে। Goal: বিদ্যমান conversation engine/state/reply logic রেখে নতুন platform adapter দিয়ে similar project; শুধু নতুন chat website-এর নামের তালিকা নয়।

এই research-এ existing third-party random-chat service-এর মধ্যে **অনুমোদিত ও live-tested automation-ready platform নিশ্চিত করা যায়নি**। এটি “কোনো site-এ প্রযুক্তিগতভাবে সম্ভব নয়” এমন সিদ্ধান্ত নয়। অনেকটির terms automated interaction নিষিদ্ধ করে; অন্যগুলোর ক্ষেত্রে permission/API contract অনিশ্চিত।

**প্রথম contact shortlist:** Chatblink ও StrangerMeetup-এর operator-কে intended disclosed/consented bot integration সম্পর্কে জিজ্ঞেস করা। এটি permission পাওয়ার সম্ভাবনা বা সহজ implementation-এর ranking নয়। Written permission/API information না পাওয়া পর্যন্ত কোনোটিকে approved target বলা যাবে না।

## Research scope and limits

- 27 web-search queries were issued. This is not a claim that Google search pages 1–100 or 100 complete pages were reviewed.
- 19 page-retrieval calls reviewed official-page text or relevant chunks, including redirects, an obsolete Emerald terms URL and an incorrect Chatblink terms route. Long documents were not all read end-to-end; the relevant clauses are identified below.
- Five GitHub repositories had metadata/root inventories and READMEs reviewed; four exposed a root LICENSE that was separately read.
- Third-party comparison/SEO pages were discovery leads only. Operator rules and actual license files controlled the recommendations.
- No signed-in chat session, browser network capture, live WebSocket connection, message delivery, bot run, active security test or production integration test was performed.
- Public page retrieval proves only what that retrieval returned. It does not establish service uptime, audience size, regional availability or a stable developer API.
- No credentials, cookies, private messages or raw session captures were requested or collected.

## 1. Existing sites: policy and feasibility screen

Status meanings:

- **Not a default automation target:** a relevant operator clause expressly restricts automation/bots/scripts or the proposed method. Seek operator permission instead of building around the restriction.
- **Permission/API unknown:** the read material does not establish approval for this project's interaction model. Not an implicit permission.
- **Unverified technology:** no production HTTP/WS protocol or auth contract was captured in this review.

| Platform / primary source | Observed evidence | Assessment for this project |
| --- | --- | --- |
| Emerald Chat — https://emeraldchat.com/terms-of-service/ | Sections 3 and 9 prohibit automated/non-human access and automated message scripts. Current terms name Connected Software Inc.; older `terms.txt` returned different legacy text. | Not a default automation target. Do not rely on the older terms file or third-party bot tutorials. |
| OmeTV — https://ome.tv/rules/ | Rule 7 prohibits external software, including bots/scripts, modifying service operation. Rule 4 prohibits spam, bulk messages and links including social profiles. | Poor fit for a migrated automated/contact-sharing flow without explicit permission. |
| Chatroulette — https://chatroulette.com/terms | Sections 3 and 8 restrict automated/non-human access, automated message scripts and unauthorized systems. Terms displayed an update date of 18 June 2026. | Not a default automation target. No approved bot/API integration established. |
| Chatrandom — https://chatrandom.com/terms/ | User Conduct and Restrictions prohibits automation tools/bots/scripts collecting or interacting with users or data. | Not a default automation target. A video/text offering does not imply bot support. |
| Shagle — https://shagle.com/terms/ | User Conduct and Restrictions contains the same relevant prohibition on automation interacting with users/data. | Not a default automation target. |
| Chatspin — https://chatspin.com/legal/terms/ | `/terms/` redirected to this canonical page; User Conduct and Restrictions prohibits automation tools/bots/scripts collecting or interacting with users/data. | Not a default automation target. |
| Camsurf — https://camsurf.com/terms/ | User Conduct and Restrictions prohibits automation tools/bots/scripts collecting or interacting with users/data. | Not a default automation target. |
| Umingle / Uhmegle lead — https://umingle.com/rules/ and https://uhmegle.com/ | Umingle rules prohibit unauthorized scripts/bots/automation. The Uhmegle terms-request retrieval returned a landing page linking users to Umingle. | Not a default automation target. Do not infer common ownership or identical APIs from a link/redirect alone. |
| TalkWithStranger — https://talkwithstranger.com/talk-to-strangers-privacy-policy.html | Terms & Conditions subsection says not to use automated programs to start chats. Other marketing pages discuss bots generally; that is not an integration grant. | Not a default automation target. Policy text matters more than marketing references to bot integration. |
| Chatblink — https://www.chatblink.com/terms-of-use | Eligibility item 5 prohibits automated systems for data mining/spam; impersonation and false information are also restricted. Wording is narrower than a universal bot ban. | Permission/API unknown. Ask operator for disclosed, consented integration approval. No public supported bot API was located in the scoped search; absence is not proven. |
| StrangerMeetup — https://strangermeetup.com/terms | Retrieved terms are dated 25 August 2020 and contain broad IP, termination and use provisions. Its homepage advertises keeping bots out: https://strangermeetup.com/ | Permission/API unknown. Read terms do not grant a bot integration. Ask operator; old/sparse terms do not make it an easy target. |

**Reference platform:** Chitchat's current terms (https://www.chitchat.gg/terms/, updated 9 September 2026) section 12 restricts automated content access, reverse engineering and bypassing protections. Its guidelines (https://www.chitchat.gg/guidelines/) restrict third-party software changing video-service functionality. A previous project archive is not proof that the current operator permits it.

### What this table does not claim

It does not say which site's private WS endpoint is easiest to replay, that a text-only mode works without the required video/auth flow, that any bot is undetectable, or that switching sites avoids future maintenance. Socket.IO, raw WebSocket and WebRTC are distinct technologies; none was assumed for a third-party site from the word “realtime.”

## 2. Self-hosted alternatives: controllable implementation, not existing audience

These are source projects to evaluate for an **owner-operated deployment**, not permission to automate a public demo. No application code was run, and no security/dependency audit was completed.

### A. Python: hakiKhuva/random-chat

- Repository: https://github.com/hakiKhuva/random-chat
- README describes Flask-SocketIO realtime messages; root has `app/`, `requirements.txt`, `wsgi.py`.
- Root LICENSE contains MIT terms. Preserve the license/notice if reusing code.
- Metadata: not archived; pushed_at `2023-09-27T14:44:29Z`.
- README blob: `4c2379aece9c43b53aa1b07494b8ca2b08002e24`.
- LICENSE blob: `639a9e99234514547799ea0e06b899b4269a6c4a`.
- Assessment: a potentially small Python baseline/reference; dependencies, match lifecycle, moderation and production readiness still need review. GitHub's primary-language field says JavaScript, despite a Python server; language labels alone are insufficient.

### B. Go: minghsu0107/go-random-chat

- Repository: https://github.com/minghsu0107/go-random-chat
- Default branch at review: `kafka`.
- README describes Go, WebSocket handling via Melody, matching, JWT chat auth, gRPC, Kafka, Cassandra and observability.
- Root LICENSE contains MIT terms.
- Metadata: not archived; pushed_at `2025-08-06T23:41:54Z`.
- README blob: `0e8905e1ec1d0ce0e7716fe8278e955689363cf6`.
- LICENSE blob: `ad960e98b46945703d073f408da7821fb4c501d7`.
- Assessment: useful architecture reference, but the dependency footprint appears too heavy for a first small deployment. That complexity assessment is a recommendation, not a benchmark.

### C. Python HTTP-only reference: k0dev/random-chat-api

- Repository: https://github.com/k0dev/random-chat-api
- README describes one-to-one HTTP lobbies, random or manually created, with timed deletion. It lists API documentation as TODO.
- Root LICENSE contains MIT terms.
- Metadata: not archived; pushed_at `2023-08-03T20:56:30Z`.
- README blob: `56f7e8683c1807b6fc04b1dbe8fb739d9f6caa01`.
- LICENSE blob: `6cf1d25aa2aa1e441e9d6b4277e361a03fdf2c8f`.
- Assessment: small conceptual HTTP alternative; do not advertise it as an existing verified WS solution. API semantics and dependencies need code review.

### D. JavaScript starter: sathwik8627/stranger-chat

- Repository: https://github.com/sathwik8627/stranger-chat
- README describes React + Node + Socket.IO + WebRTC, random matching and next/report flows.
- No root LICENSE was found; GitHub license metadata is null. Public visibility does not grant reuse rights.
- Metadata pushed_at `2026-09-10T06:20:15Z`.
- README blob: `cf3d49b8d9a4a26148a43f7ba707af1c64654794`.
- Assessment: architectural reading only until an appropriate license/permission is confirmed. README itself lists substantial production hardening still needed.

### E. Excluded from reuse despite an attractive README: saketkumar-18/strngr

- Repository: https://github.com/saketkumar-18/strngr
- README says Node/Express/Socket.IO/WebRTC and labels the project MIT.
- **Actual root LICENSE conflicts:** “All Rights Reserved”, visibility only, not licensed for reuse; written permission is required to copy/modify/redistribute.
- GitHub license metadata returned `NOASSERTION`.
- README blob: `576e82692d688a1fd0f13c629d4475d5e1686951`.
- LICENSE blob: `6f817c5df130b9c3e82c20cde1a7e3b2309bfe0c`.
- Assessment: not a reuse baseline without permission. Search snippets/README labels are not a substitute for the license file.

## 3. Can an API/WS-driven project be built in Python, Go or JS?

Yes as an engineering approach for an authorized target or an owner-operated system. Feasibility for an individual third-party site remains unproven until its permitted interface and actual lifecycle are examined.

- **JS/TypeScript:** useful for browser-side observation and event adapters; Socket.IO client only when Socket.IO is actually confirmed.
- **Python:** close to the existing EVA conversation API, fast offline prototypes and test fixtures.
- **Go:** suitable for bounded concurrent workers, cancellation and a desktop/dashboard core.

Language choice does not solve an unstable private API contract or missing authorization.

### Authorized investigation sequence

1. Obtain a documented API/SDK or operator permission covering intended bot behavior, environment, test accounts, message types and rate limits.
2. Use synthetic/consented test participants. Prefer operator-provided sandbox documentation over capturing unrelated users.
3. Inspect the permitted HTTP/event lifecycle: session expiry, match identity, new-message identifiers, ACKs, edits, typing, partner-left, reconnect and close.
4. Keep cookies/tokens/private content out of shared HARs and traces; use redacted schema fixtures, not raw browser-profile exports.
5. Write a platform adapter returning normalized events. Keep reply engine/state/storage outside it.
6. Add contract tests and replay fixtures for duplicate delivery, out-of-order events, late ACK, unknown send outcome, reconnect and stale conversations.
7. Add schema-drift alarms and a fail-closed feature flag. Do not automatically probe new endpoints or bypass protections when a contract breaks.
8. Verify one worker/one conversation before scaling; track confirmed delivery and await clean shutdown.

## 4. Fit to the owner's existing knowledge pack

Reusable: `new_conversation()` / `reply()` concept, per-conversation state, category pools, anti-repeat, duplicate-event handling, provenance, worker lifecycle and delivery tracking.

Must be reconsidered: target-specific auth, session/profile storage, private endpoint assumptions, bot disclosure, participant consent, global age/content policy, refusal handling and social-contact-sharing rules. These are not portable just because both sites have text chat.

Proposed dependency direction:

```text
UI -> application lifecycle -> authorized platform adapter
                            -> normalized events / deduplication
                            -> policy -> conversation engine
                            -> guarded delivery -> persistence / redacted logs
```

**Practical recommendation:** for an existing-audience site, first seek operator confirmation from Chatblink or StrangerMeetup; treat both as unapproved until answered. For low-maintenance owned integration, evaluate the MIT Python baseline or implement a small original Node/Go server; it will not supply a ready-made audience. Do not spend weeks reverse-engineering a site whose operator disallows the intended automation.

## 5. Operator inquiry template

> We are evaluating a disclosed, opt-in automated chat integration. Do you permit this on your service? Do you provide a supported API/SDK or test environment? Please confirm allowed actions (matching, receiving/replying, reconnecting), rate limits, bot disclosure, participant consent, retention requirements, and whether commercial/contact-sharing behavior is permitted. We will not deploy without your approval or bypass your protections.

## 6. Research reliability notes

- Similar names/domains in search results were not treated as the same operator: for example, `chatrandom.net` is not evidence for `chatrandom.com`, and `chatroulette.to` is not evidence for `chatroulette.com`.
- Chatblink `/terms` returned a profile-unavailable page; the actual reviewed legal page was `/terms-of-use`.
- Emerald's older `terms.txt` and current `/terms-of-service/` returned different legal text. The current canonical terms were used for the screening decision.
- A result mentioning general chatbot features is not developer documentation or permission to start random chats automatically.
- No traffic/audience, price, bot-detection or “easy automation” ranking is asserted.
- This is a technical/policy screening memo, not a legal opinion or a verified production-integration report.
