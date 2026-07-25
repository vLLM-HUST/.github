from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


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


def test_shuhao_historical_tony_and_qixin_identities_coalesce() -> None:
    root = Path(__file__).resolve().parents[1]
    people = leaderboard.load_people_index(root)
    stats = {
        email: leaderboard.ContributorStats(
            name=name,
            email=email,
            commits=commits,
        )
        for name, email, commits in (
            ("Shuhao Zhang", "shuhao_zhang@hust.edu.cn", 10),
            ("Tony", "864832769@qq.com", 2),
            ("qixinzhang2601", "420444843@qq.com", 1),
        )
    }

    result = leaderboard.coalesce_stats_by_person(root, stats)

    assert list(result) == ["github:shuhaozhangtony"]
    assert result["github:shuhaozhangtony"].commits == 13
    assert people.by_name["tony"]["github_login"] == "ShuhaoZhangTony"
    assert people.by_name["qixinzhang2601"]["github_login"] == "ShuhaoZhangTony"


def test_iliujunn_is_publicly_mapped_to_liu_jun() -> None:
    root = Path(__file__).resolve().parents[1]
    people = leaderboard.load_people_index(root)

    person = people.by_login["iliujunn"]

    assert person["display_name"] == "Liu Jun"
    assert person["chinese_name"] == "刘俊"
    assert person["public"] is True
    assert person["needs_review"] is False


def test_required_canonical_people_and_aliases_are_mapped() -> None:
    root = Path(__file__).resolve().parents[1]
    people = leaderboard.load_people_index(root)
    expected_names = {
        "kimmozag": "张睿诚",
        "sad-and-bad1231": "匡明轩",
        "kms12425": "马俊豪",
        "kms12425-ctrl": "马俊豪",
        "junhao ma": "马俊豪",
        "jerry01020": "邱瑞杰",
        "curryzjj": "赵建军",
        "jianjun zhao": "赵建军",
        "xilinggao": "高西岭",
        "coisinixixi": "高西岭",
        "moonandlife": "王胜",
        "succinctpaul": "程月甲",
        "remygred": "刘世锋",
        "xmdhb": "曹哲",
        "anjiangy": "李庚",
        "dzcixy": "杜忠承",
        "xsun2001": "徐晨曦",
        "renty-0": "王润泽",
        "ilnnfover": "吴天宇",
    }
    for alias, chinese_name in expected_names.items():
        assert people.by_name[alias]["chinese_name"] == chinese_name

    assert people.by_login["moonandlife"]["profiles"]["vllm_hust"]["role_zh"] == "工程师"
    assert people.by_login["succinctpaul"]["profiles"]["vllm_hust"]["role_zh"] == "工程师"
    zhao = people.by_login["curryzjj"]["profiles"]["vllm_hust"]
    assert zhao["role_zh"] == "已毕业博士生，目前已入职高校"
    xiling = people.by_login["xilinggao"]["profiles"]["vllm_hust"]
    assert xiling["research_direction_zh"] == "KV量化"
    dzcixy = people.by_login["dzcixy"]
    assert dzcixy["public"] is True
    assert dzcixy["needs_review"] is False
    assert dzcixy["profiles"]["vllm_hust"]["advisor_zh"] == "黄禹"
    assert (
        dzcixy["profiles"]["vllm_hust"]["participation_direction_zh"]
        == "推测解码与阶段协同执行优化"
    )
    expected_advisors = {
        "machuanhu": "王雄",
        "raing5days": "郑龙",
        "li-changwu": "张书豪",
        "rzwang22": "王庆刚",
        "gumorming": "罗瑞坤",
        "jieyang2001": "赵进",
        "cybber695": "张书豪",
        "amber1qq": "刘海坤",
        "aly16-k": "项翔",
        "hustcui": "姚鹏程",
        "wenjuzhao": "姚鹏程",
        "seas0": "万瑶",
    }
    for login, advisor in expected_advisors.items():
        profile = people.by_login[login]["profiles"]["vllm_hust"]
        assert profile["advisor_zh"] == advisor
        assert profile["role_zh"] == "学生"

    assert people.by_login["llxler"]["chinese_name"] == "雷翔麟"
    assert people.by_login["seas0"]["chinese_name"] == "刘思辰"
    assert people.by_email["xcx14@outlook.com"]["github_login"] == "xsun2001"
    assert people.by_login["moonandlife"]["profiles"]["vllm_hust"]["staff_member"]
    assert people.by_login["succinctpaul"]["profiles"]["vllm_hust"]["staff_member"]
    long_bin = people.by_name["龙斌"]["profiles"]["vllm_hust"]
    assert long_bin["staff_member"] is True
    assert long_bin["role_zh"] == "项目/科研助理"
    for engineering_member in ("Pygone", "WMASTER123", "XilingGao"):
        profile = people.by_login[engineering_member.casefold()][
            "profiles"
        ]["vllm_hust"]
        assert profile.get("staff_member") is not True


