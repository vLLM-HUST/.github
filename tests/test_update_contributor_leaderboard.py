from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "update_contributor_leaderboard.py"
)
SPEC = importlib.util.spec_from_file_location("update_contributor_leaderboard", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
leaderboard = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = leaderboard
SPEC.loader.exec_module(leaderboard)


def test_coalesce_stats_by_curated_github_identity(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "people.json").write_text(
        json.dumps(
            {
                "people": {
                    "example": {
                        "english_name": "Example Person",
                        "github_login": "example",
                        "emails": ["canonical@example.com"],
                        "git_names": ["Example Alias"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    leaderboard.GITHUB_LOGIN_BY_EMAIL["canonical@example.com"] = "example"

    first = leaderboard.ContributorStats(
        name="Example Person", email="canonical@example.com", commits=2, added=10
    )
    first.repos.add("repo-a")
    first.per_repo_added["repo-a"] = 10
    first.per_repo_commits["repo-a"] = 2
    second = leaderboard.ContributorStats(
        name="Example Alias", email="alias@example.com", commits=3, deleted=4
    )
    second.repos.add("repo-b")
    second.per_repo_deleted["repo-b"] = 4
    second.per_repo_commits["repo-b"] = 3

    result = leaderboard.coalesce_stats_by_person(
        tmp_path,
        {first.email: first, second.email: second},
    )

    assert list(result) == ["github:example"]
    contributor = result["github:example"]
    assert contributor.name == "Example Person"
    assert contributor.email == "canonical@example.com"
    assert contributor.commits == 5
    assert contributor.added == 10
    assert contributor.deleted == 4
    assert contributor.repos == {"repo-a", "repo-b"}
    assert contributor.per_repo_commits == {"repo-a": 2, "repo-b": 3}


def test_unmapped_identities_remain_distinct(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "people.json").write_text('{"people": {}}', encoding="utf-8")
    first = leaderboard.ContributorStats(name="One", email="one@example.com")
    second = leaderboard.ContributorStats(name="Two", email="two@example.com")

    result = leaderboard.coalesce_stats_by_person(
        tmp_path,
        {first.email: first, second.email: second},
    )

    assert set(result) == {"email:one@example.com", "email:two@example.com"}


def test_succinctpaul_identities_coalesce_without_merging_curated_peer(
    tmp_path: Path,
) -> None:
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "people.json").write_text(
        json.dumps(
            {
                "people": {
                    "SuccinctPaul": {
                        "github_login": "SuccinctPaul",
                        "emails": [
                            "108982045+SuccinctPaul@users.noreply.github.com",
                            "chengyuejia@foxmail.com",
                        ],
                        "git_names": ["Paul", "Paul Cheng"],
                    },
                    "other-paul": {
                        "github_login": "other-paul",
                        "emails": ["other-paul@example.com"],
                        "git_names": ["Paul"],
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    noreply = leaderboard.ContributorStats(
        name="Paul",
        email="108982045+SuccinctPaul@users.noreply.github.com",
        commits=2,
        added=10,
    )
    foxmail = leaderboard.ContributorStats(
        name="Paul Cheng",
        email="chengyuejia@foxmail.com",
        commits=3,
        deleted=4,
    )
    curated_peer = leaderboard.ContributorStats(
        name="Paul",
        email="other-paul@example.com",
        commits=5,
        added=7,
    )

    result = leaderboard.coalesce_stats_by_person(
        tmp_path,
        {
            noreply.email: noreply,
            foxmail.email: foxmail,
            curated_peer.email: curated_peer,
        },
    )

    assert set(result) == {"github:succinctpaul", "github:other-paul"}
    assert result["github:succinctpaul"].commits == 5
    assert result["github:succinctpaul"].added == 10
    assert result["github:succinctpaul"].deleted == 4
    assert result["github:other-paul"].commits == 5


def test_qoder_agent_is_excluded_as_automation() -> None:
    assert leaderboard.is_excluded_author_identity("Qoder Agent", "agent@qoder.ai")
    assert leaderboard.is_excluded_author_identity("Qoder Agent", "agent@qoder.local")
    assert leaderboard.is_excluded_author_identity("qoder", "qoder@local")


def test_org_member_identity_uses_canonical_email_login_mapping() -> None:
    assert leaderboard.is_org_member_identity(
        "Jingyuan Tian",
        "49518565+cubelander@users.noreply.github.com",
        {"CubeLander"},
    )


def test_upstream_and_sync_subjects_are_excluded() -> None:
    assert leaderboard.should_exclude_subject("upstream change", {"upstream change"})
    assert leaderboard.should_exclude_subject("Merge: sync upstream main", set())
    assert leaderboard.should_exclude_subject("Sync main with upstream vllm/main", set())
    assert leaderboard.should_exclude_subject(
        "Merge latest upstream/main into vLLM-HUST", set()
    )
    assert not leaderboard.should_exclude_subject("fix: local regression", set())


def test_contribution_size_filter_excludes_empty_and_bulk_imports() -> None:
    assert not leaderboard.is_valid_contribution_size(0, 0)
    assert leaderboard.is_valid_contribution_size(49_999, 1)
    assert not leaderboard.is_valid_contribution_size(50_000, 1)


def test_generated_payload_has_unique_mapped_people() -> None:
    root = Path(__file__).resolve().parents[1]
    payload = json.loads((root / "profile" / "core_contributors.json").read_text())
    for scope in ("all_repos", "core_repos"):
        contributors = payload[scope]["contributors"]
        logins = [
            item["github_login"].casefold()
            for item in contributors
            if item["github_login"]
        ]
        assert len(logins) == len(set(logins))
