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
        "upstream_remote": "upstream",
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
    "vllm-hust bot",
    "bot@vllm-hust.org",
)

GITHUB_LOGIN_BY_EMAIL = {
    "shuhao_zhang@hust.edu.cn": "ShuhaoZhangTony",
    "mingqiwang@hust.edu.cn": "MingqiWang-coder",
    "gxl20040702@gmail.com": "XilingGao",
    "995496585@qq.com": "KimmoZAG",
    "iliujun@msn.com": "iliujunn",
    "cubelander@users.noreply.github.com": "CubeLander",
    "moonandlife@qq.com": "moonandlife",
    "pygonebe@outlook.com": "Pygone",
}

PR_MERGE_PATTERN = re.compile(r"^Merge pull request #(\d+) from (?P<owner>[^/]+)/")

SYNC_SUBJECT_PATTERNS = (
    re.compile(r"main\s*2\s*main", re.IGNORECASE),
    re.compile(r"sync upstream", re.IGNORECASE),
    re.compile(r"merge:\s*sync upstream", re.IGNORECASE),
    re.compile(r"\bupgrade\s+vllm\b", re.IGNORECASE),
    re.compile(r"\bupgrade\s+vllm\s+commit\b", re.IGNORECASE),
    re.compile(r"\bupgrade\s+vllm\s+main\b", re.IGNORECASE),
    re.compile(r"\bupgrade\s+to\s+vllm\b", re.IGNORECASE),
)

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


