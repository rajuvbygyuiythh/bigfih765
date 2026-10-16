# DeadSimpleChat — সম্পূর্ণ scoped delivery plan

Plan ID: **DS-DIAG-v1** · 2026-10-16 · **PROPOSED / OWNER APPROVAL REQUIRED**

এই plan তৈরি করা setup-এর approval নয়। Owner এই exact plan অনুমোদন না দেওয়া পর্যন্ত setup, live bot creation, paid-plan purchase, outbound request বা site unlock হবে না। Plan বদলালে আগের approval বাতিল বলে গণ্য হবে। এই document অনুমোদনের পরও নিজেকে APPROVED বলে rewrite করা হবে না; approval ও exact SHA-256 আলাদাভাবে SITES-এ থাকবে।

## 1. কোন কাজটি শেষ করব

একটি owner-authorized DeadSimpleChat room + একটি disclosed diagnostic bot + consenting test participants। Dashboard থেকে lifecycle, test intake, প্রতি send-এর operator approval, outcome, Stop ও recovery দেখা যাবে। DeadSimpleChat-এর existing audience acquisition বা সাধারণ-purpose chat bot এই scope নয়।

সম্পূর্ণ flow:

**Owner approves plan → private setup → entitlement/auth/scope verification → controlled test intent → one guarded bot reply → consenting witness checks room → failure/Stop/restart tests → release ZIP → GREEN → শুধু Minnit unlock।**

## 2. ব্যবহারকারী কী পাবেন

- একই Orbit dashboard-এ একটি DeadSimpleChat diagnostic panel।
- server-only configuration validation; secret browser/API response/Git/ZIP-এ যাবে না।
- সর্বোচ্চ একটি configured room ও bot; অন্য room/bot হলে reject।
- authenticated narrow callback intake — vendor-supported authenticity contract যাচাই না হলে receiver live-enable হবে না। URL-secret ব্যবহার করলে তাকে provider signature বলা হবে না।
- SQLite durable dedup + one-shot pending/submitting/result ledger। Raw transcript, cookie, IP, profile, key বা query-secret রাখা হবে না।
- একটি registered test question + consenting user-এর জন্য সর্বোচ্চ একটি room-visible disclosed response; প্রতি send-এ operator confirmation। Free text/campaign/bulk send নয়।
- API accepted / rejected / unknown আলাদা; timeout হলে auto-retry নয়। API 200 দিয়ে peer delivered বলা হবে না।
- Stop, restart-disarmed, stale-run/age rejection ও callback replay tests।
- run/setup/backup instructions, evidence report, tests, versioned ZIP + SHA-256।

## 3. Known contract বনাম mandatory discovery gates