def test_member_profile_classification_uses_merged_core_repos() -> None:
    participant_person = {
        "display_name": "Participant",
        "chinese_name": "参与者",
        "english_name": "Participant",
        "github_login": "participant",
        "github_url": "https://github.com/participant",
        "public": True,
        "needs_review": False,
        "profiles": {"vllm_hust": {"participant": True}},
    }
    external_person = {
        "display_name": "徐晨曦",
        "chinese_name": "徐晨曦",
        "english_name": "Chenxi Xu",
        "github_login": "xsun2001",
        "github_url": "https://github.com/xsun2001",
        "public": True,
        "needs_review": False,
        "profiles": {
            "vllm_hust": {
                "external_contributor": True,
                "role_zh": "外部贡献者（港科大（广州））",
            }
        },
    }
    staff_person = {
        "display_name": "Engineer",
        "chinese_name": "工程师",
        "english_name": "Engineer",
        "github_login": "engineer",
        "github_url": "https://github.com/engineer",
        "public": True,
        "needs_review": False,
        "profiles": {
            "vllm_hust": {
                "participant": True,
                "staff_member": True,
                "role_zh": "工程师",
            }
        },
    }
    people = leaderboard.PeopleIndex(
        by_login={
            "participant": participant_person,
            "xsun2001": external_person,
            "engineer": staff_person,
        },
        by_email={},
        by_name={
            "participant": participant_person,
            "xsun2001": external_person,
            "engineer": staff_person,
        },
        people=[participant_person, external_person, staff_person],
    )
    core = {
        "person_id": "github:core",
        "identity_confirmed": True,
        "name": "Core",
        "display_name": "Core",
        "github_login": "core",
        "repos": ["vllm-hust"],
        "core_member": True,
    }
    participant = {
        "person_id": "github:participant",
        "identity_confirmed": True,
        "name": "Participant",
        "display_name": "参与者",
        "github_login": "participant",
        "repos": ["vllm-hust-website"],
        "core_member": False,
        "rank": 1,
    }
    external = {
        "person_id": "github:xsun2001",
        "identity_confirmed": True,
        "external_contributor": True,
        "name": "Chenxi Xu",
        "display_name": "徐晨曦",
        "github_login": "xsun2001",
        "repos": ["vllm-hust"],
        "core_member": False,
    }
    staff = {
        "person_id": "github:engineer",
        "identity_confirmed": True,
        "external_contributor": False,
        "staff_member": True,
        "name": "Engineer",
        "display_name": "工程师",
        "github_login": "engineer",
        "repos": ["vllm-hust"],
        "core_member": False,
    }

    profiles = leaderboard.build_member_profiles(
        people,
        [core, participant, external, staff],
        [core, external, staff],
    )

    assert [item["person_id"] for item in profiles["core_members"]] == [
        "github:core"
    ]
    assert [item["person_id"] for item in profiles["participants"]] == [
        "github:participant"
    ]
    assert [
        item["person_id"] for item in profiles["external_contributors"]
    ] == ["github:xsun2001"]
    assert [item["person_id"] for item in profiles["staff_members"]] == [
        "github:engineer"
    ]


