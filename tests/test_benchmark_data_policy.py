import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "policy", Path(__file__).resolve().parents[1] / "scripts/benchmark_data_policy.py"
)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class PolicyTests(unittest.TestCase):
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
