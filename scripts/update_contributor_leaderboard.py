#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
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
    {
        "name": ".github",
        "url": "git@github.com:vLLM-HUST/.github.git",
        "branch": "main",
    },
]

RUNTIME_CORE_REPOS = {
    "vllm-hust",
    "vllm-ascend-hust",
    "vllm-ascend-quant-hust",
}

# Independently maintained result repositories whose implementation directly
# optimizes the inference execution layer.
INDEPENDENT_OPTIMIZATION_REPOS = {
    "vllm-ascend-hust-diffspec",
    "vllm-hust-bidkv",
}

CORE_REPOS = RUNTIME_CORE_REPOS | INDEPENDENT_OPTIMIZATION_REPOS

MAX_COMMIT_LINES = 50_000

EXCLUDED_AUTHOR_PATTERNS = (
    "github-actions[bot]",
    "dependabot",
    "copilot-swe-agent",
    "qoder agent",
    "qoder",
    "agent@qoder.ai",
    "agent@qoder.local",
    "vllm-hust bot",
    "benchmark bot",
    "bot@vllm-hust.org",
)

GITHUB_LOGIN_BY_EMAIL = {
    "shuhao_zhang@hust.edu.cn": "ShuhaoZhangTony",
    "864832769@qq.com": "ShuhaoZhangTony",
    "420444843@qq.com": "ShuhaoZhangTony",
    "qixinzhang2601@users.noreply.github.com": "ShuhaoZhangTony",
    "mingqiwang@hust.edu.cn": "MingqiWang-coder",
    "gxl20040702@gmail.com": "XilingGao",
    "995496585@qq.com": "KimmoZAG",
    "180929231+kms12425-ctrl@users.noreply.github.com": "kms12425",
    "ma.rocky.oa@outlook.com": "kms12425",
    "2819959180@qq.com": "Jerry01020",
    "czjwangyi2023@163.com": "mynameisczj",
    "141249024+mynameisczj@users.noreply.github.com": "mynameisczj",
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
    "961554798@qq.com": "dzcixy",
}

PR_MERGE_PATTERN = re.compile(r"^Merge pull request #(\d+) from (?P<owner>[^/]+)/")

SYNC_SUBJECT_PATTERNS = (
    re.compile(r"main\s*2\s*main", re.IGNORECASE),
    re.compile(r"sync upstream", re.IGNORECASE),
    re.compile(r"merge:\s*sync upstream", re.IGNORECASE),
    re.compile(r"\bmerge\b.*\bupstream\b|\bupstream\b.*\bmerge\b", re.IGNORECASE),
    re.compile(r"\bsync\b.*\bupstream\b|\bupstream\b.*\bsync\b", re.IGNORECASE),
    re.compile(r"\bupgrade\s+vllm\b", re.IGNORECASE),
    re.compile(r"\bupgrade\s+vllm\s+commit\b", re.IGNORECASE),
    re.compile(r"\bupgrade\s+vllm\s+main\b", re.IGNORECASE),
    re.compile(r"\bupgrade\s+to\s+vllm\b", re.IGNORECASE),
)

# Display-name overrides: git author name -> canonical display name
# Used AFTER mailmap canonicalization to fix remaining display anomalies.
NAME_MAP: dict[str, str] = {
    "GitHub Copilot": "Shuhao Zhang",
    "Remby Lis": "Remygred",
}

START_MARKER = "<!-- contributor-leaderboard:start -->"
END_MARKER = "<!-- contributor-leaderboard:end -->"
ORG_NAME = "vLLM-HUST"
SYNTHETIC_CONTRIBUTOR_IDENTITIES = {
    "vllm-hust developer",
}


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
    # Commit subjects for contribution summarization: list of (repo_name, subject)
    commit_subjects: list[tuple[str, str]] = field(default_factory=list)

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


