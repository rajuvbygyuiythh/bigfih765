# Site workstreams — authorization and evidence

## Latest owner-approved Europe browser workstream

2026-10-16: all eight shortlisted websites are approved for assessment/implementation work, with no repeated owner-approval prompt. Work is **UNLOCKED**, not live-enabled. Current runnable source of truth for this separate backlog: `control-plane/data/europe_assessment.json` and `python -B control-plane/tools/europe_tasks.py`.

| Website | Work authorization | Next evidence/task | Live |
| --- | --- | --- | --- |
| 6obcy | APPROVED / UNLOCKED | Administrator permission: unofficial-client restriction | NOT READY |
| Bazoocam | APPROVED / UNLOCKED | Permitted scope: commercial/advertising restrictions | NOT READY |
| Chatroom2000 | APPROVED / UNLOCKED | Current automation policy review | NOT READY |
| Knuddels | APPROVED / UNLOCKED | Current policy + browser feature limits | NOT READY |
| Chaat | APPROVED / UNLOCKED | Connection/event/ACK/close contract; bots conditionally tolerated with+B | NOT READY |
| Tchatche | APPROVED / UNLOCKED | Current automation policy review | NOT READY |
| Deutscher-Chat | APPROVED / UNLOCKED | Current automation policy review | NOT READY |
| Chat4free | APPROVED / UNLOCKED | Current automation policy review; do not bypass challenge | NOT READY |

Next technical priority: **Chaat contract investigation**, selected by primary policy evidence rather than traffic alone. No live adapter implemented. The historical provider-delivery machine block below is unchanged and applies only to that earlier queue; it does not relock this approved research/backlog.

## Historical provider delivery queue (runtime gates preserved)

**Active: DeadSimpleChat — PLAN APPROVED / NEW OPERATOR WORKSPACE IMPLEMENTED. All seven remaining target sites are LOCKED.** Complete the active site before unlocking exactly the next site. No skip/unlock-all path. Restricted/reference sites never enter the unlock queue.

Percent = completed delivery steps / 8, not success probability. Legacy offline work is preserved; Minnit still lacks live evidence. A blocked active site stays active/locked-in rather than being falsely marked done. Pure offline inspectors and historical configuration slots remain available; project advancement and real diagnostic arming/sending are gated.

<!-- site-workflow:start -->
| Site | Lock | Delivery steps | Progress |
| --- | --- | --- | --- |
| deadsimplechat | ACTIVE | 2/8 | 25.0% |
| minnit | LOCKED | 0/8 | 0.0% |
| rumbletalk | LOCKED | 0/8 | 0.0% |
| chatwee | LOCKED | 0/8 | 0.0% |
| chatblink | LOCKED | 0/8 | 0.0% |
| strangermeetup | LOCKED | 0/8 | 0.0% |
| chatango | LOCKED | 0/8 | 0.0% |
| chatiw | LOCKED | 0/8 | 0.0% |
| chatzy | RESTRICTED | — | N/A |
| chitchat | REFERENCE | — | N/A |
| joingy | REFERENCE | — | N/A |
| isexychat | REFERENCE | — | N/A |

<details><summary>Machine-readable queue (canonical)</summary>

