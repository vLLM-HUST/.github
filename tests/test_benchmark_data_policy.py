import importlib.util
import copy
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "policy", Path(__file__).resolve().parents[1] / "scripts/benchmark_data_policy.py"
)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class PolicyTests(unittest.TestCase):
    def reviewed_case(self):
        row = dict(
            filename="scripts/archive.py",
            previous_filename="evidence/archive.py",
            status="renamed",
            sha="a" * 40,
            patch="@@ -1 +1 @@\n-old\n+new",
            additions=1,
            deletions=1,
            changes=2,
        )
        ledger = {
            "schema": 1,
            "reviews": [
                dict(
                    repository="org/mod",
                    pull_request=17,
                    path=row["filename"],
                    fingerprint_sha256=policy.review_fingerprint(row),
                )
            ],
        }
        return row, ledger

    def reviewed_check(self, row, ledger, repo="org/mod", number=17):
        pages = [[row]]
        return policy.apply_trusted_reviews(
            pages, policy.check_pr(pages, 1), repo, number, ledger
        )

    def test_exact_central_review_only(self):
        row, ledger = self.reviewed_case()
        self.assertTrue(policy.check_pr([[row]], 1))
        self.assertEqual(self.reviewed_check(row, ledger), [])
        self.assertTrue(self.reviewed_check(row, ledger, repo="other/mod"))
        self.assertTrue(self.reviewed_check(row, ledger, number=18))
        self.assertTrue(self.reviewed_check(row, {"schema": 1, "reviews": []}))

    def test_changed_review_identity_fails_closed(self):
        original, ledger = self.reviewed_case()
        for key, value in dict(
            filename="scripts/other.py",
            previous_filename="runs/other.py",
            status="modified",
            sha="b" * 40,
            patch="+different",
            additions=2,
            deletions=2,
            changes=4,
        ).items():
            row = {**original, key: value}
            with self.subTest(field=key):
                self.assertTrue(self.reviewed_check(row, ledger))

    def test_missing_diff_sha_and_invalid_ledger_rejected(self):
        row, ledger = self.reviewed_case()
        for field in ("patch", "sha"):
            bad = copy.deepcopy(row)
            bad.pop(field)
            with self.assertRaises(ValueError):
                self.reviewed_check(bad, ledger)
        with self.assertRaises(ValueError):
            self.reviewed_check(row, {})
        with self.assertRaises(ValueError):
            policy.check_pr([[row, row]], 2)

    def test_review_does_not_approve_other_data(self):
        row, ledger = self.reviewed_case()
        pages = [[row, dict(filename="results/new.json", status="added")]]
        self.assertEqual(
            policy.apply_trusted_reviews(
                pages, policy.check_pr(pages, 2), "org/mod", 17, ledger
            ),
            ["results/new.json"],
        )

    def test_public_inventory_excludes_private_and_unknown_visibility(self):
        for visibility in ("private", "internal", None):
            self.assertFalse(
                policy.auditable_repo(
                    {"name": "example", "archived": False, "visibility": visibility}
                )
            )
        self.assertTrue(
            policy.auditable_repo(
                {"name": "example", "archived": False, "visibility": "public"}
            )
        )

    def check(self, **row):
        return policy.check_pr([[row]], 1)

    def test_removal_allowed(self):
        self.assertEqual(self.check(filename="results/a.json", status="removed"), [])

    def test_data_and_rename_rejected(self):
        self.assertTrue(self.check(filename="results/a.json", status="added"))
        self.assertTrue(
            self.check(
                filename="src/a.txt", previous_filename="runs/a.json", status="renamed"
            )
        )

    def test_document_measurements_reviewed(self):
        self.assertTrue(
            self.check(
                filename="README.md",
                status="modified",
                patch="+Measured throughput: 42 tokens/s",
            )
        )
        self.assertEqual(
            self.check(
                filename="README.md",
                status="modified",
                patch="+See the benchmark source link.",
            ),
            [],
        )

    def test_missing_and_partial_fail_closed(self):
        with self.assertRaises(ValueError):
            policy.check_pr([[]], 1)
        self.assertTrue(self.check(filename="README.md", status="modified"))

    def test_fixture_not_blanket_exemption(self):
        self.assertTrue(
            self.check(filename="tests/fixtures/results/a.json", status="added")
        )

    def test_code_allowed(self):
        self.assertEqual(
            self.check(
                filename="src/engine.py", status="modified", patch="+latency = 12"
            ),
            [],
        )

    def test_drift_deletions_allowed_changes_blocked(self):
        baseline = {"mod": {"paths": {"results/a.json": "old"}, "assets": {}}}
        self.assertEqual(
            policy.drift(baseline, {"mod": {"paths": {}, "assets": {}}}), []
        )
        self.assertTrue(
            policy.drift(
                baseline, {"mod": {"paths": {"results/a.json": "new"}, "assets": {}}}
            )
        )


if __name__ == "__main__":
    unittest.main()
