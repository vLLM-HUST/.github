# Upstream synchronization

`hust-upstream-sync.yml` is the shared source for `.github/workflows/sync-upstream.yml`
in the HUST core, Ascend, Metal, Triton Ascend, SGLang, Mooncake and production-stack
forks. Copy the template while preserving each repository's staggered cron schedule.
It executes only GitHub metadata/merge APIs on a hosted runner: no checkout,
dependency install, model download, production deployment or hardware access.

## Credentials (required for upstream workflow changes)

The default `GITHUB_TOKEN` can merge source-only changes, but cannot write changed
workflow files. `permissions: contents: write` does not grant this capability.
Do not add a nonexistent `permissions: workflows` key.

Preferred configuration:

1. Install a dedicated GitHub App on only the target forks, granting repository
   **Contents: read/write** and **Workflows: read/write**.
2. Set `UPSTREAM_SYNC_APP_CLIENT_ID` as a repository or organization Actions variable.
3. Store its private key in `UPSTREAM_SYNC_APP_PRIVATE_KEY`, scoped to those forks.
4. The pinned `actions/create-github-app-token` action mints a token restricted to
   the current repository and revokes it after the job. Issues use `GITHUB_TOKEN`,
   not the App token.

Alternatively, store a dedicated, expiring fine-grained token in
`UPSTREAM_SYNC_TOKEN`, scoped to those repositories with the same permissions.
If organizational policy requires a classic token, it needs `repo` and `workflow`;
prefer the narrower App instead. Never copy an administrator's personal CLI token
into a shared secret. Credential creation/installation requires administrator
approval. Secret values must not appear in logs, issue bodies or documentation.

App configuration takes precedence over the dedicated token, then `GITHUB_TOKEN`.
An incomplete App configuration fails rather than silently falling back. The final
fallback warns about its limitations. A successful no-op without dedicated
credentials does **not** close an existing incident: it cannot prove that the next
workflow-file update will succeed.

## Verification and recovery

Dispatch on the default branch only. Review the run summary's before/upstream/after
SHAs and two ancestry checks; success must preserve both the fork's previous HEAD
and the observed upstream HEAD. No reset, force push or overwrite-sync is used.
The upstream may advance after the snapshot; that newer commit belongs to the next
run. A GitHub `409` is a genuine conflict, `422` mentioning workflows is a workflow
permission check failure (possibly a permission-check timeout), and `401/403`
requires checking credentials, SSO, installation scope or branch rules. Other API
errors remain errors, not fabricated success. Retrying is safe after diagnosis.

The merge API uses the exact observed upstream SHA rather than a moving branch.
Already synchronized snapshots return after a read-only ancestry check, avoiding
unnecessary writes and their permission checks. After an actual merge, the response
SHA is recorded and branch/compare reads are retried at most five times (two-second
intervals) to tolerate GitHub read-after-write lag. The mutation is never retried;
persistent ancestry failures still fail closed.

Its commit message includes `[skip ci]`: unlike `GITHUB_TOKEN`, a dedicated App/PAT
would otherwise trigger imported push CI, including hardware tests and releases.
This preserves the previous sync-only behavior. Explicit product validation and
deployment remain separate; this automation must not be used to bypass required
branch checks. If branch protection blocks the merge, retain that failure and
follow the repository's PR/check process instead of weakening the rules.

Resolve conflicts in an isolated checkout and retain fork-only changes. Verify the
resolution with focused tests before merging. This sync does not update any product
gitlinks or prove runtime compatibility. Product deployments remain pinned and
must go through their own validation.

Failure issues retain the existing exact title and owner; notifications use a body
file and verify the posted bytes. Slack is optional and cannot hide the original
failure. Success remains silent except for closing a recovered incident when a
dedicated credential was used.

Run the CPU-only template contract and shell-behavior tests with:

```sh
python -m pytest tests/test_upstream_sync_workflow.py
```

References: [fork sync API](https://docs.github.com/en/rest/branches/branches#sync-a-fork-branch-with-the-upstream-repository),
[App token action](https://github.com/actions/create-github-app-token).