def test_resolve_upstream_ref_reuses_existing_ref_after_fetch_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls = []

    def fake_run_git(args: list[str], repo_dir: Path) -> str:
        calls.append((args, repo_dir))
        if args == ["remote"]:
            return "upstream"
        if args == ["fetch", "upstream", "main"]:
            raise subprocess.CalledProcessError(128, args)
        if args == ["rev-parse", "--verify", "upstream/main^{commit}"]:
            return "abc123"
        raise AssertionError(f"unexpected git call: {args}")

    monkeypatch.setattr(leaderboard, "run_git", fake_run_git)

    result = leaderboard._resolve_upstream_ref(
        tmp_path,
        {
            "upstream": "https://example.com/upstream.git",
            "upstream_remote": "upstream",
            "upstream_branch": "main",
        },
    )

    assert result == "upstream/main"
    assert (["rev-parse", "--verify", "upstream/main^{commit}"], tmp_path) in calls


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
    assert "vllm-ascend-hust-bidkv" not in payload["all_repos"]["scope_repos"]
    assert "vllm-hust-bidkv" in payload["core_repos"]["scope_repos"]
    mingqi = next(
        item
        for item in payload["all_repos"]["contributors"]
        if item.get("github_login") == "MingqiWang-coder"
    )
    assert "vllm-ascend-hust-bidkv" not in mingqi["repos"]


def test_generated_member_profiles_share_core_classification_invariants() -> None:
    root = Path(__file__).resolve().parents[1]
    payload = json.loads((root / "profile" / "core_contributors.json").read_text())
    profiles = payload["member_profiles"]
    core_repos = set(profiles["core_repo_names"])
    core_members = profiles["core_members"]
    participants = profiles["participants"]
    staff = profiles["staff_members"]
    external = profiles["external_contributors"]
    assert {item["display_name"] for item in staff} == {
        "王胜",
        "程月甲",
        "龙斌",
    }

    assert core_repos == set(payload["core_repos"]["scope_repos"])
    raw_core_ids = {
        item["person_id"] for item in payload["core_repos"]["contributors"]
    }
    classified_core_ids = {item["person_id"] for item in core_members}
    external_core_ids = {
        item["person_id"]
        for item in external
        if set(item["repos"]) & core_repos
    }
    staff_core_ids = {
        item["person_id"]
        for item in staff
        if set(item["repos"]) & core_repos
    }
    assert raw_core_ids == (
        classified_core_ids | staff_core_ids | external_core_ids
    )
    assert all(set(item["repos"]) & core_repos for item in core_members)
    assert all(not (set(item["repos"]) & core_repos) for item in participants)

    core_ids = [item["person_id"] for item in core_members]
    participant_ids = [item["person_id"] for item in participants]
    staff_ids = [item["person_id"] for item in staff]
    external_ids = [item["person_id"] for item in external]
    assert len(core_ids) == len(set(core_ids))
    assert len(participant_ids) == len(set(participant_ids))
    assert len(staff_ids) == len(set(staff_ids))
    assert len(external_ids) == len(set(external_ids))
    assert set(core_ids).isdisjoint(participant_ids)
    assert set(core_ids).isdisjoint(staff_ids)
    assert set(core_ids).isdisjoint(external_ids)
    assert set(participant_ids).isdisjoint(staff_ids)
    assert set(participant_ids).isdisjoint(external_ids)
    assert set(staff_ids).isdisjoint(external_ids)