def fetch_org_member_logins() -> set[str]:
    gh_binary = shutil.which("gh")
    if gh_binary is None:
        raise RuntimeError("gh CLI is required to resolve vLLM-HUST org members")
    output = subprocess.run(
        [gh_binary, "api", f"orgs/{ORG_NAME}/members", "--paginate", "--jq", ".[].login"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    member_logins = {line.strip() for line in output.splitlines() if line.strip()}
    if not member_logins:
        raise RuntimeError(f"Failed to resolve {ORG_NAME} org members")
    return member_logins


def fetch_pull_request_author_login(repo_name: str, pr_number: str) -> str | None:
    gh_binary = shutil.which("gh")
    if gh_binary is None:
        return None
    try:
        output = subprocess.run(
            [gh_binary, "api", f"repos/{ORG_NAME}/{repo_name}/pulls/{pr_number}", "--jq", ".user.login"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        return None
    return output or None


def is_org_member_identity(name: str, email: str, member_logins: set[str]) -> bool:
    lowered_logins = {login.lower() for login in member_logins}
    normalized_logins = {re.sub(r"[^a-z0-9]", "", login.lower()) for login in member_logins}
    candidate_tokens = {
        name.lower(),
        email.split("@", 1)[0].lower(),
        re.sub(r"[^a-z0-9]", "", name.lower()),
        re.sub(r"[^a-z0-9]", "", email.split("@", 1)[0].lower()),
    }
    candidate_tokens.discard("")
    if any(token in lowered_logins for token in candidate_tokens):
        return True
    for token in candidate_tokens:
        if any(token and (token in login or login in token) for login in normalized_logins):
            return True
    return False


def update_contributor_stats(
    stats: dict[str, ContributorStats],
    *,
    contributor_key: str,
    display_name: str,
    display_email: str,
    repo_name: str,
    added: int,
    deleted: int,
    commits: int = 1,
) -> None:
    contributor = stats[contributor_key]
    contributor.name = display_name
    contributor.email = display_email
    contributor.repos.add(repo_name)
    contributor.commits += commits
    contributor.added += added
    contributor.deleted += deleted


def get_upstream_subjects(repo_dir: Path, repo_spec: dict[str, str]) -> set[str]:
    if "upstream" not in repo_spec:
        return set()

    fetch_target = repo_spec.get("upstream_remote")
    if fetch_target is not None:
        remotes = set(run_git(["remote"], repo_dir).split())
        if fetch_target not in remotes:
            fetch_target = None
    if fetch_target is None:
        fetch_target = repo_spec["upstream"]

    run_git(["fetch", fetch_target, repo_spec.get("upstream_branch", "main")], repo_dir)
    upstream_log = run_git(["log", "--format=%s", "--no-merges", "FETCH_HEAD"], repo_dir)
    return {line.strip() for line in upstream_log.splitlines() if line.strip()}


def get_log_output(repo_dir: Path, repo_spec: dict[str, str]) -> str:
    common_args = [
        "log",
        "--format=@@@%aN <%aE>%x09%s",
        "--numstat",
        "--no-renames",
        "--no-merges",
    ]
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


def should_exclude_subject(subject: str, upstream_subjects: set[str]) -> bool:
    normalized = subject.strip()
    if not normalized:
        return False
    if normalized in upstream_subjects:
        return True
    return any(pattern.search(normalized) for pattern in SYNC_SUBJECT_PATTERNS)


def sum_numstat_output(numstat_output: str) -> tuple[int, int]:
    added = 0
    deleted = 0
    for line in numstat_output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 3 or parts[0] == "-" or parts[1] == "-":
            continue
        added += int(parts[0])
        deleted += int(parts[1])
    return added, deleted


def collect_standard_repo_stats(
    repo_dir: Path,
    repo_spec: dict[str, str],
    alias_identity_map: dict[str, tuple[str, str]],
    alias_email_map: dict[str, tuple[str, str]],
    stats: dict[str, ContributorStats],
) -> None:
    log_output = get_log_output(repo_dir, repo_spec)
    current_email: str | None = None
    for line in log_output.splitlines():
        if line.startswith("@@@"):
            header = line[3:].strip()
            identity_text, _, subject = header.partition("\t")
            name, email = parse_identity(identity_text)
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


def collect_fork_repo_stats(
    repo_dir: Path,
    repo_spec: dict[str, str],
    alias_identity_map: dict[str, tuple[str, str]],
    alias_email_map: dict[str, tuple[str, str]],
    member_logins: set[str],
    stats: dict[str, ContributorStats],
) -> None:
    upstream_subjects = get_upstream_subjects(repo_dir, repo_spec)
    pr_author_cache: dict[str, str] = {}
    field_sep = "\x1f"
    record_sep = "\x1e"
    branch = repo_spec.get("branch", "main")
    history = run_git(
        [
            "log",
            "--first-parent",
            "--reverse",
            f"--format=%H{field_sep}%P{field_sep}%aN <%aE>{field_sep}%s{field_sep}%b{record_sep}",
            branch,
        ],
        repo_dir,
    )

    for raw_record in history.split(record_sep):
        record = raw_record.strip()
        if not record:
            continue
        record_parts = record.split(field_sep, 4)
        if len(record_parts) < 5:
            record_parts.extend([""] * (5 - len(record_parts)))
        commit_hash, parents_text, identity_text, subject, body = record_parts
        parent_hashes = parents_text.split()

        if len(parent_hashes) > 1:
            match = PR_MERGE_PATTERN.match(subject.strip())
            if match is None:
                continue
            pr_number = match.group(1)
            pr_owner = match.group("owner")
            pr_title = next((line.strip() for line in body.splitlines() if line.strip()), subject)
            if should_exclude_subject(pr_title, upstream_subjects):
                continue
            added, deleted = sum_numstat_output(
                run_git(["diff-tree", "--numstat", "--no-renames", f"{commit_hash}^1", commit_hash], repo_dir)
            )
            if added == 0 and deleted == 0:
                continue
            pr_author = pr_author_cache.get(pr_number)
            if pr_author is None:
                pr_author = fetch_pull_request_author_login(repo_spec["name"], pr_number) or pr_owner
                pr_author_cache[pr_number] = pr_author
            synthetic_email = f"{pr_author.lower()}@users.noreply.github.com"
            canonical_name, canonical_email = canonicalize_identity(
                pr_author,
                synthetic_email,
                alias_identity_map,
                alias_email_map,
            )
            update_contributor_stats(
                stats,
                contributor_key=canonical_email,
                display_name=canonical_name,
                display_email=canonical_email,
                repo_name=repo_spec["name"],
                added=added,
                deleted=deleted,
            )
            continue

        name, email = parse_identity(identity_text)
        lowered = f"{name} <{email}>".lower()
        if any(pattern in lowered for pattern in EXCLUDED_AUTHOR_PATTERNS):
            continue
        if should_exclude_subject(subject, upstream_subjects):
            continue
        canonical_name, canonical_email = canonicalize_identity(
            name,
            email,
            alias_identity_map,
            alias_email_map,
        )
        if not is_org_member_identity(canonical_name, canonical_email, member_logins):
            continue
        added, deleted = sum_numstat_output(
            run_git(["show", "--format=", "--numstat", "--no-renames", commit_hash], repo_dir)
        )
        update_contributor_stats(
            stats,
            contributor_key=canonical_email,
            display_name=canonical_name,
            display_email=canonical_email,
            repo_name=repo_spec["name"],
            added=added,
            deleted=deleted,
        )


def collect_stats(repo_root: Path, workspace_root: Path | None) -> list[ContributorStats]:
    alias_identity_map, alias_email_map = read_mailmap(repo_root / ".mailmap")
    member_logins = fetch_org_member_logins()
    stats: dict[str, ContributorStats] = defaultdict(lambda: ContributorStats(name="", email=""))

    with tempfile.TemporaryDirectory(prefix="vllm-hust-profile-") as temp_dir:
        temp_root = Path(temp_dir)
        for repo_spec in REPO_SPECS:
            repo_dir = ensure_repo_checkout(temp_root, repo_spec, workspace_root)
            if "upstream" in repo_spec:
                collect_fork_repo_stats(
                    repo_dir,
                    repo_spec,
                    alias_identity_map,
                    alias_email_map,
                    member_logins,
                    stats,
                )
            else:
                collect_standard_repo_stats(
                    repo_dir,
                    repo_spec,
                    alias_identity_map,
                    alias_email_map,
                    stats,
                )

    filtered = [item for item in stats.values() if len(item.repos) >= 1]
    filtered.sort(
        key=lambda item: (item.changed_lines, item.added, item.commits, item.name.lower()),
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
        "- fork 去上游：`vllm-hust` 与 `vllm-ascend-hust` 仍以官方上游为参照，但统计时优先按主线首父链上的 PR merge 净 diff 归因给 PR 作者；纯同步上游的 merge 与 main2main / upgrade / sync 型提交不计入榜单",
        "- 统计方式：fork 仓库按 PR merge 的净变更量统计，其他仓库按 `git log --numstat` 聚合；统一指标为 `added + deleted`；直接提交到主线的 author identity 仍按本仓库 `.mailmap` 合并",
        "- 展示规则：排除 bot 账号，列出在至少 1 个主要仓库里有提交的全部贡献者",
        f"- 快照时间：`{snapshot_date}`",
        "",
        "| Rank | Contributor | Changed lines | Added / Deleted | Active repos |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for rank, contributor in enumerate(contributors, start=1):
        lines.append(
            f"| {rank} | {format_contributor_name(contributor)} | {format_number(contributor.changed_lines)} | "
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