Primary sources: [Send Bot Message](https://deadsimplechat.com/support/rest-api/bots/post-send-message-bot), [Quiz/action webhook](https://deadsimplechat.com/support/bots/quiz-bot-using-action-buttons)। Step 1 report-এ দুইটি page পুরো পড়ার ফল রয়েছে।

| বিষয় | জানা তথ্য | কী না মিটলে বন্ধ থাকবে |
| --- | --- | --- |
| Plan/access | Docs: Business / Advanced API | Owner's actual entitlement, room/bot authorization; purchase আলাদা owner consent ছাড়া নয় |
| Send | HTTPS POST `/consumer/api/v2/bot/{bot}/chatroom/{room}/message`, JSON message <=1000 | Exact key/auth requirements যাচাই ছাড়া transport live-enable নয় |
| Auth ambiguity | Table-এ query `auth`; কিছু example-এ Authorization-ও আছে; quiz example-এ নেই | Supported requirement vendor docs/support বা existing authorized successful server evidence থেকে স্থির করতে হবে; credential guessing/probing নয় |
| Callback | Documented `actionButtonPressed`; enclosing message original bot question | Generic mention/new-message shape আন্দাজ নয়; authenticity/replay/retry contract verified হতে হবে |
| Intent identity | Button `_id` definition হতে পারে | এই scope per-click bot নয়: registered bot/room/question/user/action tuple-এ একবার reply। Parent-question linkage ও supported fields staging-এ verify না হলে block; click-ID অনুমান নয় |
| Delivery | HTTP 200 + boolean success:true = API accepted | Consenting witness room-এ response না দেখা পর্যন্ত peer delivery unverified |
| Hosting | Public HTTPS callback + provider API egress দরকার | এই sandbox-এ provider egress নেই; approved deployment ছাড়া live staging অসম্ভব |

কোনো critical discovery gate অমীমাংসিত থাকলে **BLOCKED/AMBER**, GREEN নয়; পরের site unlock নয়। Scope বদলাতে হলে নতুন plan hash ও নতুন owner approval লাগবে। 100% working-এর আগাম guarantee দেওয়া হচ্ছে না।

## 3A. Frozen reply semantics — occurrence-ID আন্দাজের প্রয়োজন নেই

এই v1-এ “প্রতিটি click-এ reply” নয়। **একটি registered question + consenting test user + action-এর জন্য একটিই possible reply**, user যতবার click করুক। এটি deliberate scope; legitimate দ্বিতীয় click-ও একই intent consume করে না, নতুন question/intent লাগবে।

- Local operator একটি fresh owned test question-এর provider ID, room/bot IDs, consenting test user ID এবং fixed action ID `orbit_diagnostic_ping_v1` server-side register করবেন। IDs authorized dashboard/server evidence থেকে; জানা না গেলে setup block, ID guess নয়। প্রয়োজনীয় question publication/registration interface staging-এ supported কিনা verify করতে হবে; না হলে re-plan + re-approval।
- Incoming `bot._id`, `chatRoom.roomId`, `user._id`, `message._id`, `actionButtonPressed.messageId/id/type` registered values-এর সঙ্গে match চাই। Parent IDs একই হতে হবে; action type `action`। Original bot-question text reply input নয়।
- Durable intent key = hash(bot + room + question + consenting user + fixed action)। Provider button `_id`, nick+text বা random local occurrence ID দিয়ে click-identity বানানো হবে না। Run ID key-তে বসিয়ে replay protection reset করা যাবে না।
- Registration ও armed run-এর local expiry থাকবে; callback-এর অজানা timestamp field বানানো হবে না। Expired/consumed/cancelled/unknown intent আবার register/auto-retry করা যাবে না; নতুন provider question লাগবে।
- Authenticated valid match কেবল pending intent করবে। Operator একটি fixed `[Orbit diagnostic bot] pong - requested test only.` room-visible response approve করবেন। No private DM/userId targeting, no free-text answer generation, no automatic question campaign।
- Server keeps secret-free intent hashes/state; consenting user ID credential নয়, তবুও raw user identity ledger/report-এ রাখা হবে না। Bot visibility/room mapping staging-এ witness দিয়ে যাচাই ছাড়া delivery pass নয়।

এই one-shot limitation plan approval-এর অংশ; পরে per-click/general bot চাইলে নতুন scope approval প্রয়োজন।

## 4. Approval-এর পর execution order

1. **Private setup/preflight:** owner নিজের deployment-এ ignored `.env.local`/secret manager-এ values দেবেন। App default disabled/disarmed। Account/plan, callback URL, room ID, bot ID ও bot disclosure validate। Credential values chat-এ নয়। `.env.local` loader থাকলে explicit, no logging; stdout validation-এ শুধু field names।
2. **Contract resolution:** exact query/header auth, callback verification এবং occurrence/intent identity freeze। Need হলে minimum redacted server-side synthetic fixture; browser HAR সাধারণত backend send/webhook দেখাতে পারে না। Missing evidence না জেনে HAR চাইব না।
3. **Intake implementation:** strict content-type/body/batch limits, room+bot/action binding, age/run gate, authenticated origin/secret mechanism, durable dedup। Unrecognized event → no reply।
4. **Outbound implementation:** configured HTTPS origin/path only; no redirect, no arbitrary target, no inherited proxy surprises; query-secret URL/error/access-log redaction; one fixed diagnostic reply, durable intent commit before network। Vendor limits + conservative local cooldown। Hard total timeout/cancellation policy test করতে হবে; শুধু per-I/O timeout দিয়ে bounded Stop দাবি নয়।
5. **Dashboard:** preflight blockers, plan approval/hash, armed state, pending approvals, minimal ledger, disarm/Stop controls। Setup/approval এবং live GREEN আলাদা labels। Queue UI green check local mock থেকে নয়।
6. **Authorized staging:** safe single-room consenting run; webhook receive, one reply, actual witness evidence। Actual successful send auth combination record করা হলেও তা অন্য possible auth combinations-এর necessity প্রমাণ নয়। সন্দেহ হলে vendor confirmation।
7. **Regression:** duplicate, repeated click/legitimate repeated text, cross-room/bot, stale work, invalid secret, oversized/malformed input, expiry/revocation, 4xx/5xx/429, timeout ambiguity, stop during send, crash/restart ও secret-redaction tests। Unknown send কখনও blind retry নয়।
8. **Release/green:** actual live acceptance report, fresh source-bound tests, versioned ZIP/sha256/manifest, clean-extracted run ও reproducible rebuild। Owner-readable result দেখাব। সব gate pass হলে GREEN; তারপর guarded complete-and-next action-এ কেবল Minnit unlock।

এটি deliverable order; unresolved evidence পুষিয়ে random traffic, anti-bot bypass বা unsolicited message দিয়ে কাজ চালানো হবে না।

## 5. Acceptance matrix — কোনটি হলে GREEN

| Gate | Required evidence | বর্তমান অবস্থা |
| --- | --- | --- |
| A. Exact plan approval | Owner/operator explicit approval, exact SHA-256, non-secret reference | **WAITING** |
| B. Authorized setup | Config/entitlement + one-room/bot binding; no secret output | NOT RUN |
| C. Verified receive/identity | Auth/replay/registered one-shot intent linkage/auth/replay contract + consenting fixture | BLOCKED: contract unknown |
| D. Guarded reply | One valid request → one fixed reply; wrong/stale/replayed input → zero sends | NOT IMPLEMENTED/LIVE-TESTED |
| E. Peer witness | Consenting receiver sees correct bot reply in correct room; timestamp/delivery reference, no transcript archive | NOT RUN |
| F. Stop/restart/failure | No new send after Stop; in-flight outcome honest; restart disarmed; no duplicate retry; measured deadline behavior | NOT RUN |
| G. Full regression | Fresh Python + DOM/source-bound receipt for implemented DS connector, not old inspector tests only | CURRENT TESTS BASELINE ONLY |
| H. Handoff | 8 evidenced steps + all catalog acceptance gates + actual new ZIP/sha256/extracted checks | NOT COMPLETE |

A–H সব pass না হলে **GREEN নয়, Minnit unlock নয়**। Progress percentage, plan approval, environment fields present বা HTTP 200 একা GREEN নয়। বর্তমান application scope: single operator/process; 100 live connections, production scaling/security audit ও acquisition metrics acceptance-এর অংশ নয়।

## 6. Explicit non-goals ও stop conditions

No automatic join welcome/promotion, random-stranger outreach, bulk/private DM campaigns, account signup/cookie reuse, CAPTCHA/WAF bypass, guessed private protocols, token harvesting, paid purchase without permission, arbitrary LLM replies বা acquisition claims। Supported callback/auth/identity unavailable হলে Stop + exact blocker; scope পরিবর্তন করলে re-approval।

## 7. Owner decision

Approve **DS-DIAG-v1-এর এই scope** হলে এরপর setup শুরু করা যাবে। Approval মানে credential/purchase/network access নিজে থেকে পাওয়া নয়; required account/deployment setup আলাদা যাচাই হবে। Approval ছাড়া এই turn-এ কেবল plan, approval guards ও tests তৈরি হচ্ছে। Live setup, GREEN ও next unlock কোনোটিই হয়নি।
