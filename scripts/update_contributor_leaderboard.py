#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import tempfile
from collections import defaultdict
from dataclasses import dataclass
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
        "upstream_branch": "main",
    },
    {
        "name": "vllm-hust-benchmark",
        "url": "git@github.com:vLLM-HUST/vllm-hust-benchmark.git",
        "branch": "main",
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
]

EXCLUDED_AUTHOR_PATTERNS = (
    "github-actions[bot]",
    "dependabot",
    "copilot",
)

START_MARKER = "<!-- contributor-leaderboard:start -->"
END_MARKER = "<!-- contributor-leaderboard:end -->"


@dataclass
class ContributorStats:
    name: str
    email: str
    added: int = 0
    deleted: int = 0
    commits: int = 0
    repos: set[str] | None = None

    def __post_init__(self) -> None:
        if self.repos is None:
            self.repos = set()

    @property
    def changed_lines(self) -> int:
        return self.added + self.deleted


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
        return alias_identity_map[identity_key]
    if email in alias_email_map:
        return alias_email_map[email]
    return name, email


def ensure_repo_checkout(base_dir: Path, repo_spec: dict[str, str], workspace_root: Path | None) -> Path:
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


def get_log_output(repo_dir: Path, repo_spec: dict[str, str]) -> str:
    common_args = ["log", "--format=@@@%aN <%aE>", "--numstat", "--no-renames", "--no-merges"]
    if "upstream" in repo_spec:
        fetch_target = repo_spec.get("upstream_remote")
        if fetch_target is not None:
            remotes = set(run_git(["remote"], repo_dir).split())
            if fetch_target not in remotes:
                fetch_target = None
        if fetch_target is None:
            fetch_target = repo_spec["upstream"]
        run_git(["fetch", fetch_target, repo_spec.get("upstream_branch", "main")], repo_dir)
        revspec = "FETCH_HEAD...HEAD"
        return run_git(common_args + ["--right-only", "--cherry-pick", revspec], repo_dir)
    return run_git(common_args, repo_dir)


def collect_stats(repo_root: Path, workspace_root: Path | None) -> list[ContributorStats]:
    alias_identity_map, alias_email_map = read_mailmap(repo_root / ".mailmap")
    stats: dict[str, ContributorStats] = defaultdict(lambda: ContributorStats(name="", email=""))

    with tempfile.TemporaryDirectory(prefix="vllm-hust-profile-") as temp_dir:
        temp_root = Path(temp_dir)
        for repo_spec in REPO_SPECS:
            repo_dir = ensure_repo_checkout(temp_root, repo_spec, workspace_root)
            log_output = get_log_output(repo_dir, repo_spec)
            current_email: str | None = None
            for line in log_output.splitlines():
                if line.startswith("@@@"):
                    name, email = parse_identity(line[3:].strip())
                    lowered = f"{name} <{email}>".lower()
                    if any(pattern in lowered for pattern in EXCLUDED_AUTHOR_PATTERNS):
                        current_email = None
                        continue
                    canonical_name, canonical_email = canonicalize_identity(
                        name,
                        email,
                        alias_identity_map,
                        alias_email_map,
                    )
                    current_email = canonical_email
                    contributor = stats[current_email]
                    contributor.name = canonical_name
                    contributor.email = canonical_email
                    contributor.repos.add(repo_spec["name"])
                    contributor.commits += 1
                    continue

                if current_email is None or not line.strip():
                    continue

                parts = line.split("\t")
                if len(parts) < 3 or parts[0] == "-" or parts[1] == "-":
                    continue
                contributor = stats[current_email]
                contributor.added += int(parts[0])
                contributor.deleted += int(parts[1])

    filtered = [item for item in stats.values() if len(item.repos) >= 2]
    filtered.sort(
        key=lambda item: (item.changed_lines, item.added, item.commits, item.name.lower()),
        reverse=True,
    )
    return filtered


def format_number(value: int) -> str:
    return f"{value:,}"


def build_section(contributors: list[ContributorStats]) -> str:
    snapshot_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        START_MARKER,
        "## 核心贡献者排行榜",
        "",
        "下面的榜单展示 `vLLM-HUST` 主要仓库里持续推动组织工程演进的核心贡献者，方便新成员快速了解当前的主要维护力量分布。",
        "",
        "说明：",
        "",
        "- 统计范围：`vllm-hust`、`vllm-ascend-hust`、`vllm-hust-benchmark`、`vllm-hust-dev-hub`、`vllm-hust-docs`、`vllm-hust-website`、`vllm-hust-workstation`",
        "- fork 去上游：`vllm-hust` 与 `vllm-ascend-hust` 只统计相对上游新增的组织侧提交；已同步的上游 commit 与 patch 等价的 sync / cherry-pick 不计入榜单",
        "- 统计方式：按 `git log --numstat` 聚合后的代码变更行数排序，指标为 `added + deleted`；同一贡献者的多个 author identity 会按本仓库 `.mailmap` 合并",
        "- 展示规则：排除 bot 账号，只展示在至少 2 个主要仓库里有提交的贡献者",
        f"- 快照时间：`{snapshot_date}`",
        "",
        "| Rank | Contributor | Changed lines | Added / Deleted | Active repos |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for rank, contributor in enumerate(contributors[:10], start=1):
        lines.append(
            f"| {rank} | {contributor.name} | {format_number(contributor.changed_lines)} | "
            f"{format_number(contributor.added)} / {format_number(contributor.deleted)} | {len(contributor.repos)} |"
        )
    lines.extend(
        [
            "",
            "这份榜单更适合表达 `vLLM-HUST` 组织自有工程链路中的持续活跃度，不等价于代码质量、技术难度、设计贡献或社区影响力的完整排序。后续如果需要，也可以继续补充运行时、Ascend、Benchmark / Website 等分榜。",
            END_MARKER,
        ]
    )
    return "\n".join(lines)


def replace_section(readme_path: Path, new_section: str) -> None:
    content = readme_path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        flags=re.DOTALL,
    )
    if pattern.search(content):
        updated = pattern.sub(new_section, content)
    else:
        heading_pattern = re.compile(r"^## 核心贡献者排行榜\n.*?(?=^## )", flags=re.DOTALL | re.MULTILINE)
        if not heading_pattern.search(content):
            raise RuntimeError("Could not find contributor leaderboard section to replace")
        updated = heading_pattern.sub(new_section + "\n\n", content)
    readme_path.write_text(updated, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update the vLLM-HUST contributor leaderboard")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=None,
        help="Optional local workspace root containing sibling repository checkouts",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    workspace_root = args.workspace_root
    if workspace_root is None:
        candidate = repo_root.parent
        workspace_root = candidate if (candidate / "vllm-hust").exists() else None

    contributors = collect_stats(repo_root, workspace_root)
    replace_section(repo_root / "profile" / "README.md", build_section(contributors))


if __name__ == "__main__":
    main()