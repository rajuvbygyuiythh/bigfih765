# Single-site roadmap

Scope: supported/authorized integrations and consenting tests. Mission remains unchanged in `GOALS.md` (alias to the existing knowledge-pack mission). Active queue and percentages: `SITES.md`. No batch research, file deletion, force push or rebasing published work.

| Step | Deliverable / exit gate |
| --- | --- |
| 1 Recon | One site's primary docs, observed vs unknown contracts, runnable diagnostic code + tests; no invented protocol |
| 2 Contract design | Explicit event identity, auth, room scope, ACK/failure/Stop policy; unresolved live assumptions stay gated |
| 3 Intake | Protected narrow intake, strict schema, durable dedup/identity; malformed/replay tests |
| 4 Outbound | Guarded opt-in transport and one-shot intent/outcome ledger; never blind retry ambiguous sends |
| 5 Dashboard | Server-only configuration, status, operator controls, secret-free diagnostics |
| 6 Integration | Authorized staging; consenting witness; API acceptance != delivered; block rather than fabricate access |
| 7 Regression | Failure/restart/race/privacy cases, source-bound full suite; no false live PASS |
| 8 Handoff | ZIP + sha256 in artifacts, manifest/clean-extract checks, source/evidence/run instructions; preserve old artifacts |

Each turn: read PROJECT_MEMORY → SITES → SKILLS → GOALS → PLAN; code/test/push on the fixed Arena branch; update memory/queue and append CHANGELOG. Delivery percent = completed steps / 8, independent of the older twelve-gate evidence checklist. Steps may contain multiple implementation turns; do not award completion for a scaffold alone.

Current next: **DeadSimpleChat Step 2**. Do not copy Minnit webhook auth, infer normal-message schemas, turn button definitions into unique occurrences, or guess whether the extra Authorization header is required. No capture requested in Step 1: first establish exactly which evidence Step 2 actually needs. Credentials, if later necessary, are entered by the owner in ignored `.env.local`; tools do not automatically source it.

User-requested system OUTPUT FORMAT was not present in the supplied instructions. Until supplied, use only one concise handoff block containing SITE, STEP, PROGRESS, CODE, TEST, PUSH, NEXT; Bangla/Banglish values are preferred. Do not claim this fallback originated in a system prompt.
