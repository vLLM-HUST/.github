# Upstream sync recovery: 2026-09-03

Last verified: **2026-09-03 00:33 UTC**. This is a source/automation verification,
not a model/runtime compatibility or deployment approval.

## Result and remaining administrator action

All seven managed fork defaults contain their observed upstream main snapshots,
preserve previous fork heads, and have a successful final dispatched sync run.
All remediation commits are on the respective remote main branches.

**Dedicated workflow-write credentials are still not configured.** The action
supports a repository-scoped App or dedicated token, but a successful source-only
merge or no-op does not prove that the next upstream workflow-file change will
succeed. Follow [credential setup](README.md#credentials-required-for-upstream-workflow-changes).
Do not copy a privileged personal CLI token into shared Actions secrets.
Credential-related incidents should remain open until a correctly scoped
credential has been installed and workflow-file synchronization has been verified.

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