```json
{
  "schema_version": 1,
  "revision": 2,
  "active_site": "deadsimplechat",
  "order": [
    "deadsimplechat",
    "minnit",
    "rumbletalk",
    "chatwee",
    "chatblink",
    "strangermeetup",
    "chatango",
    "chatiw"
  ],
  "sites": {
    "minnit": {
      "state": "locked",
      "completed_steps": [],
      "evidence": {}
    },
    "deadsimplechat": {
      "state": "active",
      "completed_steps": [
        1,
        2
      ],
      "evidence": {
        "1": "research/deadsimplechat-recon-2026-10-16/REPORT.md",
        "2": "research/deadsimplechat-plan-2026-10-16/PLAN.md"
      },
      "plan_path": "research/deadsimplechat-plan-2026-10-16/PLAN.md",
      "approval": {
        "plan_sha256": "dc8a906cd04c6293c54d347f1a910767202a890f8dbbc45b9206c1a80edb01f8",
        "approved_at": "2026-10-16T12:09:44.536843+00:00",
        "reference": "owner-chat-2026-10-16-approve-and-local-txt-test"
      }
    },
    "rumbletalk": {
      "state": "locked",
      "completed_steps": [],
      "evidence": {}
    },
    "chatwee": {
      "state": "locked",
      "completed_steps": [],
      "evidence": {}
    },
    "chatblink": {
      "state": "locked",
      "completed_steps": [],
      "evidence": {}
    },
    "strangermeetup": {
      "state": "locked",
      "completed_steps": [],
      "evidence": {}
    },
    "chatango": {
      "state": "locked",
      "completed_steps": [],
      "evidence": {}
    },
    "chatiw": {
      "state": "locked",
      "completed_steps": [],
      "evidence": {}
    },
    "chatzy": {
      "state": "restricted",
      "completed_steps": [],
      "evidence": {}
    },
    "chitchat": {
      "state": "reference",
      "completed_steps": [],
      "evidence": {}
    },
    "joingy": {
      "state": "reference",
      "completed_steps": [],
      "evidence": {}
    },
    "isexychat": {
      "state": "reference",
      "completed_steps": [],
      "evidence": {}
    }
  }
}
```
</details>
<!-- site-workflow:end -->

## Completion and unlock rule

`complete-and-next` atomically marks only the active site DONE and unlocks exactly one successor. It requires owner approval of the exact unchanged scope plan, all eight sequential evidenced steps, all twelve site-specific acceptance gates, fresh passing regression proof and Step 8 ZIP + matching SHA-256. Approval alone does not run setup or unlock anything; setup starts only after explicit approval, and next unlock waits for actual GREEN. A percentage or operator click cannot bypass these checks. No live gates are complete just because local tests pass.

Root workflow was bootstrapped from existing work; this lock update is not new batch research. Machine state above is canonical; the table is regenerated by the queue tool. Never hand-edit just the table or maintain a second queue.

## Active-site acceptance

DeadSimpleChat: Steps 1–2 complete (25% delivery). Proposed full plan: `research/deadsimplechat-plan-2026-10-16/PLAN.md` (DS-DIAG-v1). Owner explicitly approved unchanged DS-DIAG-v1; approval is recorded above. Approved new operator workspace is default, with TXT self-test inside Messages and prior tester preserved at `/legacy/test`; Step 3 now has a disabled-by-default shadow receiver, private env loader and setup/status controls; provider authenticity/staging remains partial, no live GREEN or next unlock. TXT multi-line flow is local-only and does not expand the provider one-shot scope. One registered question/user/action has at most one fixed room-visible response; not per-click bot automation. Auth-header ambiguity, webhook authenticity, registered question linkage, account/plan/egress and consenting peer delivery remain unresolved. Per-click uniqueness is not promised by the frozen one-shot scope. Browser HAR normally cannot show server-to-server callbacks. Report: `research/deadsimplechat-recon-2026-10-16/REPORT.md`.

Shadow setup evidence: `research/deadsimplechat-shadow-2026-10-16/REPORT.md`. Private configuration template: `.env.example`; actual `.env.local` is ignored, explicit-load only, never paste values in chat. No provider sender exists yet.

2026-10-16 dashboard reset: full screen/form/architecture and site-order map in `docs/DASHBOARD_MASTER_PLAN.md`; representative old UI analysis in `research/dashboard-review-2026-10-16/REPORT.md`. Default `/` is read-only plan/status, not the replacement dashboard. Presentation work does not complete a delivery step or unlock any site. Canonical machine state remains unchanged.

2026-10-16 owner “ok approve”: dashboard master plan approved separately (`docs/DASHBOARD_APPROVAL.json`), operator shell/local tools/status now implemented,159Python+55DOM+7Chromium smoke PASS. See `research/operator-workspace-2026-10-16/REPORT.md`. Default is `/workspace`; `/plan` remains read-only. This presentation approval is not a provider-scope change, completed sequential step, live GREEN or unlock; canonical queue unchanged.
