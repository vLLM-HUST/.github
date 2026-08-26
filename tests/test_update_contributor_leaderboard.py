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


def test_profiles_only_refresh_merges_newly_confirmed_aliases(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "people.json").write_text(
        json.dumps(
            {
                "people": {
                    "canonical": {
                        "display_name": "MingXuan Kuang",
                        "chinese_name": "匡明轩",
                        "github_login": "sad-and-bad1231",
                        "github_url": "https://github.com/sad-and-bad1231",
                        "git_names": ["MingXuan Kuang", "Sadboineedluv"],
                        "aliases": ["Sadboineedluv"],
                        "public": True,
                        "needs_review": False,
                        "profiles": {"vllm_hust": {"participant": True}},
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    payload = {
        "all_repos": {
            "contributors": [
                {
                    "rank": 1,
                    "name": "MingXuan Kuang",
                    "commits": 3,
                    "changed_lines": 30,
                    "added": 20,
                    "deleted": 10,
                    "repos": ["vllm-hust"],
                    "key_contributions": "runtime",
                },
                {
                    "rank": 2,
                    "name": "Sadboineedluv",
                    "commits": 2,
                    "changed_lines": 12,
                    "added": 8,
                    "deleted": 4,
                    "repos": ["survey"],
                    "key_contributions": "docs",
                },
            ]
        },
        "core_repos": {"contributors": []},
    }

    refreshed = leaderboard.refresh_contributor_payload_profiles(tmp_path, payload)
    rows = refreshed["all_repos"]["contributors"]

    assert len(rows) == 1
    assert rows[0]["person_id"] == "github:sad-and-bad1231"
    assert rows[0]["display_name"] == "匡明轩"
    assert rows[0]["commits"] == 5
    assert rows[0]["changed_lines"] == 42
    assert rows[0]["repos"] == ["survey", "vllm-hust"]
    assert rows[0]["key_contributions"] == "runtime, docs"
    assert rows[0]["core_repository_contributor"] is True
    assert rows[0]["core_member"] is True


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
    assert people.by_name["qixinzhang26"]["github_login"] == "ShuhaoZhangTony"
    assert people.by_name["chooper26"]["github_login"] == "ShuhaoZhangTony"
    assert "chooper26" not in people.by_login


def test_iliujunn_is_publicly_mapped_to_liu_jun() -> None:
    root = Path(__file__).resolve().parents[1]
    people = leaderboard.load_people_index(root)

    person = people.by_login["iliujunn"]

    assert person["display_name"] == "Liu Jun"
    assert person["chinese_name"] == "刘俊"
    assert person["public"] is True
    assert person["needs_review"] is False


def test_confirmed_member_logins_have_unique_real_name_mappings() -> None:
    root = Path(__file__).resolve().parents[1]
    people = leaderboard.load_people_index(root)
    expected_names = {
        "Renty-0": "任天宇",
        "rzwang22": "王润泽",
        "jxd1111": "江勰东",
        "mumu029": "陈湘",
        "peter17-17": "李佳乐",
    }

    assert len(set(expected_names.values())) == len(expected_names)
    for login, chinese_name in expected_names.items():
        login_key = leaderboard.normalize_lookup_value(login)
        person = people.by_login[login_key]
        assert person["github_login"] == login
        assert person["chinese_name"] == chinese_name
        assert person["public"] is True
        assert person["needs_review"] is False
        assert people.by_name[login_key] is person
        assert [
            candidate
            for candidate in people.people
            if leaderboard.normalize_lookup_value(candidate.get("github_login"))
            == login_key
        ] == [person]
        assert [
            candidate
            for candidate in people.people
            if candidate.get("chinese_name") == chinese_name
        ] == [person]


def test_required_canonical_people_and_aliases_are_mapped() -> None:
    root = Path(__file__).resolve().parents[1]
    people = leaderboard.load_people_index(root)
    expected_names = {
        "kimmozag": "张睿诚",
        "qixinzhang26": "张书豪",
        "li-changwu": "李昶吾",
        "sssarrior": "李旭恒",
        "hongrugao": "高鸿儒",
        "tkhkrnx": "彭浩然",
        "mingqiwang682-boop": "王明琪",
        "yang-yjy": "杨锦昀",
        "zerojustme": "王子澳",
        "zslchase": "张森磊",
        "pluviophile-chen": "陈德斌",
        "yancanmao": "毛言粲",
        "wrp-wrp": "万瑞鹏",
        "firmamentumx": "周雨桐",
        "carsontung666": "董君瑶",
        "leixy2004": "雷欣妍",
        "luqhhh": "路庆浩",
        "sad-and-bad1231": "匡明轩",
        "sadboineedluv": "匡明轩",
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
        "remygred": "刘世峰",
        "xmdhb": "曹哲",
        "anjiangy": "李庚",
        "dzcixy": "杜忠承",
        "xsun2001": "徐晨曦",
        "renty-0": "任天宇",
        "ilnnfover": "吴天宇",
        "liu-zimo-lzm": "刘子墨",
        "oddod": "欧丹丹",
        "devilsssssss": "钱柯彤",
        "qingwanruojun": "段盈君",
        "healer-positive": "何维",
        "xiehanlong834-gif": "谢汉龙",
        "keridone": "周升晖",
        "ywhuter": "姚世文",
        "fuze1111": "沈家乐",
        "sunshine-llh": "李林浩",
        "yutiantian0115": "余天成",
        "xinyanli-0725": "李欣妍",
        "kotoriqaq0": "韦若皓",
    }
    for alias, chinese_name in expected_names.items():
        assert people.by_name[alias]["chinese_name"] == chinese_name

    assert people.by_login["moonandlife"]["profiles"]["vllm_hust"]["role_zh"] == "历史贡献者"
    assert people.by_login["succinctpaul"]["profiles"]["vllm_hust"]["role_zh"] == "工程师"
    zhao = people.by_login["curryzjj"]["profiles"]["vllm_hust"]
    assert zhao["role_zh"] == "已毕业博士生，目前已入职高校"
    xiling = people.by_login["xilinggao"]["profiles"]["vllm_hust"]
    assert xiling["research_direction_zh"] == "KV 量化"
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
        "keridone": "张书豪",
        "healer-positive": "张书豪",
        "luqhhh": "张书豪",
        "devilsssssss": "张书豪",
        "fuze1111": "张书豪",
        "liu-zimo-lzm": "张书豪",
        "oddod": "张书豪",
        "qingwanruojun": "张书豪",
        "mynameisczj": "张书豪",
        "carsontung666": "张书豪",
        "xiehanlong834-gif": "张书豪",
        "ywhuter": "张书豪",
    }
    for login, advisor in expected_advisors.items():
        profile = people.by_login[login]["profiles"]["vllm_hust"]
        assert profile["advisor_zh"] == advisor
        assert profile["role_zh"] == "学生"

    assert people.by_login["llxler"]["chinese_name"] == "雷翔麟"
    assert people.by_login["seas0"]["chinese_name"] == "刘思辰"
    assert people.by_email["xcx14@outlook.com"]["github_login"] == "xsun2001"
    assert not people.by_login["moonandlife"]["profiles"]["vllm_hust"]["staff_member"]
    assert people.by_login["moonandlife"]["profiles"]["vllm_hust"]["former_member"]
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
        "luoxiaohei",
        "张俊辉",
        "程月甲",
        "龙斌",
    }
    assert "王胜" not in {
        item["display_name"]
        for group in (
            profiles["core_members"],
            profiles["participants"],
            profiles["staff_members"],
            profiles["external_contributors"],
        )
        for item in group
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
    former_core_ids = {
        item["person_id"]
        for item in payload["core_repos"]["contributors"]
        if item.get("former_member")
    }
    assert raw_core_ids == (
        classified_core_ids | staff_core_ids | external_core_ids | former_core_ids
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
    assert by_name["张书豪"]["github_login"] == "ShuhaoZhangTony"
    assert by_name["李昶吾"]["github_login"] == "Li-changwu"
    assert by_name["李旭恒"]["github_login"] == "sssarrior"
    assert by_name["高鸿儒"]["github_login"] == "hongrugao"
    assert by_name["彭浩然"]["github_login"] == "Tkhkrnx"
    assert by_name["王明琪"]["github_login"] == "MingqiWang-coder"
    assert by_name["杨锦昀"]["github_login"] == "Yang-YJY"
    assert by_name["王子澳"]["github_login"] == "ZeroJustMe"
    assert by_name["张森磊"]["github_login"] == "zslchase"
    assert by_name["陈德斌"]["github_login"] == "pluviophile-chen"
    assert by_name["毛言粲"]["github_login"] == "yancanmao"
    assert by_name["万瑞鹏"]["github_login"] == "wrp-wrp"
    assert by_name["周雨桐"]["github_login"] == "FirmamentumX"
    assert by_name["董君瑶"]["github_login"] == "carsontung666"
    assert by_name["雷欣妍"]["github_login"] == "leixy2004"
    assert by_name["路庆浩"]["github_login"] == "Luqhhh"
    assert by_name["田景远"]["github_login"] == "CubeLander"
    assert by_name["田景远"]["role"]["zh"] == "实习生"
    assert by_name["田景远"]["advisor"]["zh"] == "张书豪"
    assert (
        by_name["田景远"]["key_contributions"]
        == "distributed, storage, profiling, development environment"
    )
    assert by_name["匡明轩"]["github_login"] == "sad-and-bad1231"
    assert by_name["匡明轩"]["advisor"]["zh"] == "张书豪"
    assert by_name["马俊豪"]["github_login"] == "kms12425"
    assert by_name["邱瑞杰"]["github_login"] == "Jerry01020"
    assert by_name["赵建军"]["github_login"] == "curryzjj"
    assert by_name["高西岭"]["github_login"] == "XilingGao"
    assert by_name["张俊辉"]["github_login"] == "junhuizhang-boop"
    assert by_name["张俊辉"]["role"]["zh"] == "工程师（派欧云）"
    assert by_name["张俊辉"]["staff_member"] is True
    assert by_name["luoxiaohei"]["role"]["zh"] == "工程师（派欧云）"
    assert by_name["luoxiaohei"]["staff_member"] is True
    assert by_name["程月甲"]["role"]["zh"] == "工程师"
    assert by_name["程月甲"]["staff_member"] is True
    assert by_name["龙斌"]["role"]["zh"] == "项目/科研助理"
    assert by_name["龙斌"]["staff_member"] is True
    assert by_name["龙斌"]["github_status"]["zh"] == "无 GitHub ID"
    assert by_name["宋功轩"]["github_status"]["zh"] == "GitHub ID 待确认"
    assert by_name["彭成"]["github_status"]["zh"] == "GitHub ID 待确认"
    assert by_name["赵建军"]["role"]["zh"] == "已毕业博士生，目前已入职高校"
    assert by_name["高西岭"]["research_direction"]["zh"] == "KV 量化"
    assert "多级KV缓存" not in by_name["高西岭"]["research_direction"]["zh"]
    assert by_name["刘世峰"]["github_login"] == "Remygred"
    assert by_name["刘世峰"]["role"]["zh"] == "华科大三实习生"
    assert by_name["刘世峰"]["advisor"]["zh"] == "张书豪"
    expected_research_interests = {
        "张书豪": "并行与分布式系统；状态管理；流处理；运行时系统；大模型推理基础设施；状态复用；记忆增强智能体中间件",
        "张睿诚": "智能体记忆体；长期记忆评测；推理技术实现；Benchmark；多模态长上下文推理",
        "刘俊": "SLO 感知的 LLM Serving 调度；MLA 与 KV Cache 优化；张量并行与多 GPU 推理解码；延迟保障与资源分配；应用感知 Serving",
        "李昶吾": "大模型推理系统软硬件协同优化；动态 MoE 推理；AI 加速器执行效率优化；Ascend NPU Host–Device 协同优化",
        "李旭恒": "KV Cache 跨请求与跨 Chunk 复用；共享选择层；缓存精度与存储权衡；vLLM、SGLang、Mooncake 与 CacheBlend",
        "高鸿儒": "动态图系统；计算机系统结构；国产硬件运行时与推理引擎优化",
        "曹哲": "Prompt/KV Cache 复用；缓存驱逐；语义感知与在线自适应策略；Agent 场景缓存生命周期管理",
        "彭浩然": "SLO-aware 调度；Workflow/Agent-aware Serving；程序感知调度；工作流状态管理",
        "王明琪": "大模型推理系统工程开发；LLM Serving；vLLM 架构；KV Cache 生命周期管理；PagedAttention；缓存置换与资源调度；长序列推理内存优化",
        "杨锦昀": "Flink 流处理；分布式数据处理；流系统与推理系统协同",
        "王子澳": "ANNS；向量流连接；多核并行；RAG 检索基础设施",
        "张森磊": "待定",
        "陈彦博": "SLO-aware 请求调度；国产硬件推理引擎适配；性能测试与工程实现",
        "朱鑫材": "智能体数据库；Agent 状态与记忆持久化；数据管理中间件",
        "陈德斌": "MoE 专家卸载优化；控制面优化（与李昶吾协作）",
        "王杰": "面向长上下文工作负载的大模型推理引擎性能优化；Prefill 阶段计算与数据搬运瓶颈；KV Cache 复用；分层缓存；运行时调度；算子优化",
        "李庚": "分布式推理加速",
        "高西岭": "KV 量化",
        "刘子墨": "待定",
        "欧丹丹": "待定",
        "钱柯彤": "vLLM-HUST 推理系统性能分析与调度优化；系统 Profiling；瓶颈定位；资源利用率提升；工程化性能改进",
        "段盈君": "算子优化；寒武纪算子开发",
        "陈子嘉": "昇腾 NPU 算子级性能调优；PyPTO Tile 编程；算子融合",
        "何维": "性能优化；算法与硬件调优；方向适应性强",
        "马俊豪": "待定",
        "匡明轩": "KV Cache 压缩；调度同步开销优化；Attention Kernel",
        "董君瑶": "向量数据库",
        "田景远": "昇腾 NPU 推理系统优化；调度优化；通信—计算重叠；多卡扩展；软硬件协同；真实负载",
        "邱瑞杰": "待定",
        "路庆浩": "Profiling；vLLM 性能问题分析与优化",
        "刘世峰": "请求调度；资源管理；KV Cache 优化；长上下文服务",
        "谢汉龙": "异构 GPU 推理分离；系统架构；资源调度；异构兼容；成本敏感型部署；自动并行",
        "周升晖": "Profiling；算子性能瓶颈分析；算子融合；减少计算冗余",
        "姚世文": "资源调度；任务卸载；复杂系统优化；LLM Serving 性能优化；智能调度；异构计算",
        "沈家乐": "KV Cache 复用；长上下文推理优化；多后端运行时适配",
        "李林浩": "待定",
        "余天成": "大模型推理方向待定；愿意根据课题安排探索相关研究",
        "李欣妍": "模型执行优化；状态管理；KV Cache 复用与压缩；多模态推理优化；AI4S 场景",
        "韦若皓": "待补充",
        "万瑞鹏": "待补充",
        "周雨桐": "待补充",
        "毛言粲": "待补充",
        "雷欣妍": "待补充",
    }
    for name, expected in expected_research_interests.items():
        assert by_name[name]["research_direction"]["zh"] == expected
        for name in ("李林浩", "余天成"):
            assert by_name[name]["role"]["zh"] == "2027 年待入学学生"
            assert by_name[name]["advisor"]["zh"] == "张书豪"
        assert by_name["李欣妍"]["role"]["zh"] == "学生"
        assert by_name["李欣妍"]["advisor"]["zh"] == "张书豪"
    assert by_name["曹哲"]["github_login"] == "xmdhb"
    assert by_name["曹哲"]["role"]["zh"] == "即将入学的研究生"
    assert by_name["曹哲"]["advisor"]["zh"] == "张书豪"
    assert by_name["李庚"]["github_login"] == "Anjiangy"
    assert by_name["李庚"]["role"]["zh"] == "马上入学的华科研究生"
    assert by_name["李庚"]["advisor"]["zh"] == "张书豪"
    assert by_name["马俊豪"]["advisor"]["zh"] == "张书豪"
    assert by_name["sunYangGitHub"]["github_login"] == "sunYangGitHub"
    assert by_name["sunYangGitHub"]["role"]["zh"] == "外校实习生"
    assert by_name["sunYangGitHub"]["advisor"]["zh"] == "张书豪"
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
    assert "github:sunyanggithub" not in unresolved_ids
    assert "github:luoxiaohei" not in unresolved_ids
    assert "author:sssarrior" not in unresolved_ids
    assert "github:kotoriqaq0" not in unresolved_ids
    assert by_name["韦若皓"]["github_login"] == "kotoriqaq0"
    assert by_name["韦若皓"]["role"]["zh"] == "学生"
    assert by_name["韦若皓"]["advisor"]["zh"] == "万瑶"

    kuang_rows = [
        item
        for item in payload["all_repos"]["contributors"]
        if item["person_id"] == "github:sad-and-bad1231"
    ]
    assert len(kuang_rows) == 1
    assert kuang_rows[0]["commits"] == 17
    assert "cccf-domestic-inference-engine-survey" in kuang_rows[0]["repos"]
    xuheng_rows = [
        item
        for item in profiles["participants"]
        if item["display_name"] == "李旭恒"
    ]
    assert len(xuheng_rows) == 1
    assert xuheng_rows[0]["person_id"] == "github:sssarrior"

    for item in by_name.values():
        assert "contribution_areas" in item
        assert "research_direction" in item
        assert item["contribution_areas"] == item["key_contributions"]
        if not item.get("github_login"):
            assert item["github_status"]["zh"]

    people_payload = json.loads((root / "profile" / "people.json").read_text())
    student_role_markers = ("学生", "研究生", "实习生")
    for person in people_payload["people"].values():
        profile = (person.get("profiles") or {}).get("vllm_hust") or {}
        role = profile.get("role_zh") or ""
        if any(marker in role for marker in student_role_markers):
            assert profile.get("advisor_zh"), (
                f"{person.get('chinese_name') or person.get('github_login')} "
                f"has role {role} but no advisor"
            )


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
