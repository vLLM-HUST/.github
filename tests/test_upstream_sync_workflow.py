"""Exercise the actual workflow shell without network access or credentials."""

import json
import os
from pathlib import Path
import subprocess

import pytest
import yaml


TEMPLATE = Path(__file__).parents[1] / "workflow-templates/hust-upstream-sync.yml"
WORKFLOW = yaml.safe_load(TEMPLATE.read_text())
STEPS = WORKFLOW["jobs"]["sync"]["steps"]


@pytest.fixture
def run_step(tmp_path):
    # A tiny GitHub CLI double lets the real bash guard/classifier/verification run.
    gh = tmp_path / "gh"
    gh.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, pathlib, sys\n"
        "a=sys.argv[1:]; scenario=os.environ.get('SCENARIO', 'ok')\n"
        "p=pathlib.Path(os.environ['FAKE_CALLS'])\n"
        "with p.open('a') as f: f.write(json.dumps(a)+'\\n')\n"
        "if '/merges' in ' '.join(a):\n"
        " errors={'conflict':'There are merge conflicts (HTTP 409)', "
        "'permission':'Cannot update workflow without workflows permission (HTTP 422)', "
        "'timeout':'Unable to determine if workflow can be updated due to timeout (HTTP 422)', "
        "'auth':'Bad credentials (HTTP 401)', 'api':'Internal error (HTTP 500)'}\n"
        " if scenario in errors: print(errors[scenario], file=sys.stderr); sys.exit(1)\n"
        " if scenario!='http204': print(json.dumps({'sha':'c'*40,'commit':{'message':'Merged upstream'}}))\n"
        "elif '/compare/' in ' '.join(a):\n"
        " endpoint=a[1]\n"
        " if scenario=='ancestry': print('diverged')\n"
        " elif endpoint.endswith('b'*40+'...'+'a'*40): print('ahead' if scenario=='noop' else 'behind')\n"
        " elif endpoint.endswith('c'*40+'...'+'a'*40): print('behind')\n"
        " else: print('ahead')\n"
        "elif '/commits/' in ' '.join(a):\n"
        " if 'official/core' in a[1]: print('b'*40)\n"
        " else:\n"
        "  reads=sum('/commits/' in line and 'test/fork' in line for line in p.read_text().splitlines())\n"
        "  print('a'*40 if reads==1 or (scenario=='stale-read' and reads==2) else 'c'*40)\n"
        "elif a[1]=='repos/test/fork':\n"
        " print(json.dumps({'default_branch':'main', 'parent':None if scenario=='not-fork' "
        "else {'full_name':'official/core'}}))\n"
        "elif a[1]=='repos/official/core': print('main')\n"
        "else: raise AssertionError(a)\n"
    )
    gh.chmod(0o755)
    sleep = tmp_path / "sleep"
    sleep.write_text("#!/bin/sh\nexit 0\n")
    sleep.chmod(0o755)

    def run(step_id, **extra):
        step = next(s for s in STEPS if s.get("id", s["name"]) == step_id)
        output, summary = tmp_path / "output", tmp_path / "summary"
        calls = tmp_path / "calls"
        env = {
            **os.environ,
            "PATH": f"{tmp_path}:{os.environ['PATH']}",
            "GITHUB_REPOSITORY": "test/fork",
            "GITHUB_REF_NAME": "main",
            "GITHUB_OUTPUT": str(output),
            "GITHUB_STEP_SUMMARY": str(summary),
            "FAKE_CALLS": str(calls),
            "APP_CLIENT_ID": "",
            "APP_PRIVATE_KEY": "",
            "HAS_SYNC_CREDENTIAL": "true",
            "UPSTREAM_REPOSITORY": "official/core",
            "UPSTREAM_BRANCH": "main",
            "TARGET_BRANCH": "main",
            "SLACK_WEBHOOK_URL": "",
            **extra,
        }
        result = subprocess.run(
            ["bash", "-c", step["run"]],
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return (
            result,
            output.read_text() if output.exists() else "",
            summary.read_text() if summary.exists() else "",
            calls.read_text() if calls.exists() else "",
        )

    return run


def test_default_branch_metadata(run_step):
    result, output, _, _ = run_step("upstream")
    assert result.returncode == 0
    assert "repository=official/core" in output
    assert "target=main" in output


@pytest.mark.parametrize(
    "env",
    [
        {"GITHUB_REF_NAME": "feature/untrusted"},
        {"SCENARIO": "not-fork"},
        {"APP_CLIENT_ID": "app-without-key"},
        {"APP_PRIVATE_KEY": "key-without-app"},
    ],
)
def test_invalid_target_or_partial_credential_fails_before_merge(run_step, env):
    result, _, _, calls = run_step("upstream", **env)
    assert result.returncode != 0
    assert "/merges" not in calls


@pytest.mark.parametrize(
    "scenario,kind",
    [
        ("conflict", "merge-conflict"),
        ("permission", "workflow-permission"),
        ("timeout", "workflow-permission"),
        ("auth", "authentication"),
        ("api", "api-error"),
        ("ancestry", "ancestry-verification"),
    ],
)
def test_sync_failure_classification(run_step, scenario, kind):
    result, output, _, _ = run_step("merge", SCENARIO=scenario)
    assert result.returncode != 0
    assert f"failure-kind={kind}" in output


def test_merge_preserves_fork_and_upstream_ancestry(run_step):
    result, output, summary, calls = run_step("merge")
    assert result.returncode == 0
    assert "has-sync-credential=true" in output
    assert "Both previous fork HEAD and observed upstream HEAD" in summary
    api_calls = [json.loads(line) for line in calls.splitlines()]
    assert sum("/compare/" in " ".join(call) for call in api_calls) == 4
    assert all("force" not in " ".join(call) for call in api_calls)
    merge = next(call for call in api_calls if "/merges" in " ".join(call))
    assert "head=" + "b" * 40 in merge
    assert "[skip ci]" in " ".join(merge)


def test_http_204_noop_still_verifies_ancestry(run_step):
    result, _, summary, calls = run_step("merge", SCENARIO="http204")
    assert result.returncode == 0
    assert "HTTP 204" in summary
    assert calls.count("/compare/") == 4


def test_noop_is_read_only_even_when_a_write_token_is_unavailable(run_step):
    result, _, summary, calls = run_step("merge", SCENARIO="noop")
    assert result.returncode == 0
    assert "No-op:" in summary
    assert "/merges" not in calls


def test_stale_branch_read_recovers_without_repeating_the_merge(run_step):
    result, _, summary, calls = run_step("merge", SCENARIO="stale-read")
    assert result.returncode == 0
    assert "Waiting for branch/compare consistency" in result.stdout
    assert calls.count("/merges") == 1
    assert "Merge response SHA: `" + "c" * 40 in summary


def test_persistent_ancestry_failure_has_a_bounded_read_retry(run_step):
    result, _, _, calls = run_step("merge", SCENARIO="ancestry")
    assert result.returncode != 0
    assert calls.count("/merges") == 1
    assert calls.count("repos/test/fork/commits/main") == 6


def test_default_token_noop_does_not_claim_credential_recovery(run_step):
    result, output, _, _ = run_step(
        "merge", HAS_SYNC_CREDENTIAL="false", SCENARIO="noop"
    )
    assert result.returncode == 0
    assert "::warning::" in result.stdout
    assert "has-sync-credential=false" in output
    recovery = next(s for s in STEPS if s["name"] == "Close recovered failure issue")
    assert "steps.merge.outputs.has-sync-credential == 'true'" in recovery["if"]


def test_missing_optional_slack_is_not_another_failure(run_step):
    result, _, _, _ = run_step("Send optional Slack failure notification")
    assert result.returncode == 0


def test_credentials_are_scoped_and_never_interpolated_into_shell():
    app = next(s for s in STEPS if s.get("id") == "app-token")
    assert len(app["uses"].split("@")[1]) == 40
    assert app["with"]["permission-workflows"] == "write"
    assert app["with"]["permission-contents"] == "write"
    assert "owner" not in app["with"]  # Current repository, not entire installation.
    for step in STEPS:
        assert "secrets." not in step.get("if", "")
        assert "${{" not in step.get("run", "")
        assert "self-hosted" not in str(step)


def test_all_shell_steps_parse_and_notifications_use_verified_body_files():
    for step in STEPS:
        if "run" in step:
            subprocess.run(["bash", "-n"], input=step["run"], text=True, check=True)
    issue = next(s for s in STEPS if s["name"] == "Create or update failure issue")
    assert '--body-file "$body"' in issue["run"]
    assert 'cmp "$body" "$stored"' in issue["run"]
    assert "select(.title ==" in issue["run"]
