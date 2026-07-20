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
