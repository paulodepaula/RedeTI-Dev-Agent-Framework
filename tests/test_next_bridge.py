import pathlib
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import next_bridge as bridge


class BridgeTests(unittest.TestCase):
    def test_author_and_prefix_required(self):
        good = {"title": "[HERMES NEXT] update", "author": {"login": "owner"}}
        self.assertTrue(bridge.issue_ok(good, "owner"))
        self.assertFalse(bridge.issue_ok(good, "different"))
        self.assertFalse(bridge.issue_ok({"title": "something else", "author": {"login": "owner"}}, "owner"))

    def test_queue_order_and_empty(self):
        issues = [
            {"number": 7, "title": "[HERMES NEXT] B", "author": {"login": "owner"}, "body": "B", "url": "7"},
            {"number": 2, "title": "[HERMES NEXT] A", "author": {"login": "owner"}, "body": "A", "url": "2"},
        ]
        with patch.object(bridge, "run", return_value=__import__("json").dumps(issues)):
            self.assertEqual(bridge.fetch("owner/proj")["issue"], 2)
        with patch.object(bridge, "run", return_value="[]"):
            self.assertEqual(bridge.fetch("owner/proj")["status"], "empty")

    def test_success_requires_sha(self):
        with self.assertRaises(ValueError):
            bridge.verified_sha(pathlib.Path("."), "dev/ai-shared", None)
        with self.assertRaises(ValueError):
            bridge.verified_sha(pathlib.Path("."), "dev/ai-shared", "abc")

    def test_remote_verification(self):
        sha = "a" * 40
        def cmd(argv, cwd=None):
            if "rev-parse" in argv:
                return sha
            if "branch" in argv:
                return "dev/ai-shared"
            if "ls-remote" in argv:
                return sha + "\trefs/heads/dev/ai-shared"
            return ""
        with patch.object(bridge, "run", side_effect=cmd):
            self.assertEqual(bridge.verified_sha(pathlib.Path("."), "dev/ai-shared", sha), sha)

    def test_targeted_fetch_never_uses_another_issue(self):
        selected = {
            "number": 2, "title": "[HERMES NEXT] Safe test",
            "body": "Only tests", "url": "2", "state": "OPEN",
            "author": {"login": "owner"}, "labels": [{"name": "hermes-ready"}]
        }
        def fake_run(args, cwd=None):
            self.assertEqual(args[:4], ["gh", "issue", "view", "2"])
            return __import__("json").dumps(selected)
        with patch.object(bridge, "run", side_effect=fake_run):
            result = bridge.fetch("owner/proj", issue_number=2)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["issue"], 2)

    def test_targeted_fetch_fails_closed(self):
        bad = {
            "number": 27, "title": "[HERMES NEXT] Other task",
            "body": "Other", "url": "27", "state": "OPEN",
            "author": {"login": "owner"}, "labels": [{"name": "hermes-ready"}]
        }
        with patch.object(bridge, "run", return_value=__import__("json").dumps(bad)):
            self.assertEqual(bridge.fetch("owner/proj", issue_number=2)["status"], "blocked")
        bad["number"] = 2
        bad["labels"] = []
        with patch.object(bridge, "run", return_value=__import__("json").dumps(bad)):
            self.assertEqual(bridge.fetch("owner/proj", issue_number=2)["status"], "blocked")



if __name__ == "__main__":
    unittest.main()