def test_generated_profiles_preserve_manual_metadata_separately() -> None:
    root = Path(__file__).resolve().parents[1]
    payload = json.loads((root / "profile" / "core_contributors.json").read_text())
    profiles = payload["member_profiles"]
    by_name = {
        item["display_name"]: item
        for item in (
            profiles["core_members"]
            + profiles["participants"]
            + profiles["staff_members"]
            + profiles["external_contributors"]
        )
    }

    assert by_name["张睿诚"]["github_login"] == "KimmoZAG"
    assert by_name["匡明轩"]["github_login"] == "sad-and-bad1231"
    assert by_name["马俊豪"]["github_login"] == "kms12425"
    assert by_name["邱瑞杰"]["github_login"] == "Jerry01020"
    assert by_name["赵建军"]["github_login"] == "curryzjj"
    assert by_name["高西岭"]["github_login"] == "XilingGao"
    assert by_name["王胜"]["role"]["zh"] == "工程师"
    assert by_name["王胜"]["staff_member"] is True
    assert by_name["程月甲"]["role"]["zh"] == "工程师"
    assert by_name["程月甲"]["staff_member"] is True
    assert by_name["龙斌"]["role"]["zh"] == "项目/科研助理"
    assert by_name["龙斌"]["staff_member"] is True
    assert by_name["赵建军"]["role"]["zh"] == "已毕业博士生，目前已入职高校"
    assert by_name["高西岭"]["research_direction"]["zh"] == "KV量化"
    assert "多级KV缓存" not in by_name["高西岭"]["research_direction"]["zh"]
    assert by_name["刘世锋"]["github_login"] == "Remygred"
    assert by_name["刘世锋"]["role"]["zh"] == "华科大三实习生"
    assert by_name["刘世锋"]["advisor"]["zh"] == "张书豪"
    assert by_name["曹哲"]["github_login"] == "xmdhb"
    assert by_name["曹哲"]["role"]["zh"] == "即将入学的研究生"
    assert by_name["曹哲"]["advisor"]["zh"] == "张书豪"
    assert by_name["李庚"]["github_login"] == "Anjiangy"
    assert by_name["李庚"]["role"]["zh"] == "马上入学的华科研究生"
    assert by_name["李庚"]["advisor"]["zh"] == "张书豪"
    assert by_name["杜忠承"]["github_login"] == "dzcixy"
    assert by_name["杜忠承"]["advisor"]["zh"] == "黄禹"
    assert by_name["徐晨曦"]["github_login"] == "xsun2001"
    assert by_name["徐晨曦"]["external_contributor"] is True
    assert by_name["徐晨曦"]["role"]["zh"] == "外部贡献者（港科大（广州））"
    unresolved_ids = {
        item["person_id"] for item in profiles["unresolved_contributors"]
    }
    assert "github:remygred" not in unresolved_ids
    assert "github:dzcixy" not in unresolved_ids
    assert "author:sssarrior" not in unresolved_ids
    xuheng_rows = [
        item
        for item in profiles["participants"]
        if item["display_name"] == "李旭恒"
    ]
    assert len(xuheng_rows) == 1
    assert xuheng_rows[0]["person_id"] == "profile:李旭恒"

    for item in by_name.values():
        assert "contribution_areas" in item
        assert "research_direction" in item
        assert item["contribution_areas"] == item["key_contributions"]


def test_expand_repo_specs_adds_public_independent_repositories() -> None:
    configured = [
        {
            "name": "vllm-hust",
            "url": "https://github.com/vLLM-HUST/vllm-hust.git",
            "branch": "main",
            "upstream": "https://github.com/vllm-project/vllm.git",
        }
    ]
    repositories = [
        {
            "name": "vllm-hust",
            "clone_url": "https://github.com/vLLM-HUST/vllm-hust.git",
            "default_branch": "main",
            "private": False,
            "archived": False,
            "fork": True,
        },
        {
            "name": "vllm-ascend-hust-bidkv",
            "clone_url": "https://github.com/vLLM-HUST/vllm-ascend-hust-bidkv.git",
            "default_branch": "main",
            "private": False,
            "archived": False,
            "fork": False,
        },
        {
            "name": "private-research",
            "clone_url": "https://github.com/vLLM-HUST/private-research.git",
            "default_branch": "main",
            "private": True,
            "archived": False,
            "fork": False,
        },
        {
            "name": "external-fork",
            "clone_url": "https://github.com/vLLM-HUST/external-fork.git",
            "default_branch": "main",
            "private": False,
            "archived": False,
            "fork": True,
        },
    ]

    expanded = leaderboard.expand_repo_specs(configured, repositories)

    assert [spec["name"] for spec in expanded] == [
        "vllm-hust",
        "vllm-ascend-hust-bidkv",
    ]
    assert expanded[0]["upstream"].endswith("vllm.git")
    assert expanded[1]["branch"] == "main"
