#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


REPO_SPECS = [
    {
        "name": "vllm-hust",
        "url": "git@github.com:vLLM-HUST/vllm-hust.git",
        "branch": "main",
        "upstream": "git@github.com:vllm-project/vllm.git",
        "upstream_remote": "upstream",
        "upstream_branch": "main",
    },
    {
        "name": "vllm-ascend-hust",
        "url": "git@github.com:vLLM-HUST/vllm-ascend-hust.git",
        "branch": "main",
        "upstream": "git@github.com:vllm-project/vllm-ascend.git",
        "upstream_remote": "upstream",
        "upstream_branch": "main",
    },
    {
        "name": "vllm-hust-benchmark",
        "url": "git@github.com:vLLM-HUST/vllm-hust-benchmark.git",
        "branch": "main",
    },
    {
        "name": "vllm-ascend-quant-hust",
        "url": "git@github.com:vLLM-HUST/vllm-ascend-quant-hust.git",
        "branch": "main",
        "exclude_commits": ["9d1e318"],
    },
    {
        "name": "vllm-hust-dev-hub",
        "url": "git@github.com:vLLM-HUST/vllm-hust-dev-hub.git",
        "branch": "main",
    },
    {
        "name": "vllm-hust-docs",
        "url": "git@github.com:vLLM-HUST/vllm-hust-docs.git",
        "branch": "main",
    },
    {
        "name": "vllm-hust-website",
        "url": "git@github.com:vLLM-HUST/vllm-hust-website.git",
        "branch": "main",
    },
    {
        "name": "vllm-hust-workstation",
        "url": "git@github.com:vLLM-HUST/vllm-hust-workstation.git",
        "branch": "main",
    },
    {
        "name": "vllm-hust-perf-analyzer",
        "url": "git@github.com:vLLM-HUST/vllm-hust-perf-analyzer.git",
        "branch": "main",
    },
]

CORE_REPOS = {"vllm-hust", "vllm-ascend-hust", "vllm-ascend-quant-hust"}

MAX_COMMIT_LINES = 50_000

EXCLUDED_AUTHOR_PATTERNS = (
    "github-actions[bot]",
    "dependabot",
    "copilot-swe-agent",
    "vllm-hust bot",
    "benchmark bot",
    "bot@vllm-hust.org",
)

GITHUB_LOGIN_BY_EMAIL = {
    "shuhao_zhang@hust.edu.cn": "ShuhaoZhangTony",
    "mingqiwang@hust.edu.cn": "MingqiWang-coder",
    "gxl20040702@gmail.com": "XilingGao",
    "995496585@qq.com": "KimmoZAG",
    "iliujun@msn.com": "iliujunn",
    "cubelander@users.noreply.github.com": "CubeLander",
    "49518565+cubelander@users.noreply.github.com": "CubeLander",
    "jingyuantian@hust.edu.cn": "CubeLander",
    "moonandlife@qq.com": "moonandlife",
    "1427850140k@gmail.com": "aly16-k",
    "pygonebe@outlook.com": "Pygone",
    "luoxiaohei@ppio.com": "luoxiaohei",
    "153624059+remygred@users.noreply.github.com": "Remygred",
    "2779387088@qq.com": "Remygred",
}

# Display-name overrides: git author name -> canonical display name
# Used AFTER mailmap canonicalization to fix remaining display anomalies.
NAME_MAP: dict[str, str] = {
    "GitHub Copilot": "Shuhao Zhang",
    "Remby Lis": "Remygred",
}

START_MARKER = "<!-- contributor-leaderboard:start -->"
END_MARKER = "<!-- contributor-leaderboard:end -->"
ORG_NAME = "vLLM-HUST"


