# Next project brief

Copy this into the new project's documentation and fill it with the owner. Use `UNDECIDED` rather than inventing missing requirements.

## Confirmed goal

- Delivery-cycle date:
- Daily target: one selected site, one complete project for agreed scope (not a guaranteed deadline).
- Current status: READY / IN_PROGRESS / BLOCKED / OFFLINE_VALIDATED / COMPLETE_FOR_SCOPE

- Project name:
- Target site/platform:
- What the user should be able to do:
- Why this project is needed:
- Required features, in priority order:
- Explicit non-goals:

## Integration and permission

- Supported API/SDK/documented interface:
- Account/data ownership or authorization:
- Platform terms/rate limits:
- Is interaction user-initiated or explicitly opted in?
- Bot identity/disclosure:
- What live integration testing is authorized?

Do not put real credentials, cookies or session tokens here.

## Chat behavior

- Local rules/templates / LLM / hybrid:
- Supported language(s):
- Conversation start/reset/end rules:
- Required states and routing priority:
- Mandatory facts, optional facts and uncertainty handling:
- Missing-info behavior:
- Global content/age/consent policy:
- Refusal/exit/consent-revocation behavior:
- Multi-message reply rules:
- Anti-repeat and fallback rules:
- Delivery confirmation/retry policy:
- History retention and deletion:

## Architecture

- Baseline family and why:
- Baseline repository/archive/source hash:
- UI: desktop / web / CLI / messaging:
- Transport adapter:
- Storage/config schema:
- One-worker initial limit:
- Eventual worker/resource limit:
- Optional services and safe fallback:

## Delivery and acceptance

- OS/hosting/runtime:
- Packaging format:
- Required offline test cases:
- Allowed integration test:
- Exact success criteria:
- Known risks:
- Unresolved questions:

## Decisions and validation

Use [SITE_DELIVERY_REPORT.md](SITE_DELIVERY_REPORT.md) for the end-of-cycle handoff.

For each milestone, record the confirmed scope, implementation, command/test results and remaining limitations. Do not mark a feature complete only because its interface exists.
