# Exact custody review: vllm-hust-bidkv PR 15

Reviewed by Codex under the repository owner’s explicit instruction to finish
the oldest actionable organization PRs. This is an exact code/data-custody
review, not independent human approval, a new hardware run, or acceptance of a
broader performance claim.

Scope: `vLLM-HUST/vllm-hust-bidkv#15`, reviewed head
`0b021653d46b7dd7e3dcf102aeb26994e9359050`, base
`8394bdeb09353337199f27497e40f8202bcfefad`. The two entries bind each Git
blob and the complete GitHub diff metadata; changed bytes require a new review.

## Findings

`paper/EVIDENCE_LEDGER.md` is a bounded claim ledger, not raw benchmark data.
It records that five TP4 cells are functional, one repeated interactive cell
is negative for the maintained formula, and one mixed cell is inconclusive. It
explicitly says raw receipts remain external and disallows general NPU,
production, cross-topology, or independent-reproduction claims. The same
boundaries appear in the paper and README.

`paper/tectonic.log` is the generated TeX build transcript retained to verify
the checked-in three-page PDF. It is not a serving trace or experimental
dataset. Two trailing spaces were normalized so `git diff --check` matches the
PR’s validation claim; TeX and PDF bytes did not change in that normalization.
The manifest pins the transcript SHA-256 together with README, TeX, bibliography,
ledger, and PDF hashes.

## Verification and trust boundary

The current source suite passes with `418 passed, 4 skipped`; all six manifest
hashes reproduce. Existing NPU evidence was not rerun. This review admits only
the two exact findings above and does not exempt the `paper/`, evidence, log,
or Markdown paths generally.

The central ledger must merge first. BidKV then updates its default-branch
trusted-policy pin and passes explicit repository/PR context in a separate PR.
Only after that base change merges is PR 15 rebuilt on the new base and
reevaluated.