@dataclass
class ContributorStats:
    name: str
    email: str
    added: int = 0
    deleted: int = 0
    commits: int = 0
    repos: set[str] = field(default_factory=set)
    # Per-repo breakdown for core-repo filtering
    per_repo_added: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    per_repo_deleted: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    per_repo_commits: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    @property
    def changed_lines(self) -> int:
        return self.added + self.deleted

    def core_changed_lines(self) -> int:
        total = 0
        for repo in CORE_REPOS:
            total += self.per_repo_added.get(repo, 0) + self.per_repo_deleted.get(repo, 0)
        return total

    def core_added(self) -> int:
        return sum(self.per_repo_added.get(r, 0) for r in CORE_REPOS)

    def core_deleted(self) -> int:
        return sum(self.per_repo_deleted.get(r, 0) for r in CORE_REPOS)

    def core_commits(self) -> int:
        return sum(self.per_repo_commits.get(r, 0) for r in CORE_REPOS)

    def core_repos(self) -> set[str]:
        return self.repos & CORE_REPOS


def run_git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def parse_identity(identity: str) -> tuple[str, str]:
    match = re.match(r"\s*(.*?)\s*<(.*?)>\s*$", identity)
    if match:
        return match.group(1).strip(), match.group(2).strip().lower()
    identity = identity.strip()
    return identity, identity.lower()


def read_mailmap(mailmap_path: Path) -> tuple[dict[str, tuple[str, str]], dict[str, tuple[str, str]]]:
    alias_identity_map: dict[str, tuple[str, str]] = {}
    alias_email_map: dict[str, tuple[str, str]] = {}
    if not mailmap_path.exists():
        return alias_identity_map, alias_email_map

    for raw_line in mailmap_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        identities = re.findall(r"[^<]*<[^>]+>", line)
        if len(identities) < 2:
            continue
        canonical_name, canonical_email = parse_identity(identities[0])
        canonical = (canonical_name, canonical_email)
        for alias in identities[1:]:
            alias_name, alias_email = parse_identity(alias)
            alias_identity_map[f"{alias_name} <{alias_email}>".lower()] = canonical
            alias_email_map[alias_email] = canonical
    return alias_identity_map, alias_email_map


def canonicalize_identity(
    name: str,
    email: str,
    alias_identity_map: dict[str, tuple[str, str]],
    alias_email_map: dict[str, tuple[str, str]],
) -> tuple[str, str]:
    identity_key = f"{name} <{email}>".lower()
    if identity_key in alias_identity_map:
        canon_name, canon_email = alias_identity_map[identity_key]
        canon_name = NAME_MAP.get(canon_name, canon_name)
        return canon_name, canon_email
    if email in alias_email_map:
        canon_name, canon_email = alias_email_map[email]
        canon_name = NAME_MAP.get(canon_name, canon_name)
        return canon_name, canon_email
    # Apply NAME_MAP even without mailmap match
    resolved_name = NAME_MAP.get(name, name)
    return resolved_name, email


def is_excluded_author_identity(name: str, email: str) -> bool:
    lowered = f"{name} <{email}>".lower()
    return any(pattern in lowered for pattern in EXCLUDED_AUTHOR_PATTERNS)


def ensure_repo_checkout(base_dir: Path, repo_spec: dict, workspace_root: Path | None) -> Path:
    repo_name = repo_spec["name"]
    if workspace_root is not None:
        candidate = workspace_root / repo_name
        if (candidate / ".git").exists():
            return candidate

    checkout_dir = base_dir / repo_name
    if checkout_dir.exists():
        return checkout_dir

    subprocess.run(
        [
            "git",
            "clone",
            "--branch",
            repo_spec["branch"],
            "--single-branch",
            repo_spec["url"],
            str(checkout_dir),
        ],
        text=True,
        check=True,
    )
    return checkout_dir



def update_contributor_stats(
    stats: dict[str, ContributorStats],
    *,
    contributor_key: str,
    display_name: str,
    display_email: str,
    repo_name: str,
    added: int,
    deleted: int,
) -> None:
    contributor = stats[contributor_key]
    contributor.name = display_name
    contributor.email = display_email
    contributor.repos.add(repo_name)
    contributor.added += added
    contributor.deleted += deleted
    contributor.per_repo_added[repo_name] += added
    contributor.per_repo_deleted[repo_name] += deleted