def fetch_org_repositories() -> list[dict]:
    gh_binary = shutil.which("gh")
    if gh_binary is None:
        raise RuntimeError("gh CLI is required to discover vLLM-HUST repositories")
    output = subprocess.run(
        [gh_binary, "api", f"orgs/{ORG_NAME}/repos?per_page=100&type=all"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    repositories = json.loads(output)
    if not isinstance(repositories, list):
        raise RuntimeError(f"Failed to resolve {ORG_NAME} repositories")
    return repositories


def expand_repo_specs(configured_specs: list[dict], repositories: list[dict]) -> list[dict]:
    """Add active public organization-owned repositories to configured specs.

    Explicit specs remain authoritative for repositories that need special
    upstream or commit-exclusion rules. GitHub forks are not auto-added because
    they require an explicit fork-only attribution policy; private repositories
    are excluded from the public leaderboard.
    """
    expanded = [dict(spec) for spec in configured_specs]
    configured_names = {spec["name"] for spec in expanded}

    for repository in sorted(repositories, key=lambda item: str(item.get("name") or "")):
        name = str(repository.get("name") or "").strip()
        branch = str(repository.get("default_branch") or "").strip()
        clone_url = str(
            repository.get("ssh_url") or repository.get("clone_url") or ""
        ).strip()
        if (
            not name
            or name in configured_names
            or not branch
            or not clone_url
            or repository.get("private")
            or repository.get("archived")
            or repository.get("fork")
        ):
            continue
        expanded.append({"name": name, "url": clone_url, "branch": branch})
        configured_names.add(name)

    return expanded


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
    count_commit: bool = False,
    subject: str = "",
) -> None:
    contributor = stats[contributor_key]
    contributor.name = display_name
    contributor.email = display_email
    contributor.repos.add(repo_name)
    contributor.added += added
    contributor.deleted += deleted
    contributor.per_repo_added[repo_name] += added
    contributor.per_repo_deleted[repo_name] += deleted
    if count_commit:
        contributor.commits += 1
        contributor.per_repo_commits[repo_name] += 1
        contributor.commit_subjects.append((repo_name, subject))



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
    upstream_ref = f"{fetch_target}/{upstream_branch}"
    try:
        run_git(["fetch", fetch_target, upstream_branch], repo_dir)
    except subprocess.CalledProcessError:
        run_git(["rev-parse", "--verify", f"{upstream_ref}^{{commit}}"], repo_dir)
        print(
            f"warning: using existing {upstream_ref} after upstream fetch failed",
            file=sys.stderr,
        )
    return upstream_ref


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
    members = {line.strip() for line in output.splitlines() if line.strip()}
    if not members:
        raise RuntimeError(f"Failed to resolve {ORG_NAME} org members")
    return members


def fetch_pull_request_author_login(repo_name: str, pr_number: str) -> str | None:
    gh_binary = shutil.which("gh")
    if gh_binary is None:
        return None
    try:
        return subprocess.run(
            [gh_binary, "api", f"repos/{ORG_NAME}/{repo_name}/pulls/{pr_number}", "--jq", ".user.login"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip() or None
    except subprocess.CalledProcessError:
        return None


def is_org_member_identity(name: str, email: str, member_logins: set[str]) -> bool:
    lowered_logins = {login.casefold() for login in member_logins}
    mapped_login = GITHUB_LOGIN_BY_EMAIL.get(email)
    if mapped_login and mapped_login.casefold() in lowered_logins:
        return True
    normalized_logins = {re.sub(r"[^a-z0-9]", "", login) for login in lowered_logins}
    candidates = {
        name.casefold(),
        email.split("@", 1)[0].casefold(),
        re.sub(r"[^a-z0-9]", "", name.casefold()),
        re.sub(r"[^a-z0-9]", "", email.split("@", 1)[0].casefold()),
    }
    candidates.discard("")
    if any(candidate in lowered_logins for candidate in candidates):
        return True
    return any(
        candidate and (candidate in login or login in candidate)
        for candidate in candidates
        for login in normalized_logins
    )


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
        parts = line.split("\t")
        if len(parts) < 3 or parts[0] == "-" or parts[1] == "-":
            continue
        added += int(parts[0])
        deleted += int(parts[1])
    return added, deleted


def is_valid_contribution_size(added: int, deleted: int) -> bool:
    return 0 < added + deleted <= MAX_COMMIT_LINES



def collect_standard_repo_stats(
    repo_dir: Path,
    repo_spec: dict,
    alias_identity_map: dict[str, tuple[str, str]],
    alias_email_map: dict[str, tuple[str, str]],
    stats: dict[str, ContributorStats],
) -> None:
    exclude_prefixes = repo_spec.get("exclude_commits", [])
    log_output = run_git(
        [
            "log",
            "--format=@@@%H%x09%aN <%aE>%x09%s",
            "--numstat",
            "--no-renames",
            "--no-merges",
            repo_spec.get("branch", "main"),
        ],
        repo_dir,
    )

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
            contributor.commit_subjects.append((repo_spec["name"], subject))
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


def collect_fork_repo_stats(
    repo_dir: Path,
    repo_spec: dict,
    alias_identity_map: dict[str, tuple[str, str]],
    alias_email_map: dict[str, tuple[str, str]],
    member_logins: set[str],
    stats: dict[str, ContributorStats],
) -> None:
    upstream_ref = _resolve_upstream_ref(repo_dir, repo_spec)
    upstream_subjects = {
        subject.strip()
        for subject in run_git(["log", "--format=%s", "--no-merges", upstream_ref], repo_dir).splitlines()
        if subject.strip()
    }
    pr_author_cache: dict[str, str] = {}
    field_sep = "\x1f"
    record_sep = "\x1e"
    history = run_git(
        [
            "log",
            "--first-parent",
            "--reverse",
            f"--format=%H{field_sep}%P{field_sep}%aN <%aE>{field_sep}%s{field_sep}%b{record_sep}",
            repo_spec.get("branch", "main"),
        ],
        repo_dir,
    )

    for raw_record in history.split(record_sep):
        record = raw_record.strip()
        if not record:
            continue
        parts = record.split(field_sep, 4)
        parts.extend([""] * (5 - len(parts)))
        commit_hash, parents_text, identity_text, subject, body = parts
        parent_hashes = parents_text.split()

        if len(parent_hashes) > 1:
            match = PR_MERGE_PATTERN.match(subject.strip())
            if match is None:
                continue
            pr_number = match.group(1)
            pr_title = next((line.strip() for line in body.splitlines() if line.strip()), subject)
            if should_exclude_subject(pr_title, upstream_subjects):
                continue
            added, deleted = sum_numstat_output(
                run_git(["diff-tree", "--numstat", "--no-renames", f"{commit_hash}^1", commit_hash], repo_dir)
            )
            if not is_valid_contribution_size(added, deleted):
                continue
            pr_author = pr_author_cache.get(pr_number)
            if pr_author is None:
                pr_author = fetch_pull_request_author_login(repo_spec["name"], pr_number) or match.group("owner")
                pr_author_cache[pr_number] = pr_author
            synthetic_email = f"{pr_author.casefold()}@users.noreply.github.com"
            if is_excluded_author_identity(pr_author, synthetic_email):
                continue
            canonical_name, canonical_email = canonicalize_identity(
                pr_author, synthetic_email, alias_identity_map, alias_email_map
            )
            update_contributor_stats(
                stats,
                contributor_key=canonical_email,
                display_name=canonical_name,
                display_email=canonical_email,
                repo_name=repo_spec["name"],
                added=added,
                deleted=deleted,
                count_commit=True,
                subject=pr_title,
            )
            continue

        name, email = parse_identity(identity_text)
        if is_excluded_author_identity(name, email) or should_exclude_subject(subject, upstream_subjects):
            continue
        canonical_name, canonical_email = canonicalize_identity(
            name, email, alias_identity_map, alias_email_map
        )
        if not is_org_member_identity(canonical_name, canonical_email, member_logins):
            continue
        added, deleted = sum_numstat_output(
            run_git(["show", "--format=", "--numstat", "--no-renames", commit_hash], repo_dir)
        )
        if not is_valid_contribution_size(added, deleted):
            continue
        update_contributor_stats(
            stats,
            contributor_key=canonical_email,
            display_name=canonical_name,
            display_email=canonical_email,
            repo_name=repo_spec["name"],
            added=added,
            deleted=deleted,
            count_commit=True,
            subject=subject,
        )



def collect_stats(repo_root: Path, workspace_root: Path | None) -> dict[str, ContributorStats]:
    """Collect contributor stats across all repos. Returns the unified stats dict."""
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

    return stats


def coalesce_stats_by_person(
    repo_root: Path, stats: dict[str, ContributorStats]
) -> dict[str, ContributorStats]:
    """Merge git identities that resolve to the same curated GitHub person.

    Mailmap remains the primary source for author canonicalization.  The people
    index is a second, curated identity source and can associate newly observed
    emails or git names with an existing GitHub account.  Without this pass,
    those aliases appear as separate leaderboard rows even though enrichment
    later assigns them the same ``github_login``.
    """
    people_index = load_people_index(repo_root)
    merged: dict[str, ContributorStats] = {}

    for email, contributor in stats.items():
        person = resolve_person_record(
            people_index, email=email, name=contributor.name
        )
        login = str((person or {}).get("github_login") or "").strip()
        key = f"github:{login.lower()}" if login else f"email:{email.lower()}"

        if key not in merged:
            canonical_email = email
            if login:
                canonical_email = next(
                    (
                        candidate
                        for candidate in (person or {}).get("emails") or []
                        if GITHUB_LOGIN_BY_EMAIL.get(str(candidate).lower()) == login
                    ),
                    email,
                )
            canonical_name = str(
                (person or {}).get("english_name")
                or (person or {}).get("github_login")
                or contributor.name
            ).strip()
            merged[key] = ContributorStats(
                name=canonical_name, email=str(canonical_email).lower()
            )

        target = merged[key]
        target.added += contributor.added
        target.deleted += contributor.deleted
        target.commits += contributor.commits
        target.repos.update(contributor.repos)
        for repo_name, value in contributor.per_repo_added.items():
            target.per_repo_added[repo_name] += value
        for repo_name, value in contributor.per_repo_deleted.items():
            target.per_repo_deleted[repo_name] += value
        for repo_name, value in contributor.per_repo_commits.items():
            target.per_repo_commits[repo_name] += value
        target.commit_subjects.extend(contributor.commit_subjects)

    return merged


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


def summarize_contributions(
    contributor: ContributorStats, *, core_only: bool = False
) -> str:
    """Generate a concise key-contributions summary from commit subjects.

    Extracts scope/area tags from conventional commit messages and groups into
    high-level contribution themes.  Returns a short comma-separated string.
    """
    import re as _re

    subjects = contributor.commit_subjects
    if core_only:
        subjects = [(r, s) for r, s in subjects if r in CORE_REPOS]
    if not subjects:
        return ""

    # Extract areas from conventional commit scopes and keywords
    area_counts: dict[str, int] = defaultdict(int)
    for _repo, subj in subjects:
        # Try conventional commit: type(scope): ...
        m = _re.match(r"(\w+)(?:\(([^)]+)\))?[!:]\s*(.*)", subj)
        if m:
            ctype, scope, desc = m.group(1).lower(), (m.group(2) or "").lower(), m.group(3).lower()
        else:
            ctype, scope, desc = "", "", subj.lower()

        # Map to high-level areas
        if any(k in desc or k in scope for k in ("ci", "cicd", "workflow", "pre-commit", "hook")):
            area_counts["CI/CD"] += 1
        elif any(k in desc or k in scope for k in ("leaderboard", "contributor", "ranking")):
            area_counts["leaderboard"] += 1
        elif any(k in desc or k in scope for k in ("benchmark", "perf", "latency", "throughput")):
            area_counts["benchmark"] += 1
        elif any(k in desc or k in scope for k in ("website", "site", "overview", "landing")):
            area_counts["website"] += 1
        elif any(k in desc or k in scope for k in ("doc", "readme", "guide", "contributing")):
            area_counts["docs"] += 1
        elif any(k in desc or k in scope for k in ("quant", "quantiz")):
            area_counts["quantization"] += 1
        elif any(k in desc or k in scope for k in ("attention", "kernel", "cuda", "triton")):
            area_counts["kernel"] += 1
        elif any(k in desc or k in scope for k in ("ascend", "npu", "cann", "aclgraph")):
            area_counts["Ascend"] += 1
        elif any(k in desc or k in scope for k in ("model", "runner", "engine", "worker", "scheduler")):
            area_counts["engine"] += 1
        elif any(k in desc or k in scope for k in ("comm", "distributed", "tp", "ep", "all_reduce")):
            area_counts["distributed"] += 1
        elif any(k in desc or k in scope for k in ("serving", "api", "openai", "endpoint")):
            area_counts["serving"] += 1
        elif any(k in desc or k in scope for k in ("workstation", "console", "deploy")):
            area_counts["workstation"] += 1
        elif any(k in desc or k in scope for k in ("test", "fixture", "assert")):
            area_counts["testing"] += 1
        elif any(k in desc or k in scope for k in ("dev", "tool", "script", "makefile")):
            area_counts["tooling"] += 1
        elif ctype == "feat":
            area_counts["features"] += 1
        elif ctype == "fix":
            area_counts["bugfix"] += 1
        elif ctype in ("chore", "style", "refactor"):
            area_counts["maintenance"] += 1
        else:
            area_counts["misc"] += 1

    # Return top areas sorted by frequency, max 4
    sorted_areas = sorted(area_counts.items(), key=lambda x: (-x[1], x[0]))
    # Filter out 'misc' if there are better labels
    if len(sorted_areas) > 1:
        sorted_areas = [(a, c) for a, c in sorted_areas if a != "misc"] or sorted_areas
    return ", ".join(area for area, _ in sorted_areas[:4])


def build_table(contributors: list[ContributorStats], *, core_only: bool = False) -> str:
    """Build a markdown table for the given contributor list."""
    lines = [
        "| Rank | Contributor | Commits | Changed lines | Added / Deleted | Active repos | Key contributions |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
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
        summary = summarize_contributions(contributor, core_only=core_only)
        lines.append(
            f"| {rank} | {format_contributor_name(contributor)} | "
            f"{format_number(commits)} | "
            f"{format_number(changed)} | "
            f"+{format_number(added)} / -{format_number(deleted)} | {repos_count} | "
            f"{summary} |"
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
        "### 核心仓库与独立优化成果",
        "",
        f"优先统计直接影响推理性能的 {len(CORE_REPOS)} 个运行时核心仓库"
        "与独立优化成果仓库"
        f"（{core_repo_names}），"
        f"排除所有上游/初始代码，快照 `{snapshot_date}`。",
        "",
        build_table(core_contributors, core_only=True),
        "",
        "---",
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
        END_MARKER,
    ]
    return "\n".join(lines)


@dataclass
class PeopleIndex:
    by_login: dict[str, dict]
    by_email: dict[str, dict]
    by_name: dict[str, dict]
    people: list[dict]


def normalize_lookup_value(value: str | None) -> str:
    return str(value or "").strip().casefold()


def load_people_index(repo_root: Path) -> PeopleIndex:
    people_path = repo_root / "profile" / "people.json"
    if not people_path.exists():
        return PeopleIndex(by_login={}, by_email={}, by_name={}, people=[])

    payload = json.loads(people_path.read_text(encoding="utf-8"))
    people = payload.get("people") or {}
    by_login: dict[str, dict] = {}
    by_email: dict[str, dict] = {}
    by_name: dict[str, dict] = {}

    for person in people.values():
        if not isinstance(person, dict):
            continue

        login_key = normalize_lookup_value(person.get("github_login"))
        if login_key:
            by_login[login_key] = person

        for email in person.get("emails") or []:
            email_key = normalize_lookup_value(email)
            if email_key:
                by_email[email_key] = person

        name_candidates = [
            person.get("display_name"),
            person.get("chinese_name"),
            person.get("english_name"),
            person.get("github_login"),
        ]
        name_candidates.extend(person.get("git_names") or [])
        name_candidates.extend(person.get("aliases") or [])
        for candidate in name_candidates:
            name_key = normalize_lookup_value(candidate)
            if name_key:
                by_name.setdefault(name_key, person)

    return PeopleIndex(
        by_login=by_login,
        by_email=by_email,
        by_name=by_name,
        people=[person for person in people.values() if isinstance(person, dict)],
    )


def resolve_person_record(
    people_index: PeopleIndex,
    *,
    login: str | None = None,
    email: str | None = None,
    name: str | None = None,
) -> dict | None:
    login_key = normalize_lookup_value(login)
    if login_key and login_key in people_index.by_login:
        return people_index.by_login[login_key]

    email_key = normalize_lookup_value(email)
    if email_key and email_key in people_index.by_email:
        return people_index.by_email[email_key]

    name_key = normalize_lookup_value(name)
    if name_key and name_key in people_index.by_name:
        return people_index.by_name[name_key]

    return None


def is_confirmed_person(person: dict | None) -> bool:
    return bool(
        person
        and person.get("public")
        and not person.get("needs_review")
    )


def person_vllm_hust_profile(person: dict | None) -> dict:
    profiles = (person or {}).get("profiles") or {}
    profile = profiles.get("vllm_hust") or {}
    return profile if isinstance(profile, dict) else {}


def localized_profile_value(profile: dict, key: str) -> dict[str, str]:
    return {
        "zh": str(profile.get(f"{key}_zh") or "").strip(),
        "en": str(profile.get(f"{key}_en") or "").strip(),
    }


def enrich_contributor_item(
    item: dict,
    people_index: PeopleIndex,
    *,
    contributor_email: str | None = None,
) -> dict:
    person = resolve_person_record(
        people_index,
        login=item.get("github_login"),
        email=contributor_email,
        name=item.get("name"),
    )

    login = str(item.get("github_login") or "").strip()
    github_url = str(item.get("github_url") or "").strip()
    display_name = str(item.get("name") or "").strip()
    chinese_name = ""
    english_name = ""
    profile: dict = {}

    if person is not None:
        login = str(person.get("github_login") or login).strip()
        github_url = str(person.get("github_url") or github_url).strip()
        chinese_name = str(person.get("chinese_name") or "").strip()
        english_name = str(person.get("english_name") or "").strip()
        if chinese_name:
            display_name = chinese_name
        profile = person_vllm_hust_profile(person)

    if login and not github_url:
        github_url = f"https://github.com/{login}"

    item["github_login"] = login or None
    item["github_url"] = github_url or None
    item["display_name"] = display_name
    item["chinese_name"] = chinese_name
    item["english_name"] = english_name
    identity_confirmed = is_confirmed_person(person)
    item["person_id"] = (
        f"github:{login.casefold()}"
        if login
        else (
            f"profile:{normalize_lookup_value(display_name)}"
            if identity_confirmed
            else f"author:{normalize_lookup_value(item.get('name'))}"
        )
    )
    item["identity_confirmed"] = identity_confirmed
    item["core_member"] = bool(set(item.get("repos") or []) & CORE_REPOS)
    item["role"] = localized_profile_value(profile, "role")
    item["research_direction"] = localized_profile_value(
        profile, "research_direction"
    )
    item["participation_direction"] = localized_profile_value(
        profile, "participation_direction"
    )
    item["advisor"] = localized_profile_value(profile, "advisor")
    item["contribution_areas"] = str(item.get("key_contributions") or "")
    return item


def is_synthetic_contributor(item: dict) -> bool:
    identities = {
        normalize_lookup_value(item.get("name")),
        normalize_lookup_value(item.get("display_name")),
        normalize_lookup_value(item.get("github_login")),
    }
    return bool(identities & SYNTHETIC_CONTRIBUTOR_IDENTITIES)


def build_profile_only_participant(person: dict) -> dict:
    login = str(person.get("github_login") or "").strip()
    display_name = str(
        person.get("chinese_name")
        or person.get("display_name")
        or person.get("english_name")
        or login
    ).strip()
    profile = person_vllm_hust_profile(person)
    return {
        "name": str(
            person.get("english_name")
            or person.get("display_name")
            or display_name
        ).strip(),
        "github_login": login or None,
        "github_url": str(person.get("github_url") or "").strip() or None,
        "commits": 0,
        "changed_lines": 0,
        "added": 0,
        "deleted": 0,
        "active_repos": 0,
        "repos": [],
        "key_contributions": "",
        "display_name": display_name,
        "chinese_name": str(person.get("chinese_name") or "").strip(),
        "english_name": str(person.get("english_name") or "").strip(),
        "person_id": (
            f"github:{login.casefold()}"
            if login
            else f"profile:{normalize_lookup_value(display_name)}"
        ),
        "identity_confirmed": True,
        "core_member": False,
        "role": localized_profile_value(profile, "role"),
        "research_direction": localized_profile_value(
            profile, "research_direction"
        ),
        "participation_direction": localized_profile_value(
            profile, "participation_direction"
        ),
        "advisor": localized_profile_value(profile, "advisor"),
        "contribution_areas": "",
    }


def build_member_profiles(
    people_index: PeopleIndex,
    all_items: list[dict],
    core_items: list[dict],
) -> dict:
    core_person_ids = {item["person_id"] for item in core_items}
    participants_by_id: dict[str, dict] = {}

    for item in all_items:
        if (
            item["person_id"] in core_person_ids
            or not item.get("identity_confirmed")
            or is_synthetic_contributor(item)
        ):
            continue
        participant = dict(item)
        participant["all_repos_rank"] = participant.pop("rank", None)
        participants_by_id[participant["person_id"]] = participant

    for person in people_index.people:
        profile = person_vllm_hust_profile(person)
        if (
            not profile.get("participant")
            or not is_confirmed_person(person)
        ):
            continue
        participant = build_profile_only_participant(person)
        person_id = participant["person_id"]
        if person_id in core_person_ids:
            continue
        participants_by_id.setdefault(person_id, participant)

    participants = sorted(
        participants_by_id.values(),
        key=lambda item: normalize_lookup_value(item.get("display_name")),
    )
    unresolved = [
        dict(item)
        for item in all_items
        if not item.get("identity_confirmed")
        and not is_synthetic_contributor(item)
    ]
    return {
        "core_repo_names": sorted(CORE_REPOS),
        "core_members": core_items,
        "participants": participants,
        "unresolved_contributors": unresolved,
    }


def build_contributor_payload(
    repo_root: Path,
    all_contributors: list[ContributorStats],
    core_contributors: list[ContributorStats],
) -> dict:
    snapshot_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    people_index = load_people_index(repo_root)

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
            item = {
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
                "key_contributions": summarize_contributions(c, core_only=core_only),
            }
            items.append(enrich_contributor_item(item, people_index, contributor_email=c.email))
        return items

    all_items = _items(all_contributors, core_only=False)
    core_items = _items(core_contributors, core_only=True)
    return {
        "updated_at": snapshot_date,
        "all_repos": {
            "scope_repos": [spec["name"] for spec in REPO_SPECS],
            "contributors": all_items,
        },
        "core_repos": {
            "scope_repos": sorted(CORE_REPOS),
            "contributors": core_items,
        },
        "member_profiles": build_member_profiles(
            people_index, all_items, core_items
        ),
    }


def refresh_contributor_payload_profiles(repo_root: Path, payload: dict) -> dict:
    """Reapply canonical identity/profile metadata without recomputing git stats."""
    people_index = load_people_index(repo_root)
    refreshed = dict(payload)
    refreshed_scopes: dict[str, dict] = {}
    for scope_name in ("all_repos", "core_repos"):
        scope = dict(payload.get(scope_name) or {})
        scope["contributors"] = [
            enrich_contributor_item(dict(item), people_index)
            for item in scope.get("contributors") or []
        ]
        refreshed_scopes[scope_name] = scope
        refreshed[scope_name] = scope
    refreshed["member_profiles"] = build_member_profiles(
        people_index,
        refreshed_scopes["all_repos"]["contributors"],
        refreshed_scopes["core_repos"]["contributors"],
    )
    return refreshed


def sync_org_profile_contributor_data(
    repo_root: Path,
    all_contributors: list[ContributorStats],
    core_contributors: list[ContributorStats],
) -> None:
    payload = build_contributor_payload(repo_root, all_contributors, core_contributors)
    data_path = repo_root / "profile" / "core_contributors.json"
    data_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sync_website_contributor_data(
    repo_root: Path,
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
    payload = build_contributor_payload(repo_root, all_contributors, core_contributors)
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
    parser.add_argument(
        "--profiles-only",
        action="store_true",
        default=False,
        help="Refresh canonical identities and member profiles from the existing snapshot",
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

    REPO_SPECS[:] = expand_repo_specs(REPO_SPECS, fetch_org_repositories())

    if args.ci:
        convert_urls_to_https()

    repo_root = Path(__file__).resolve().parents[1]
    workspace_root = args.workspace_root
    if workspace_root is None:
        candidate = repo_root.parent
        workspace_root = candidate if (candidate / "vllm-hust").exists() else None

    if args.profiles_only:
        data_path = repo_root / "profile" / "core_contributors.json"
        payload = refresh_contributor_payload_profiles(
            repo_root, json.loads(data_path.read_text(encoding="utf-8"))
        )
        data_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if workspace_root is not None:
            website_path = workspace_root / "vllm-hust-website"
            if (website_path / ".git").exists():
                (website_path / "data" / "core_contributors.json").write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        print("Refreshed contributor identities and member profiles from existing stats")
        return

    stats = coalesce_stats_by_person(
        repo_root, collect_stats(repo_root, workspace_root)
    )
    all_contributors = build_all_contributors_list(stats)
    core_contributors = build_core_contributors_list(stats)

    sync_org_profile_contributor_data(repo_root, all_contributors, core_contributors)
    sync_website_contributor_data(repo_root, workspace_root, all_contributors, core_contributors)

    print(f"Updated leaderboard: {len(all_contributors)} contributors (all), "
          f"{len(core_contributors)} contributors (core)")


if __name__ == "__main__":
    main()
