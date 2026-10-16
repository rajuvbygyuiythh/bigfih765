# Site queue — source of truth

Active: **deadsimplechat**. One site per turn; choose first IN-PROGRESS, otherwise first QUEUED. Do not advance a BLOCKED site by inventing access or transport contracts.

Root workflow files were absent at the start of 2026-10-16's workflow reset. This queue is bootstrapped from the existing catalog/committed work, not new batch research. Existing twelve-gate evidence stays in `control-plane/data/site_catalog.json`; the percentages below separately count **completed delivery steps / 8**, not success probability or live readiness.

| Order | Site ID | Status | Current/resume point | Delivery steps | % |
| --- | --- | --- | --- | --- | --- |
| 1 | minnit | BLOCKED | v0.4 local diagnostic delivered; live access/egress/witness missing | Prior workflow; no retroactive score | N/A |
| 2 | deadsimplechat | IN-PROGRESS | Step 1 Recon complete; next Step 2 contract/safety design | 1/8 | 12.5% |
| 3 | rumbletalk | QUEUED | Existing history inspector/system-send spec only | 0/8 | 0% |
| 4 | chatwee | QUEUED | Existing redacted SSO inspector; no chat-send contract | 0/8 | 0% |
| 5 | chatblink | QUEUED | Supported interface/authorization enquiry required; no bypass | 0/8 | 0% |
| 6 | strangermeetup | QUEUED | Supported interface/authorization enquiry required | 0/8 | 0% |
| 7 | chatango | QUEUED | Establish supported integration before transport work | 0/8 | 0% |
| 8 | chatiw | QUEUED | Establish supported integration before transport work | 0/8 | 0% |
| — | chatzy | RESTRICTED | Existing script restriction; do not silently queue automation | N/A | N/A |
| — | chitchat | REFERENCE | Historical baseline only | N/A | N/A |
| — | joingy | REFERENCE | Static upstream reference only | N/A | N/A |
| — | isexychat | REFERENCE | Static upstream reference only | N/A | N/A |

## Active-site acceptance

DeadSimpleChat scope: one authorized room/bot, consenting diagnostic interactions, supported APIs. Step 1 delivers fresh official-contract recon plus runnable offline metadata tooling and regression tests. No live connector/send is enabled. Auth-header ambiguity, callback authenticity, unique click occurrence identity and entitlement/egress remain unresolved. A browser HAR cannot normally show backend bot API calls or provider-to-backend webhooks; do not ask for irrelevant captures or claim observed header presence proves necessity.

Evidence: `research/deadsimplechat-recon-2026-10-16/REPORT.md`; runnable result `control-plane/data/deadsimplechat_recon.json`.
