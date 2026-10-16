# Approved Europe browser work — execution handoff

Date: 2026-10-16. Owner's latest instruction: “approve fill next of all task no need to tell me unlock all task”. Context is the immediately preceding eight-site Europe browser shortlist. All eight assessment/implementation work items are now approved without repeated per-site project approval. This is not third-party platform permission, a live test, or authorization to bypass a service restriction.

## Shipped in this turn

- `control-plane/data/europe_assessment.json`: filled public-source recon for all eight websites, retaining provider/month/device scope, browser type/account requirements, policy source and limitations.
- `control-plane/europe_workflow.py`: strict, bounded manifest reader and task/core-evidence packet generator; exact decimal arithmetic for listed European-country shares, closed-field output and independent result objects.
- `control-plane/tools/europe_tasks.py`: runnable all-site text/JSON worklist or per-site packet, without network, chat joins or messages.
- Nine explicit per-site core requirements: permission, connection/session, conversation identity, incoming events, send/reply, ACK/failure, next/close, reconnect/cleanup/Stop, and consent/privacy. Unknown transport fields stay unknown rather than becoming invented API/WS schemas.
- Owner work approval is separate from live readiness. All eight work items are unlocked; adapters implemented=0, live connected=0. The existing runtime platform registry and canonical historical provider queue are untouched.
- New manifest is included in `research.source_fingerprint`; current regression receipt is source-bound.
- Updated PROJECT_MEMORY, SITES, PLAN, SKILLS, AGENTS, README and CHANGELOG for the latest instruction. GOALS and its target remain unchanged. No auth/demo loop restarted.

## New policy research actually performed

Three official pages retrieved and relevant clauses read; not all eight automation policies reviewed.

### 6obcy

Source: https://6obcy.org/regulamin

- Section 8 prohibits user advertising.
- Section 9 reserves blocking of unofficial clients and says their content may be altered, corrupted or blocked.
- Allows adults, or people15+ with guardian permission. Not an adult-only network.
- A non-official integration is not treated as approved by the owner's project instruction. Its next task is establishing a permitted interface/scope, not copying a private endpoint or bypassing a client restriction.

### Bazoocam

Source: https://bazoocam.org/cgu_en.html

- Article5 prohibits professional/commercial use, advertising other websites or IRC networks/channels, and disruptive mass messaging.
- No general automation permission established.
- Homepage18+ notice and terms' parental-permission wording differ; do not infer all participants are verified adults.
- Next task is permitted-scope review. Do not build an advertising/outreach transport from this shortlist approval.

### Chaat

Source: https://www.chaat.fr/conditions (page says updated March6,2024)

- Section6 expressly tolerates bots/automatic systems with mode+B so they are recognized; they must comply with the rules and not waste resources.
- Section4 prohibits spam/flood, similar-service advertising and sanction bypass. It caps sessions at3 unless a qualifying operator exception is granted. Do not open sessions to test the cap.
- Section2 excludes minors, while section5 contains inconsistent minor/guardian language. Apply strict adult/consented scope pending clarification, not a claim of participant verification.
- This is conditional bot tolerance, not an established connection endpoint/authentication/event/ACK contract or permission for arbitrary messaging.

**Next technical priority: Chaat contract investigation.** This changes the traffic-first 6obcy priority based on stronger primary policy evidence. No endpoint, port, protocol payload or sender was guessed. Five remaining sites still need current automation-policy review.

## Run

From repository root:

```sh
python -B control-plane/tools/europe_tasks.py
python -B control-plane/tools/europe_tasks.py --json
python -B control-plane/tools/europe_tasks.py --site chaat
python -B control-plane/tools/run_checks.py --ui
```

`--site` accepts only fixed shortlist IDs; it is not a path/URL input. Read-only output is the task artifact, not a provider command. No background scheduler is installed.

## Executed tests and outcomes

- Initial focused run:14 new tests PASS before the policy follow-up.
- Final full command: `python -B control-plane/tools/run_checks.py --ui` — exit0.
- **174 Python tests PASS**, including **15 new Europe-worklist tests**.
- **55 DOM/local-HTTP checks PASS** (23 existing UI +10 reply lab +6 planning +16 workspace).
- Four JavaScript syntax checks PASS.
- Source-bound receipt PASS and independently rechecked fresh against `source_fingerprint()` after the run.
- Tests cover eight-site approval/no repeated prompt, no runtime enabling/completion inflation, zero network, legacy state unchanged, exact geography arithmetic and device scopes, room-vs-random distinction, malformed/oversized/missing manifests, invalid/credential-bearing URLs, invalid/nonfinite shares/counts, duplicates/order, output extra-field stripping, policy-based priority, CLI JSON/selection and source fingerprint changes.
- `git diff --check` PASS.
- Canonical SITES machine block byte-equivalent to published baseline; GOALS target content byte-equivalent to published baseline.
- Installed existing locked npm dependencies with `npm ci --ignore-scripts --no-audit --no-fund`; no dependency source/package changes. Real Chromium checks NOT run in this turn; historical browser results are not substituted into the new receipt.

## Git continuity

The turn began on the correct Arena branch but local HEAD was9a7c7b3 and published project files appeared untracked. Fetched `origin/arena/d73f03f8-bigfih765`, confirmed ancestor relationship, compared existing files to published af16848 (GOALS is a symlink), and used `git reset --mixed FETCH_HEAD` to advance local HEAD/index while preserving working files. No hard reset, rebase, force push, branch switch or deletion. New work is committed/pushed only to the session branch; actual hash is provided in the final handoff after push succeeds.

## Not delivered / remaining

- No site-specific adapter, authorized session, live API/WS capture, send/receive/ACK acceptance or partner-delivery evidence.
- No live preview started; no private env/credential values read.
- No provider permission invented from audience size or owner approval.
- No revised frozen DS scope, runtime unlock, false GREEN or Step8 ZIP.
- Historical DS25%/seven successor runtime locks remain as historical provider gates; they do not block the new separately approved public-work backlog.
- Research audience numbers remain estimates of repeatable website visits, not unique people/active chat users/matching probability. Semrush chart-label inconsistency is recorded in `research/europe-browser-chat-2026-10-16.md`.
