# Reviewed implementation drift

Issue: vLLM-HUST/vllm-hust-benchmark#326.

The public organization inventory on 2026-10-23 reports two changed candidate
paths in `sglang-hust`. The complete blob diffs were reviewed against the debt
baseline; both are implementation code, not committed inputs or measurements:

- `python/sglang/benchmark/datasets/common.py`: factors random token selection
  into `gen_prompt_ids`; text generation delegates to it.
- `python/sglang/benchmark/datasets/generated_shared_prefix.py`: supports token-ID
  prompts, distinguishes their cache key, validates single-turn use, and computes
  generated prompt lengths. It does not embed a measured result or dataset dump.

Observed default-branch commit: `8ba1e67d246a2a45012ae896d3a927467af81ede`.
Only these two reviewed blob fingerprints are refreshed. Existing migration debt
is not erased; no path exemption, policy relaxation, device execution, or approval
of `sglang-hust#2` is implied. Future content changes still trigger drift review.
