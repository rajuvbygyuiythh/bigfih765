# Available repository skills

These are inspected local tools/methods, not installed model plugins or guaranteed live capabilities.

| Skill | Entry point | Boundary |
| --- | --- | --- |
| Plan-first dashboard review | `/plan`, `docs/DASHBOARD_MASTER_PLAN.md` | Representative UI source review; read-only real locked queue, no write/unlock controls |
| DS shadow setup | Legacy Advanced panel / `--env-file` | Independent URL-secret shadow intake + hashed one-shot intent; NO sender/vendor-auth proof, private values never chat |
| TXT web self-test | `/legacy/test` or explicit `app.py --home tester` | One local user message → one next TXT line, local live report; not provider chat/delivery |
| Scope/approval review | `python -B control-plane/tools/site_queue.py read-plan` | Read current plan/hash; no setup until explicit owner approval; changed plan requires re-approval |
| Sequential lock queue | `python -B control-plane/tools/site_queue.py status` | SITES is canonical; sequential evidence-backed steps, complete-and-next only; no override |
| One-site recon | `python -B control-plane/tools/recon_site.py deadsimplechat` | Official-documentation summary; no network/send |
| Private HAR metadata triage | Same command with `--har .runtime/authorized.har` | One allowlisted bot-send route; no bodies/cookies/IDs/header/query values retained; not webhook capture/auth proof |
| Contract fixtures | `control-plane/contracts.py` and tests | Four local documented subsets only |
| Diagnostic state/transport pattern | `control-plane/minnit.py` and tests | Disabled-by-default single-room diagnostic, never copy vendor auth blindly |
| Regression + source-bound receipt | `python -B control-plane/tools/run_checks.py --ui` | Local Python/DOM; not live delivery |
| Backup packaging | `control-plane/tools/package_release.py` | Step 8 only; explicit allowlist, ZIP/sha256; exclude runtime/secrets |
| Method knowledge | `knowledge-pack/docs/CHAT_SYSTEM.md`, `docs/PROJECT_PATTERNS.md` | Historical selected-method analysis, not all-source/runtime verification |
| Mission (read-only) | `GOALS.md` → `knowledge-pack/GOALS.md` | Compatibility symlink to unchanged existing mission |

GitHub operations: local `git`, GitHub `gh`; push only the Arena session branch. `.env.local` and raw HAR are ignored; never request credential values in chat.
