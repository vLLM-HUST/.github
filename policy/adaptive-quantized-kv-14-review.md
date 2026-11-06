# Exact Adaptive Quantized KV validation-document review

Scope: `vLLM-HUST/vllm-ascend-adaptive-quantized-kv-hust#14`, reviewed head
`f0ab2f1388492962bca0805f4dae667e2b94cf1b`, base
`9a6f45a7e06aa93196f0395c8bd5b2b4166d9292`. The ledger binds the two flagged
documents to their exact Git blobs and complete GitHub diff fingerprints. Any
byte change, missing diff, different PR, or different repository requires a new
review.

Both documents define prospective, fail-closed validation boundaries. They do
not contain a completed benchmark result or claim that the requested Qwen3.5
run occurred. The execution checklist keeps all completion boxes unchecked and
requires exact accepted revisions, artifact digests, an exclusive TP2 lease,
correctness evidence, cleanup, and a mechanically validated result before a run
can be called complete.

The result-validation document defines synthetic schema examples and fixed
decision gates for one preregistered baseline/treatment pair. It explicitly
keeps general performance, quality, release, and public-surface claims disabled.
The associated validator rejects missing or reused artifacts, identity and
digest drift, output mismatch, safety failures, and incomplete cleanup.

The project-side reconstruction ran 264 tests, Ruff check and format, package
build, and inert-distribution validation successfully. The original stacked PR
also passed Python 3.10, 3.12, 3.14 and CPU-component CI. Current hosted jobs did
not start because the organization Actions account reported a billing/spending
limit error; that infrastructure failure is not treated as test evidence.

This central entry approves only custody of the exact two documentation changes.
It does not authorize model execution, attest hardware results, approve a
performance result, waive target CI, or exempt future evidence changes.
