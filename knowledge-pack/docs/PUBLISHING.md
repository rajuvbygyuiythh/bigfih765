# GitHub publication and offline use

## Destination

The owner supplied this empty public repository for the sanitized knowledge base:

**[rajuvbygyuiythh/futureidea-goal](https://github.com/rajuvbygyuiythh/futureidea-goal)**

Repository visibility and read access were confirmed on 2026-10-15 UTC. Although repository metadata reports owner-level push permission, the actual integration-backed `git push` was denied with HTTP 403. This metadata does not prove the connection has repository write access.

**Publication status: blocked. No files or release assets were uploaded to futureidea-goal.** A sanitized publication checkout was prepared locally on `arena/d73f03f8-bigfih765`; no remote branch was created or overwritten.

To unblock: authorize the Arena GitHub integration for `futureidea-goal` with repository contents write access, then reconnect GitHub in Arena. Do not share credentials in chat. Alternatively, the owner can extract the supplied ZIP and upload its contents using GitHub's file-upload interface.

Once authorized, the knowledge-pack contents belong at the repository root so incoming agents immediately see `README.md`, `AGENTS.md` and `GOALS.md`. Downloadable ZIPs can be distributed as GitHub Release assets, outside the checked knowledge directory. That release step has not run.

## Public-data boundary

This is a public documentation repository, not a storage location for all historical data. Do not upload original source archives, credentials, cookies, tokens, saved sessions, private transcripts, account lists, large reply datasets or raw capture payloads. The original project archives remain in their source repositories and are referenced by path/hash only.

The root files are authored knowledge notes plus source metadata and static method declarations. Inspect current source separately before copying implementation behavior. Future agents can read this repository without needing access to the earlier inaccessible private destination.

## Earlier attempts

- Creating a new private `project-build-knowledge` repository was denied by the integration's `createRepository` permission.
- Reading the owner's private `indeaourproject` repository was denied with HTTP 403.
- The owner then supplied `futureidea-goal` as a public alternative. These earlier permission failures are not a reason to share credentials in chat.

## Offline use and updates

Extract the ZIP, open `README.md`, then follow `AGENTS.md`. Run:

```sh
python tools/validate_pack.py
python -B -m unittest discover -s tests -v
```

After editing knowledge files, regenerate the manifest and ZIP with `tools/build_pack.py`, keeping the output outside the knowledge directory. Revalidate links, hashes, tests and the extracted ZIP. Record a new release only after successful publication.

Refresh source references when implementations change, and preserve the distinction between owner-confirmed goals, historical observations and new recommendations.
