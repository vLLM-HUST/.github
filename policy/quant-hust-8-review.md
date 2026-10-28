# Exact custody review: vllm-ascend-quant-hust PR 8

Reviewed by Claude Code under the repository owner's explicit instruction to
complete the trusted review of one heuristic finding without weakening the
gate. This is a recorded code/data-custody review, not an assertion of
independent human approval and not a hardware or accuracy acceptance.

Scope: `vLLM-HUST/vllm-ascend-quant-hust#8`, reviewed head
`1d36d36e7e7cececf8ffb6ae152aa05dd7307fd1`, base merge
`db3f55632263997744a3125abc78324edeb0643b`. The ledger binds the file's Git
blob and complete GitHub diff metadata. A later push that changes this file's
bytes invalidates the fingerprint and needs a fresh review; unrelated commits
that leave the file untouched do not.

## Finding

`contracts/ascend-quant-evidence-v1.schema.json` is flagged by `MEASURED`
because the document is JSON and its contract identifiers contain `ttft` and
`tpot`, each followed within the heuristic's 60-character window by a digit
(`p99_...`, `"minimum": 0`).

## What the file is, and why it is not benchmark evidence

The file is a JSON Schema (draft 2020-12) that defines the closed
BF16/W8A8/W4A4/W4A8 evaluation record validated by `ascend-quant-toolkit
validate-evidence`. It contains no measured value, no dataset, no request log,
no timing and no run result: the only numbers are schema constraints
(`"minimum": 0`, `"minItems": 1`, `"minLength": 1`) and the `p99_` prefix in
field names. It ships as `share/ascend-quant-toolkit/contracts/` package data
and is the published shape existing evidence records are written against.

The file cannot be reworded without changing contract 1.1.0. The property
names `mean_ttft_ms`, `p99_ttft_ms`, `mean_tpot_ms` and `p99_tpot_ms` are the
contract, and dropping their numeric bounds would let the schema accept records
the toolkit rejects. Reformatting the JSON only to move digits out of the
heuristic's window would evade the check instead of answering it, so the bytes
are left exactly as published.

The measured results this repository used to carry are no longer in the diff:
the checkpoint record moved to `docs/artifacts/` with its duplicated PPL table
deleted, and those numbers are recorded only in
`vLLM-HUST/vllm-hust-benchmark/reports/qwen35-w4a8-gdnw8a8-tp1-20261023/`.
This review covers the schema file and nothing else.

## Trust boundary and rollout

The central ledger must merge first; this repository's caller then pins that
merged central commit and passes `--repository`/`--pull-request` in a separate
base-branch PR under the old policy. Only after that base change merges is PR 8
reevaluated. The check executes no target PR code and cannot read a target PR's
own ledger. `DATA_PARTS`, `DATA_SUFFIXES`, `MEASURED`, complete-list
validation, removal semantics, branch protection and the organization debt
baseline are unchanged.

Review checkpoint: requested exact trusted review | 149-line added contract |
no measured values, dataset, log or run result | retain heuristics, no path or
file-type exemption.
