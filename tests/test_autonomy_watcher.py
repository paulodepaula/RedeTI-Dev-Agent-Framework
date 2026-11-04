import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import autonomy_watcher as watcher

SHA = "a" * 40


def issue(number=3, body=None, author="owner", labels=None):
    if body is None:
        body = f"**Branch:** dev/ai-shared\n**Commit SHA:** {SHA}\n"
    return {"number": number, "title": "[HERMES NEXT] test", "author": {"login": author},
            "labels": labels if labels is not None else [{"name": "hermes-ready"}],
            "body": body, "url": "https://github.com/owner/repo/issues/3"}


class PollTests(unittest.TestCase):
    def test_config_rejects_live_execution(self):
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "config.json"
            path.write_text(json.dumps({"mode": "live", "projects": []}))
            with self.assertRaisesRegex(ValueError, "only mode=simulate"):
                watcher.config_load(path)

    def test_no_projects_is_safe(self):
        self.assertEqual(watcher.poll_projects({"mode": "simulate", "projects": []})[0]["event"], "idle")

    def test_invalid_duplicate_and_relative_checkout_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "config.json"
            for projects in [
                [{"repository": "owner/repo", "checkout": "relative", "allowed_branches": ["main"]}],
                [{"repository": "owner/repo", "checkout": "/a", "allowed_branches": ["main"]},
                 {"repository": "owner/repo", "checkout": "/b", "allowed_branches": ["main"]}],
            ]:
                path.write_text(json.dumps({"mode": "simulate", "projects": projects}))
                with self.assertRaises(ValueError):
                    watcher.config_load(path)

    def test_author_and_labels_enforced(self):
        for bad in (issue(author="attacker"), issue(labels=[]),
                    issue(labels=[{"name": "hermes-ready"}, {"name": "hermes-running"}])):
            self.assertIsNone(watcher.issue_metadata(bad, "owner", ["dev/ai-shared"])[0])

    def test_malformed_issue_is_rejected(self):
        self.assertIsNone(watcher.issue_metadata({"title": None}, "owner", ["main"])[0])

    def test_branch_allowlist_and_exact_sha_required(self):
        for bad in (issue(body=f"**Branch:** main\n**Commit SHA:** {SHA}"),
                    issue(body="**Branch:** dev/ai-shared\n**Commit SHA:** abc"),
                    issue(body="deploy everything")):
            self.assertIsNone(watcher.issue_metadata(bad, "owner", ["dev/ai-shared"])[0])
        result, reason = watcher.issue_metadata(issue(), "owner", ["dev/ai-shared"])
        self.assertIsNone(reason)
        self.assertEqual(result["sha"], SHA)

    def test_checkout_mismatch_blocks_without_querying_issues(self):
        with tempfile.TemporaryDirectory() as td:
            p = {"repository": "owner/repo", "checkout": td, "allowed_branches": ["dev/ai-shared"]}
            with patch.object(watcher.bridge, "project", return_value=(pathlib.Path(td), "other/repo")):
                with patch.object(watcher, "fetch_issues") as fetch:
                    events = watcher.poll_projects({"projects": [p]})
                    self.assertEqual(events[0]["event"], "blocked")
                    fetch.assert_not_called()

    def test_simulate_one_issue_no_execution(self):
        with tempfile.TemporaryDirectory() as td:
            p = {"repository": "owner/repo", "checkout": td, "allowed_branches": ["dev/ai-shared"]}
            with patch.object(watcher.bridge, "project", return_value=(pathlib.Path(td), "owner/repo")):
                with patch.object(watcher, "fetch_issues", return_value=[issue(4), issue(5)]):
                    events = watcher.poll_projects({"projects": [p]})
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["event"], "would_dispatch")
            self.assertEqual(events[0]["issue"], 4)

    def test_end_to_end_simulation_with_fake_gh(self):
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "config.json"
            path.write_text(json.dumps({"mode": "simulate", "projects": [
                {"repository": "owner/repo", "checkout": td, "allowed_branches": ["dev/ai-shared"]}]}))
            with patch.object(watcher.bridge, "project", return_value=(pathlib.Path(td), "owner/repo")):
                fake = subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps([issue()]), stderr="")
                with patch.object(watcher.subprocess, "run", return_value=fake) as command:
                    self.assertEqual(watcher.main(["--config", str(path), "--state-dir", td + "/state"]), 0)
                    self.assertEqual(command.call_count, 1)
                    self.assertEqual(command.call_args.args[0][:3], ["gh", "issue", "list"])

    def test_lock_prevents_concurrent_instances(self):
        with tempfile.TemporaryDirectory() as td:
            with watcher.exclusive_lock(td):
                with self.assertRaises(BlockingIOError):
                    with watcher.exclusive_lock(td):
                        pass


if __name__ == "__main__":
    unittest.main()
