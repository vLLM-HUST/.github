# Upstream sync recovery: 2026-09-03

Initial source verification: **2026-09-03 00:33 UTC**. The credential follow-up below
supersedes the initial missing-credential limitation. This is a source/automation
verification, not a model/runtime compatibility or deployment approval.

## Initial result and credential follow-up

All seven managed fork defaults contain their observed upstream main snapshots,
preserve previous fork heads, and have a successful final dispatched sync run.
All remediation commits are on the respective remote main branches.

At the initial 00:33 UTC verification, no workflow-write credential was configured;
the green runs alone did not resolve that limitation. Following explicit owner
authorization, organization Actions secret `UPSTREAM_SYNC_TOKEN` was configured
at **2026-09-03 01:15:16 UTC**, with `selected` visibility and exactly the seven
managed forks. The token was transferred through stdin and client-side encryption,
not printed, placed in command arguments or saved in repository/task files.

All seven follow-up runs confirmed `HAS_SYNC_CREDENTIAL=true` and succeeded. The
configured PAT has the required `repo` and `workflow` scopes. It is an authorized
existing personal credential, **not** a least-privilege dedicated App: selected
secret visibility restricts distribution but does not reduce the PAT's original
API permissions. Migration to a dedicated App/token remains a hardening
recommendation, not an unconfigured-secret blocker. See
[credential setup](README.md#credentials-required-for-upstream-workflow-changes).

## Initial failures

- Ascend: run [33683226641](https://github.com/vLLM-HUST/vllm-ascend-hust/actions/runs/33683226641), HTTP 422, refused workflow `.github/workflows/scripts/test_config.yaml`.
- Triton Ascend: run [33683935502](https://github.com/vLLM-HUST/triton-ascend-hust/actions/runs/33683935502), HTTP 422, refused `.github/workflows/Ascend950-ci.yml`.
- Mooncake: run [33684260812](https://github.com/vLLM-HUST/mooncake-hust/actions/runs/33684260812), HTTP 422, refused `.github/workflows/ci_ascend.yml`.
- SGLang: run [33684175414](https://github.com/vLLM-HUST/sglang-hust/actions/runs/33684175414), HTTP 422, workflow-permission determination timed out.
- Metal: run [33683590179](https://github.com/vLLM-HUST/vllm-metal-hust/actions/runs/33683590179), HTTP 409, a real conflict in `vllm_metal/compat.py`.

Metal resolution [a99e5e7](https://github.com/vLLM-HUST/vllm-metal-hust/commit/a99e5e7ad67df6fe4f2061ec574bf49aa853b693)
retains the HUST mirror-query redirect patch and the new upstream tokenizer and
null-block compatibility functions. It does not choose one side wholesale.

## End-to-end findings retained, not hidden

The first repaired dispatch was not fully green:

- Core [33699458559](https://github.com/vLLM-HUST/vllm-hust/actions/runs/33699458559)
  encountered integration HTTP 403 on an unnecessary no-op merge POST.
- SGLang [33699461329](https://github.com/vLLM-HUST/sglang-hust/actions/runs/33699461329)
  merged successfully, but an immediate branch read returned a stale HEAD and
  caused a false ancestry failure. The resulting commit
  `ec6e65b4aa03d91fcd462df978603afb2980af81` has both expected parents.

The second patch makes no-ops read-only, records the returned merge SHA, and
retries only branch/compare reads (five attempts, two-second intervals). A genuine
persistent ancestry failure still fails. Regression tests cover both cases.
The final SGLang run performed another real source merge to
`31cc5e8e65235a1b855f8ae7ead64acc70424ab7` and passed, so validation was not
limited to synthetic shell tests.

## Verified remote identities

Ahead/behind is relative to the exact upstream snapshot shown, not a count of
functional HUST patches. It includes merge and automation commits. Upstream
branches continue to advance after this observation.

| Fork | Final remote main | Upstream snapshot | Ahead / behind | Final Actions run |
| --- | --- | --- | --- | --- |
| vllm-hust | [`021f4afa6a3de2973d27e1ad85a51196bba88c6c`](https://github.com/vLLM-HUST/vllm-hust/commit/021f4afa6a3de2973d27e1ad85a51196bba88c6c) | [`ad127d9a0fb16c92de563e674e3737463e7f8688`](https://github.com/vllm-project/vllm/commit/ad127d9a0fb16c92de563e674e3737463e7f8688) | 18 / 0 | [success](https://github.com/vLLM-HUST/vllm-hust/actions/runs/33699894953) |
| vllm-ascend-hust | [`30de999084d578f8abc822cc78c017e622b2d793`](https://github.com/vLLM-HUST/vllm-ascend-hust/commit/30de999084d578f8abc822cc78c017e622b2d793) | [`2825e368b0ee0cd5ecfddc075cee92be658508f9`](https://github.com/vllm-project/vllm-ascend/commit/2825e368b0ee0cd5ecfddc075cee92be658508f9) | 45 / 0 | [success](https://github.com/vLLM-HUST/vllm-ascend-hust/actions/runs/33699894634) |
| triton-ascend-hust | [`148a35c01391c6bb3d34cdbc7d485a4e82480048`](https://github.com/vLLM-HUST/triton-ascend-hust/commit/148a35c01391c6bb3d34cdbc7d485a4e82480048) | [`5377005e8f980a1a8ad8d02fe53b85d1f503c424`](https://github.com/triton-lang/triton-ascend/commit/5377005e8f980a1a8ad8d02fe53b85d1f503c424) | 17 / 0 | [success](https://github.com/vLLM-HUST/triton-ascend-hust/actions/runs/33699894767) |
| vllm-metal-hust | [`a1cc8d4c9c9d0dfaf4d9088bb3ba6b0143b975f8`](https://github.com/vLLM-HUST/vllm-metal-hust/commit/a1cc8d4c9c9d0dfaf4d9088bb3ba6b0143b975f8) | [`07f1987fe9a11cf3da29f24983d9ffffc080bd7f`](https://github.com/vllm-project/vllm-metal/commit/07f1987fe9a11cf3da29f24983d9ffffc080bd7f) | 5 / 0 | [success](https://github.com/vLLM-HUST/vllm-metal-hust/actions/runs/33699894711) |
| sglang-hust | [`31cc5e8e65235a1b855f8ae7ead64acc70424ab7`](https://github.com/vLLM-HUST/sglang-hust/commit/31cc5e8e65235a1b855f8ae7ead64acc70424ab7) | [`80e8302d03dc2cc458435f623bb92de7b498b3b5`](https://github.com/sgl-project/sglang/commit/80e8302d03dc2cc458435f623bb92de7b498b3b5) | 6 / 0 | [success](https://github.com/vLLM-HUST/sglang-hust/actions/runs/33699894571) |
| mooncake-hust | [`4f5562c2518c9448913e5a8961622af7d9227c53`](https://github.com/vLLM-HUST/mooncake-hust/commit/4f5562c2518c9448913e5a8961622af7d9227c53) | [`408b831bfeff5855402c6e69163a1d1589fff833`](https://github.com/kvcache-ai/Mooncake/commit/408b831bfeff5855402c6e69163a1d1589fff833) | 6 / 0 | [success](https://github.com/vLLM-HUST/mooncake-hust/actions/runs/33699894770) |
| production-stack-hust | [`00f27f3b08d518580cdcdb00815aea2685673de3`](https://github.com/vLLM-HUST/production-stack-hust/commit/00f27f3b08d518580cdcdb00815aea2685673de3) | [`fc00f98b55961f3fa8e173fcd8fff1514d867128`](https://github.com/vllm-project/production-stack/commit/fc00f98b55961f3fa8e173fcd8fff1514d867128) | 7 / 0 | [success](https://github.com/vLLM-HUST/production-stack-hust/actions/runs/33699894986) |

The SGLang run began at `0e3166a37452b11767f492e7a23f62614d5679fd`;
the table records the resulting merged main, not just the run's starting SHA.

## Tests and scope

- Organization repository: `python -m pytest tests -q`: **37 passed**
  (20 sync behavior/contracts, 17 existing contributor tests).
- Shared-template GitHub CI:
  [33699812358](https://github.com/vLLM-HUST/.github/actions/runs/33699812358), success.
- `actionlint 1.7.12`: template, its test workflow and all seven deployed callers pass.
- Metal: `python -m unittest discover -s tests -p test_hust_sync_compat.py -v`:
  **3 passed**, covering registration coexistence, mirror redirect query/idempotence,
  and the upstream null-block reservation. No Apple GPU execution was performed.
- Ruff check/format and Mooncake touched-file pre-commit checks pass.
- Initial Mooncake lint setup failed because a sparse checkout omitted the config;
  after materializing only the lint configuration/scripts, the check passed.
- Original worktrees, product submodule pins, services, containers, proxies and
  production hardware were not changed. No force push or external upstream PR was
  used. Merge commits retain the original sync-only CI-trigger semantics via
  `[skip ci]`; runtime validation and deployment remain separate.

## Credential-backed verification at 01:15 UTC

| Fork | Actions run | Sync credential present | Result | Resulting main |
| --- | --- | --- | --- | --- |
| vllm-hust | [33702920975](https://github.com/vLLM-HUST/vllm-hust/actions/runs/33702920975) | true | success (real merge) | `86ffadbd8d27d6b17c7053420254caa239158774` |
| vllm-ascend-hust | [33702920331](https://github.com/vLLM-HUST/vllm-ascend-hust/actions/runs/33702920331) | true | success (real merge) | `1d2f1f87a7449cd86fd6c2946174224ee81def52` |
| triton-ascend-hust | [33702921859](https://github.com/vLLM-HUST/triton-ascend-hust/actions/runs/33702921859) | true | success (already synchronized) | `148a35c01391c6bb3d34cdbc7d485a4e82480048` |
| vllm-metal-hust | [33702921330](https://github.com/vLLM-HUST/vllm-metal-hust/actions/runs/33702921330) | true | success (already synchronized) | `a1cc8d4c9c9d0dfaf4d9088bb3ba6b0143b975f8` |
| sglang-hust | [33702920642](https://github.com/vLLM-HUST/sglang-hust/actions/runs/33702920642) | true | success (real merge) | `bee0ebc7148483846a4973ac2fadf480d48067cd` |
| mooncake-hust | [33702920628](https://github.com/vLLM-HUST/mooncake-hust/actions/runs/33702920628) | true | success (already synchronized) | `4f5562c2518c9448913e5a8961622af7d9227c53` |
| production-stack-hust | [33702920763](https://github.com/vLLM-HUST/production-stack-hust/actions/runs/33702920763) | true | success (already synchronized) | `00f27f3b08d518580cdcdb00815aea2685673de3` |

The Ascend run merged upstream `6d02e22f078e59eb4b7947a887116151ad8eb100`
into `1d2f1f87a7449cd86fd6c2946174224ee81def52`, including these changed files:

- `.github/workflows/scripts/coverage.py`
- `.github/workflows/scripts/select_tests.py`
- `.github/workflows/scripts/test_config.yaml`
- `.github/workflows/scripts/update_estimated_times.py`

This is a real workflow-file merge by GitHub Actions using the configured secret,
including the path originally rejected with HTTP 422. Core and SGLang also
performed real source merges; other forks were already synchronized. All runs
preserved ancestry and reached the credential-gated recovery step. The organization
unit suite was rerun unchanged: **37 passed**. No runtime deployment or NPU work
was performed. Token rotation/revocation must be accompanied by secret replacement;
an expiring least-privilege App remains preferable for long-term operation.
