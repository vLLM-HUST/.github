# vLLM-HUST Organization Profile

This repository powers the public GitHub organization profile for `vLLM-HUST`.

The content shown on the organization homepage lives in [profile/README.md](profile/README.md).

## Purpose

- present a clear overview of the repository landscape under `vLLM-HUST`
- explain how the runtime, plugin, quantization, Triton compiler, performance analyzer, AI tooling, benchmark, website, and docs repos fit together
- provide one stable landing page for contributors and users entering the workspace
- provide shared community health defaults for repositories that do not override them locally

## Repository Layout

- `profile/README.md`: the rendered GitHub organization homepage
- `.github/`: default issue templates and pull request template
- `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`: shared community health files
- `scripts/update_contributor_leaderboard.py`: maintenance automation for contributor metadata used by the profile
- `profile/core_contributors.json`: structured contributor data for rendering

## Scope Boundaries

This repository should stay narrowly focused on organization profile content and shared community health defaults.

Keep the following in sibling repositories instead:

- website pages, landing-page experiments, or published static assets in `vllm-hust-website`
- benchmark export logic and leaderboard data generation in `vllm-hust-benchmark`
- operational notes, meeting records, and internal process documents in `vllm-hust-docs`
- hardware-specific plugin or compiler code in `vllm-ascend-hust` or `triton-ascend-hust`
- AI development tooling and adapter code in `claude-code-hust`

## Notes

- organization profile rendering uses the special GitHub path `profile/README.md`
- GitHub Actions automation should avoid assuming local sibling checkouts or SSH deploy keys
- this repository is intended to stay lightweight and documentation-first by default