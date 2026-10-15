# Project Build Knowledge — Agent Handoff

**Owner:** [rajuvbygyuiythh](https://github.com/rajuvbygyuiythh)
**Knowledge snapshot:** 2026-10-15 UTC
**Purpose:** নতুন agent-কে project goal, existing architecture এবং chat-system pattern বুঝিয়ে একই ধরনের নতুন project পরিকল্পনা ও build করতে সাহায্য করা।

**Requested destination:** [futureidea-goal](https://github.com/rajuvbygyuiythh/futureidea-goal) — public read access confirmed; publishing blocked by GitHub integration write permissions. No files were uploaded there.

**ZIP:** supplied separately in the conversation; no release has been published to the requested destination yet.

**Public repository:** শুধুমাত্র sanitized knowledge ও source references; secret/session বা raw conversation data নয়।

> ভাই, এটা ready-made app নয়। এটা আপনার project-building knowledge base। এতে source references, observed logic, reusable patterns, limitations এবং next-project instructions আছে। Secret, saved login, private chat এবং raw capture নেই।

## Agent: read these first

1. **[AGENTS.md](AGENTS.md)** — operating instructions and evidence boundaries.
2. **[GOALS.md](GOALS.md)** — confirmed owner goals versus inferred preferences.
3. **[docs/CHAT_SYSTEM.md](docs/CHAT_SYSTEM.md)** — conversation state, routing, response pools and transports.
4. **[docs/PROJECT_PATTERNS.md](docs/PROJECT_PATTERNS.md)** — family-specific architecture and source locations.
5. **[docs/FEATURES_AND_BUILD_PLAN.md](docs/FEATURES_AND_BUILD_PLAN.md)** — feature choices and implementation gates.
6. **[docs/DAILY_SITE_DELIVERY.md](docs/DAILY_SITE_DELIVERY.md)** — one-site delivery gates and definition of done.
7. **[docs/SECURITY_AND_LIMITATIONS.md](docs/SECURITY_AND_LIMITATIONS.md)** — privacy, authorization, unresolved defects and verification limits.

## আপনার goal, এক কথায়

**Daily target: একদিনে একটি নির্বাচিত site নিয়ে একটি complete, scoped project delivery।** আগের main method, pattern, system ও chat logic ব্যবহার করে assess → plan → implement → test → fix → package → handoff করতে হবে; শুধু নতুন site list বানানোতেই কাজ শেষ নয়।

Daily cadence একটি লক্ষ্য, guaranteed completion বা automatic scheduled service নয়। Scope/access যাচাই করে বাস্তব ফল দিতে হবে; incomplete adapter-কে complete বলা যাবে না। পরের নির্দিষ্ট site এখনও নির্বাচিত হয়নি।

Main workflow: **[DAILY_SITE_DELIVERY.md](docs/DAILY_SITE_DELIVERY.md)**।

## System map

```text
entrypoint / UI
  -> validated configuration
  -> application lifecycle / worker scheduler
  -> authorized transport adapter
  -> normalized incoming events + deduplication
  -> isolated conversation state
  -> policy checks + routing + reply engine
  -> guarded delivery + persistence
  -> redacted diagnostics + UI status
```

Go/Wails, Python EVA and Telegram implementations are **related patterns, not one identical executable**. Never assume a browser transport, private WebSocket protocol or captured endpoint works on a different site.

## Included files

| File | Use |
| --- | --- |
| `PROJECT_MEMORY.md` | Bangla review summary from the original working repo. |
| `docs/PROJECT_PATTERNS.md` | Detailed architecture and reusable lessons. |
| `docs/CHAT_SYSTEM.md` | Observed chat behavior, proposed safe design and test cases. |
| `docs/FEATURES_AND_BUILD_PLAN.md` | Feature matrix and staged delivery plan. |
| `docs/SECURITY_AND_LIMITATIONS.md` | Scope, defects, exclusions and security requirements. |
| `docs/repository-inventory.json` | 23 repositories, 19 archives, hashes and selected method locations. |
| `docs/method-index.json` | Broader first-party declaration index; no method bodies or secret values. |
| `docs/DAILY_SITE_DELIVERY.md` | Confirmed daily delivery target, acceptance gates and honest status labels. |
| `docs/GOAL_ALIGNMENT_2026-10-15.md` | ZIP re-read evidence and latest goal clarification. |
| `templates/SITE_DELIVERY_REPORT.md` | Actual implementation/test/fix/package handoff for one site. |
| `templates/NEXT_PROJECT_BRIEF.md` | Fill this before implementing a new project. |
| `templates/AGENT_START_PROMPT.md` | Copy/paste prompt for a future agent. |
| `tools/query_methods.py` | Offline method lookup; Python standard library only. |
| `tools/validate_pack.py` | Offline structural/link/checksum validation. |
| `tools/build_pack.py` | Regenerate manifest and ZIP; no external dependencies. |
| `docs/PUBLISHING.md` | Public destination, data boundary and publication history. |
| `docs/BUILD_REPORT.md` | Handoff validation results, not historical app certification. |
| `MANIFEST.sha256` | Integrity hashes of the packaged knowledge files. |

## Quick use

- **মানুষ:** `GOALS.md` ও `docs/CHAT_SYSTEM.md` পড়ুন; পরের site-এর জন্য brief পূরণ করুন।
- **Agent:** `AGENTS.md` follow করে source snapshot এবং requirements যাচাই করুন।
- **ZIP:** extract করে এই `README.md` দিয়ে শুরু করুন; GitHub login ছাড়াও পড়া যাবে।

Python 3.9+; standard library only, no install step:

```sh
python tools/query_methods.py --repo chatfilehere --name new_conversation
python tools/query_methods.py --repo bigfih765 --name StartBot
python tools/validate_pack.py
python -B -m unittest discover -s tests -v
# After editing documentation:
python tools/build_pack.py --output ../project-build-knowledge.zip
```

The declaration index is a navigation aid, not proof of correctness. Missing methods can result from parser coverage or syntax failures. Original source remains in the referenced repositories/archives; fetch and inspect the exact snapshot before reuse.

## Maintenance

When a project changes: update the goal/decision notes, refresh source hashes and relevant method locations, record which tests actually ran, and regenerate `MANIFEST.sha256`. Keep personal data and runtime secrets out of this repository. This knowledge base is persistent documentation, not permanent model memory or model training.
