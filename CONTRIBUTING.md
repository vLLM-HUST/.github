# Contributing to vLLM-HUST

This repository provides the default contribution guidance for the `vLLM-HUST` GitHub organization.

Repository-specific rules may be stricter. When they exist, follow the local `AGENTS.md`, `copilot-instructions.md`, `CONTRIBUTING.md`, workflow docs, and test requirements first.

## Contribution Principles

`vLLM-HUST` is organized around an upstream-compatible engineering model.

Default expectations:

- prefer merge-safe changes over fork-only rewrites
- isolate hardware-specific behavior behind plugins, managers, registries, feature flags, or deployment tooling
- keep benchmark, docs, and website flows aligned with the runtime they validate
- fix the root cause when practical, not just the visible symptom

## Start In The Right Repository

- use `vllm-hust` for runtime, serving, CLI, and inference-path changes
- use `vllm-ascend-hust` for Ascend plugin work
- use `ascend-runtime-manager` for environment and setup tooling
- use `vllm-hust-dev-hub` for workspace bootstrap and CI helper flows
- use `vllm-hust-benchmark` for orchestration and leaderboard export logic
- use `vllm-hust-website` for site and published snapshot rendering
- use `vllm-hust-workstation` for user-facing web experience changes
- use `vllm-hust-docs` for operational docs and sync notes

## Before You Open A Pull Request

1. Make sure the change belongs in that repository and not better upstream.
2. Run the narrowest relevant validation you can, then record the exact commands.
3. Redact secrets and private infrastructure details from examples and logs.
4. Update docs when user-facing behavior or workflow expectations change.
5. Keep changes focused; avoid unrelated cleanup in the same PR.

## Pull Request Expectations

Unless the target repository says otherwise, a good PR should include:

- a short summary of what changed and why
- the repository scope and any affected sibling repos
- exact tests, smoke checks, or manual validation performed
- explicit risks or compatibility tradeoffs
- links to related issues, upstream PRs, or design notes when relevant

## Security And Secrets

Never commit or paste live tokens, PATs, private endpoints, or credentials.

If a secret is accidentally exposed, rotate or revoke it first, then follow [SECURITY.md](SECURITY.md).

## Community Standards

All contributions are also covered by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).