def _resolve_upstream_ref(repo_dir: Path, repo_spec: dict) -> str:
    """Ensure upstream remote exists, fetch it, and return the ref name (e.g. 'upstream/main')."""
    upstream_branch = repo_spec.get("upstream_branch", "main")
    fetch_target = repo_spec.get("upstream_remote")
    if fetch_target is not None:
        remotes = set(run_git(["remote"], repo_dir).split())
        if fetch_target not in remotes:
            fetch_target = None
    if fetch_target is None:
        remotes = set(run_git(["remote"], repo_dir).split())
        remote_name = "_upstream_src"
        if remote_name not in remotes:
            run_git(["remote", "add", remote_name, repo_spec["upstream"]], repo_dir)
        fetch_target = remote_name
    run_git(["fetch", fetch_target, upstream_branch], repo_dir)
    return f"{fetch_target}/{upstream_branch}"


def _compute_upstream_patch_ids(repo_dir: Path, upstream_ref: str) -> set[str]:
    """Compute patch-IDs for all non-merge upstream commits using a git pipeline."""
    proc_log = subprocess.Popen(
        ["git", "log", "-p", "--no-merges", upstream_ref],
        cwd=repo_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    proc_pid = subprocess.Popen(
        ["git", "patch-id", "--stable"],
        cwd=repo_dir,
        stdin=proc_log.stdout,
        stdout=subprocess.PIPE,
        text=True,
    )
    proc_log.stdout.close()
    output, _ = proc_pid.communicate()
    return {line.split()[0] for line in output.strip().splitlines() if line.strip()}


def _get_fork_unique_hashes(repo_dir: Path, upstream_ref: str) -> set[str]:
    """Return commit hashes unique to the fork (not cherry-picked from upstream).

    Uses patch-ID comparison: computes patch-IDs for fork first-parent commits
    and upstream commits, then returns only those fork commits whose patch-ID
    does NOT appear in the upstream set.
    """
    merge_base = run_git(["merge-base", upstream_ref, "HEAD"], repo_dir).strip()
    upstream_pids = _compute_upstream_patch_ids(repo_dir, upstream_ref)

    # Compute patch-ids for fork first-parent non-merge commits
    proc_log = subprocess.Popen(
        ["git", "log", "-p", "--first-parent", "--no-merges", f"{merge_base}..HEAD"],
        cwd=repo_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    proc_pid = subprocess.Popen(
        ["git", "patch-id", "--stable"],
        cwd=repo_dir,
        stdin=proc_log.stdout,
        stdout=subprocess.PIPE,
        text=True,
    )
    proc_log.stdout.close()
    output, _ = proc_pid.communicate()

    unique_hashes = set()
    for line in output.strip().splitlines():
        if not line.strip():
            continue
        parts = line.split()
        patch_id, commit_hash = parts[0], parts[1]
        if patch_id not in upstream_pids:
            unique_hashes.add(commit_hash)
    return unique_hashes


def get_log_output(repo_dir: Path, repo_spec: dict) -> tuple[str, set[str] | None]:
    """Get git log output for a repo.

    Returns (log_output, allowed_hashes).
    - For fork repos: allowed_hashes is the set of unique fork commit hashes;
      the caller should skip commits not in this set.
    - For non-fork repos: allowed_hashes is None (all commits are valid).
    """
    common_args = [
        "log",
        "--format=@@@%H%x09%aN <%aE>%x09%s",
        "--numstat",
        "--no-renames",
        "--no-merges",
    ]
    if "upstream" in repo_spec:
        upstream_ref = _resolve_upstream_ref(repo_dir, repo_spec)
        merge_base = run_git(["merge-base", upstream_ref, "HEAD"], repo_dir).strip()
        unique_hashes = _get_fork_unique_hashes(repo_dir, upstream_ref)
        # Get log for ALL first-parent non-merge commits from merge-base;
        # the caller will filter using unique_hashes.
        log_output = run_git(
            common_args + ["--first-parent", f"{merge_base}..HEAD"],
            repo_dir,
        )
        return log_output, unique_hashes
    return run_git(common_args, repo_dir), None



def collect_standard_repo_stats(
    repo_dir: Path,
    repo_spec: dict,
    alias_identity_map: dict[str, tuple[str, str]],
    alias_email_map: dict[str, tuple[str, str]],
    stats: dict[str, ContributorStats],
) -> None:
    exclude_prefixes = repo_spec.get("exclude_commits", [])
    log_output, allowed_hashes = get_log_output(repo_dir, repo_spec)

    # Parse commits with per-commit size tracking
    current_identity: tuple[str, str] | None = None
    current_hash: str | None = None
    commit_added = 0
    commit_deleted = 0

    def flush_commit() -> None:
        nonlocal commit_added, commit_deleted
        if current_identity is None:
            commit_added = 0
            commit_deleted = 0
            return
        total = commit_added + commit_deleted
        if total > MAX_COMMIT_LINES:
            commit_added = 0
            commit_deleted = 0
            return
        if total == 0:
            return
        canonical_name, canonical_email = current_identity
        update_contributor_stats(
            stats,
            contributor_key=canonical_email,
            display_name=canonical_name,
            display_email=canonical_email,
            repo_name=repo_spec["name"],
            added=commit_added,
            deleted=commit_deleted,
        )
        commit_added = 0
        commit_deleted = 0

    for line in log_output.splitlines():
        if line.startswith("@@@"):
            # Flush previous commit
            flush_commit()

            header = line[3:].strip()
            parts = header.split("\t", 2)
            if len(parts) < 3:
                current_identity = None
                current_hash = None
                continue

            commit_hash, identity_text, subject = parts
            current_hash = commit_hash

            # For fork repos, skip commits not in the unique set
            if allowed_hashes is not None and commit_hash not in allowed_hashes:
                current_identity = None
                continue

            # Check excluded commits
            if any(commit_hash.startswith(prefix) for prefix in exclude_prefixes):
                current_identity = None
                continue

            name, email = parse_identity(identity_text)
            if is_excluded_author_identity(name, email):
                current_identity = None
                continue

            canonical_name, canonical_email = canonicalize_identity(
                name, email, alias_identity_map, alias_email_map
            )
            current_identity = (canonical_name, canonical_email)
            # Increment commit count (single source of truth for commit counting)
            contributor = stats[canonical_email]
            contributor.name = canonical_name
            contributor.email = canonical_email
            contributor.repos.add(repo_spec["name"])
            contributor.commits += 1
            contributor.per_repo_commits[repo_spec["name"]] += 1
            continue

        if current_identity is None or not line.strip():
            continue

        parts = line.split("\t")
        if len(parts) < 3 or parts[0] == "-" or parts[1] == "-":
            continue
        commit_added += int(parts[0])
        commit_deleted += int(parts[1])

    # Flush last commit
    flush_commit()



def collect_stats(repo_root: Path, workspace_root: Path | None) -> dict[str, ContributorStats]:
    """Collect contributor stats across all repos. Returns the unified stats dict."""
    alias_identity_map, alias_email_map = read_mailmap(repo_root / ".mailmap")
    stats: dict[str, ContributorStats] = defaultdict(lambda: ContributorStats(name="", email=""))

    with tempfile.TemporaryDirectory(prefix="vllm-hust-profile-") as temp_dir:
        temp_root = Path(temp_dir)
        for repo_spec in REPO_SPECS:
            repo_dir = ensure_repo_checkout(temp_root, repo_spec, workspace_root)
            collect_standard_repo_stats(
                repo_dir,
                repo_spec,
                alias_identity_map,
                alias_email_map,
                stats,
            )

    return stats


def build_all_contributors_list(stats: dict[str, ContributorStats]) -> list[ContributorStats]:
    """All repos, sorted by changed_lines descending."""
    filtered = [item for item in stats.values() if item.changed_lines > 0]
    filtered.sort(
        key=lambda item: (item.changed_lines, item.added, item.commits, item.name.lower()),
        reverse=True,
    )
    return filtered


def build_core_contributors_list(stats: dict[str, ContributorStats]) -> list[ContributorStats]:
    """Core repos only, sorted by core_changed_lines descending."""
    filtered = [item for item in stats.values() if item.core_changed_lines() > 0]
    filtered.sort(
        key=lambda item: (item.core_changed_lines(), item.core_added(), item.commits, item.name.lower()),
        reverse=True,
    )
    return filtered


def format_number(value: int) -> str:
    return f"{value:,}"


def format_contributor_name(contributor: ContributorStats) -> str:
    login = GITHUB_LOGIN_BY_EMAIL.get(contributor.email)
    if login is None:
        return contributor.name
    return f"[{contributor.name}](https://github.com/{login})"


def build_table(contributors: list[ContributorStats], *, core_only: bool = False) -> str:
    """Build a markdown table for the given contributor list."""
    lines = [
        "| Rank | Contributor | Commits | Changed lines | Added / Deleted | Active repos |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for rank, contributor in enumerate(contributors, start=1):
        if core_only:
            changed = contributor.core_changed_lines()
            added = contributor.core_added()
            deleted = contributor.core_deleted()
            repos_count = len(contributor.core_repos())
            commits = contributor.core_commits()
        else:
            changed = contributor.changed_lines
            added = contributor.added
            deleted = contributor.deleted
            repos_count = len(contributor.repos)
            commits = contributor.commits
        lines.append(
            f"| {rank} | {format_contributor_name(contributor)} | "
            f"{format_number(commits)} | "
            f"{format_number(changed)} | "
            f"+{format_number(added)} / -{format_number(deleted)} | {repos_count} |"
        )
    return "\n".join(lines)


def build_section(
    all_contributors: list[ContributorStats],
    core_contributors: list[ContributorStats],
) -> str:
    snapshot_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    all_repo_names = ", ".join(f"`{spec['name']}`" for spec in REPO_SPECS)
    core_repo_names = ", ".join(f"`{r}`" for r in sorted(CORE_REPOS))

    lines = [
        START_MARKER,
        "## 贡献者排行榜",
        "",
        "> 身份合并规则与统计方法详见 [CONTRIBUTORS.md](../CONTRIBUTORS.md)",
        "",
        "### 组织全仓库",
        "",
        f"统计组织下 {len(REPO_SPECS)} 个仓库的 fork-only 贡献"
        "（fork 仓库去除上游 commit，其他仓库全量计入，"
        f"单次 commit >{MAX_COMMIT_LINES // 1000}k 行视为批量导入排除），"
        f"快照 `{snapshot_date}`。",
        "",
        build_table(all_contributors, core_only=False),
        "",
        "---",
        "",
        "### 核心性能仓库",
        "",
        f"仅统计直接影响推理性能的 {len(CORE_REPOS)} 个核心仓库"
        f"（{core_repo_names}），"
        f"排除所有上游/初始代码，快照 `{snapshot_date}`。",
        "",
        build_table(core_contributors, core_only=True),
        "",
        END_MARKER,
    ]
    return "\n".join(lines)


def build_contributor_payload(
    all_contributors: list[ContributorStats],
    core_contributors: list[ContributorStats],
) -> dict:
    snapshot_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _items(contributors: list[ContributorStats], core_only: bool) -> list[dict]:
        items = []
        for rank, c in enumerate(contributors, start=1):
            login = GITHUB_LOGIN_BY_EMAIL.get(c.email)
            if core_only:
                changed = c.core_changed_lines()
                added = c.core_added()
                deleted = c.core_deleted()
                repos = sorted(c.core_repos())
            else:
                changed = c.changed_lines
                added = c.added
                deleted = c.deleted
                repos = sorted(c.repos)
            items.append({
                "rank": rank,
                "name": c.name,
                "github_login": login,
                "github_url": f"https://github.com/{login}" if login else None,
                "commits": c.core_commits() if core_only else c.commits,
                "changed_lines": changed,
                "added": added,
                "deleted": deleted,
                "active_repos": len(repos),
                "repos": repos,
            })
        return items

    return {
        "updated_at": snapshot_date,
        "all_repos": {
            "scope_repos": [spec["name"] for spec in REPO_SPECS],
            "contributors": _items(all_contributors, core_only=False),
        },
        "core_repos": {
            "scope_repos": sorted(CORE_REPOS),
            "contributors": _items(core_contributors, core_only=True),
        },
    }


def sync_org_profile_contributor_data(
    repo_root: Path,
    all_contributors: list[ContributorStats],
    core_contributors: list[ContributorStats],
) -> None:
    payload = build_contributor_payload(all_contributors, core_contributors)
    data_path = repo_root / "profile" / "core_contributors.json"
    data_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sync_website_contributor_data(
    workspace_root: Path | None,
    all_contributors: list[ContributorStats],
    core_contributors: list[ContributorStats],
) -> None:
    if workspace_root is None:
        return
    website_root = workspace_root / "vllm-hust-website"
    if not (website_root / ".git").exists():
        return
    data_path = website_root / "data" / "core_contributors.json"
    payload = build_contributor_payload(all_contributors, core_contributors)
    data_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def replace_section(readme_path: Path, new_section: str) -> None:
    content = readme_path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        flags=re.DOTALL,
    )
    if pattern.search(content):
        updated = pattern.sub(new_section, content)
    else:
        heading_pattern = re.compile(r"^## 贡献者排行榜\n.*?(?=^## )", flags=re.DOTALL | re.MULTILINE)
        if heading_pattern.search(content):
            updated = heading_pattern.sub(new_section + "\n\n", content)
        else:
            raise RuntimeError("Could not find contributor leaderboard section to replace")
    readme_path.write_text(updated, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update the vLLM-HUST contributor leaderboard")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=None,
        help="Optional local workspace root containing sibling repository checkouts",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        default=False,
        help="CI mode: convert SSH git URLs to HTTPS for token-based auth",
    )
    return parser.parse_args()


def convert_urls_to_https() -> None:
    """Convert all SSH URLs in REPO_SPECS to HTTPS for CI environments."""
    for spec in REPO_SPECS:
        url = spec["url"]
        if url.startswith("git@github.com:"):
            spec["url"] = url.replace("git@github.com:", "https://github.com/")
        if "upstream" in spec:
            upstream_url = spec["upstream"]
            if upstream_url.startswith("git@github.com:"):
                spec["upstream"] = upstream_url.replace("git@github.com:", "https://github.com/")


def main() -> None:
    args = parse_args()

    if args.ci:
        convert_urls_to_https()

    repo_root = Path(__file__).resolve().parents[1]
    workspace_root = args.workspace_root
    if workspace_root is None:
        candidate = repo_root.parent
        workspace_root = candidate if (candidate / "vllm-hust").exists() else None

    stats = collect_stats(repo_root, workspace_root)
    all_contributors = build_all_contributors_list(stats)
    core_contributors = build_core_contributors_list(stats)

    sync_org_profile_contributor_data(repo_root, all_contributors, core_contributors)
    replace_section(
        repo_root / "profile" / "README.md",
        build_section(all_contributors, core_contributors),
    )
    sync_website_contributor_data(workspace_root, all_contributors, core_contributors)

    print(f"Updated leaderboard: {len(all_contributors)} contributors (all), "
          f"{len(core_contributors)} contributors (core)")


if __name__ == "__main__":
    main()
