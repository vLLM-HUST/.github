"""Fail-closed PR policy and organization-wide evidence drift audit.

An inventory is a debt baseline, NOT admission of existing evidence. No PR code
is imported or executed. Path/content heuristics cannot replace human review.
"""

import argparse
import concurrent.futures
import hashlib
import json
import re
import subprocess
from pathlib import Path

ORG = "vLLM-HUST"
CENTRAL = "vllm-hust-benchmark"
DATA_PARTS = {"data", "datasets", "results", "evidence", "receipts", "runs", "traces"}
DATA_SUFFIXES = (
    ".csv",
    ".tsv",
    ".jsonl",
    ".ndjson",
    ".parquet",
    ".arrow",
    ".log",
    ".log.gz",
    ".prom",
)
MEASURED = re.compile(
    r"(?:ttft|tpot|throughput|latency|tokens/s|实测|吞吐|延迟).{0,60}\d", re.I
)


def candidate(path):
    parts = path.lower().split("/")
    return bool(DATA_PARTS.intersection(parts[:-1])) or path.lower().endswith(
        DATA_SUFFIXES
    )


def check_pr(pages, expected):
    rows = [row for page in pages for row in page]
    if len(rows) != expected or len({r["filename"] for r in rows}) != expected:
        raise ValueError("Incomplete PR file listing")
    violations = []
    for row in rows:
        if row["status"] == "removed":
            continue
        path = row["filename"]
        previous = row.get("previous_filename", "")
        added = "\n".join(
            line[1:]
            for line in row.get("patch", "").splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
        prose = path.lower().endswith((".md", ".rst", ".txt", ".json", ".yaml", ".yml"))
        if candidate(path) or candidate(previous) or (prose and MEASURED.search(added)):
            violations.append(path)
        elif prose and "patch" not in row:
            violations.append(path + " (missing diff: manual evidence review required)")
    return violations


def review_fingerprint(row):
    """Bind a review to a complete GitHub file diff, not a reusable path allowlist."""
    if not re.fullmatch(r"[0-9a-f]{40}", row.get("sha", "")):
        raise ValueError("Review requires a Git blob identity")
    if not isinstance(row.get("patch"), str) or not row["patch"]:
        raise ValueError("Review requires the complete textual diff")
    fields = (
        "filename",
        "previous_filename",
        "status",
        "sha",
        "patch",
        "additions",
        "deletions",
        "changes",
    )
    bound = {key: row.get(key) for key in fields}
    return hashlib.sha256(json.dumps(bound, sort_keys=True).encode()).hexdigest()


def apply_trusted_reviews(pages, violations, repository, pull_request, ledger):
    """Only centrally committed exact reviews can resolve heuristic findings."""
    if ledger.get("schema") != 1 or not isinstance(ledger.get("reviews"), list):
        raise ValueError("Invalid trusted review ledger")
    approved = set()
    rows = {row["filename"]: row for page in pages for row in page}
    for review in ledger["reviews"]:
        if review["repository"] != repository or review["pull_request"] != pull_request:
            continue
        path = review["path"]
        row = rows.get(path)
        if row is None or path not in violations:
            continue
        if review_fingerprint(row) == review["fingerprint_sha256"]:
            approved.add(path)
    return [path for path in violations if path not in approved]


def api(endpoint):
    return json.loads(
        subprocess.check_output(["gh", "api", "--paginate", "--slurp", endpoint])
    )


def tree(repo, revision):
    root = api(f"repos/{ORG}/{repo}/git/trees/{revision}?recursive=1")[0]
    if not root.get("truncated"):
        return root["tree"]
    result = []

    def visit(sha, prefix=""):
        recursive = api(f"repos/{ORG}/{repo}/git/trees/{sha}?recursive=1")[0]
        if not recursive.get("truncated"):
            result.extend(
                {**entry, "path": prefix + entry["path"]}
                for entry in recursive["tree"]
                if entry["type"] == "blob"
            )
            return
        page = api(f"repos/{ORG}/{repo}/git/trees/{sha}")[0]
        if page.get("truncated"):
            raise ValueError("Non-recursive tree truncated: incomplete inventory")
        for entry in page["tree"]:
            path = prefix + entry["path"]
            if entry["type"] == "tree":
                visit(entry["sha"], path + "/")
            elif entry["type"] == "blob":
                result.append({**entry, "path": path})

    visit(root["sha"])
    return result


def auditable_repo(repo):
    # Public audit output must never disclose private repository metadata.
    return (
        repo.get("visibility") == "public"
        and not repo["archived"]
        and repo["name"] != CENTRAL
    )


def inventory():
    repos = [r for page in api(f"orgs/{ORG}/repos?per_page=100") for r in page]
    repos = [r for r in repos if auditable_repo(r)]

    def inspect(repo):
        name = repo["name"]
        entries = tree(name, repo["default_branch"])
        assets = {}
        for page in api(f"repos/{ORG}/{name}/releases?per_page=100"):
            for release in page:
                for asset in release["assets"]:
                    assets[str(asset["id"])] = {
                        "name": asset["name"],
                        "digest": asset.get("digest"),
                        "bytes": asset["size"],
                        "tag": release["tag_name"],
                        "draft": release["draft"],
                        "prerelease": release["prerelease"],
                    }
        state = {
            "branch": repo["default_branch"],
            "paths": {
                e["path"]: e["sha"]
                for e in entries
                if e["type"] == "blob" and candidate(e["path"])
            },
            "assets": assets,
        }
        print(name, "inventoried", flush=True)
        return name, state

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        return dict(pool.map(inspect, repos))


def drift(baseline, current):
    findings = []
    for repo, state in current.items():
        old = baseline.get(repo, {})
        for kind in ("paths", "assets"):
            for key, value in state[kind].items():
                if old.get(kind, {}).get(key) != value:
                    findings.append(f"{repo}: {kind}: {key}")
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["pr", "snapshot", "audit"])
    parser.add_argument("--files", type=Path)
    parser.add_argument("--expected", type=int)
    parser.add_argument("--repository")
    parser.add_argument("--pull-request", type=int)
    parser.add_argument(
        "--baseline", type=Path, default=Path("policy/evidence-debt-baseline.json")
    )
    args = parser.parse_args()
    if args.mode == "pr":
        pages = json.loads(args.files.read_text())
        violations = check_pr(pages, args.expected)
        if bool(args.repository) != bool(args.pull_request):
            raise ValueError("Both trusted repository and PR context are required")
        if args.repository and args.pull_request:
            # No CLI-supplied ledger or PR checkout: this file belongs to the pinned
            # central policy checkout. Existing callers without context stay strict.
            ledger_path = (
                Path(__file__).resolve().parents[1] / "policy/reviewed-pr-changes.json"
            )
            violations = apply_trusted_reviews(
                pages,
                violations,
                args.repository,
                args.pull_request,
                json.loads(ledger_path.read_text()),
            )
    else:
        current = inventory()
        if args.mode == "snapshot":
            if args.baseline.exists():
                raise ValueError("Refusing to silently replace a reviewed baseline")
            args.baseline.parent.mkdir(parents=True, exist_ok=True)
            args.baseline.write_text(
                json.dumps(current, indent=2, sort_keys=True) + "\n"
            )
            return
        violations = drift(json.loads(args.baseline.read_text()), current)
    for violation in violations:
        print("Evidence custody review required:", violation)
    raise SystemExit(bool(violations))


if __name__ == "__main__":
    main()
