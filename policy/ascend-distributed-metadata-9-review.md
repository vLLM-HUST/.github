# Exact custody review: ascend-distributed-metadata PR 9

This review records the maintainer-side acceptance requested for the oldest
actionable organization pull requests. It is an exact evidence-custody review,
not a new NPU experiment or an assertion that the MOD outperforms native vLLM.

Scope: `vLLM-HUST/ascend-distributed-metadata#9`, reviewed head
`37e8f9406bddc154faaecb2afcca888b6ef026b2`, base
`c1c366b81d2fd7f4b35e9a2962a6bda48824ec1a`. The ledger binds the README Git
blob and its complete GitHub diff metadata. Any later change to that file needs
a new exact review; unrelated commits that preserve it do not inherit a path
exemption.

## Finding and review

The policy flags `README.md` because the changed paragraph contains measured
throughput and percentages. The change corrects the comparison boundary: the
reported 467.099 versus 463.376 tok/s (+0.80%) compared the DP4 word candidate
with the previous MOD, not native vLLM. It also links a detailed historical
review that labels missing path-entry and fallback rates as unknown.

The reviewed README does not add a new result, broaden the supported workload,
or claim a native-vLLM gain. The underlying qualification remains separately
versioned and the PR explicitly says no new NPU experiment was run. Retaining
the exact numbers is useful because it makes the corrected comparison auditable;
removing them would hide which earlier claim was narrowed.

## Validation and boundary

The full PR was synchronized with current main before review. On Python 3.12,
the repository test suite passed with `PYTHONPATH=src` (56 passed, 3 skipped),
and `git diff --check` passed. The new observer is disabled by default, treats
missing telemetry as unknown, and its documentation states that diagnostic
polling/counters perturb execution and do not qualify performance.

This entry approves custody only for the exact README diff. It does not approve
future result files, raw logs, benchmark data, NPU performance, or a release.
The measured-data heuristics, complete PR-file validation, branch protections,
and organization debt baseline remain unchanged.
