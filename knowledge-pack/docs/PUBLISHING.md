# GitHub publication and offline use

## Separate repository status

Requested name: `rajuvbygyuiythh/project-build-knowledge` (private).

The creation attempt on 2026-10-15 failed with:

```text
GraphQL: Resource not accessible by integration (createRepository)
```

**The separate repository was not created.** This is a limitation of the connected GitHub integration's permission, not an indication that a password/token should be shared in chat.

The handoff is being preserved as a `knowledge-pack/` directory and a ZIP in the original `bigfih765` session branch. The final chat response provides the confirmed GitHub location after publication.

## How to finish separate-repo publication

1. On GitHub, create an empty private repository named `project-build-knowledge` (or another preferred name).
2. Share the repository URL with the agent and authorize the GitHub connection to access it. Do not share passwords, access tokens or two-factor codes.
3. Publish the **contents of this knowledge-pack directory** at the new repository root. Do not include the original project's runtime/source ZIPs or capture data.
4. Re-run `python tools/validate_pack.py` after transfer. Update these publication notes and regenerate checksums when editing documentation.

Alternatively, extract the downloaded ZIP and upload its knowledge-pack contents through GitHub's file-upload interface. Private repository access is still required for future agents; attaching the ZIP is an offline alternative.

## Suggested future maintenance

Keep a short decision log for confirmed new requirements. Refresh inventory/hash references when source changes. Do not overwrite historical observations with assumptions about a new platform.
