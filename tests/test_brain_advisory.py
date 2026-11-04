import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import next_bridge as bridge


class BrainAdvisoryTests(unittest.TestCase):
    repo = "paulodepaula/demo"

    def plan(self, *, authorized=False):
        return {
            "schema": "redeti-brain-orchestrator/v1",
            "owner": "paulodepaula",
            "private_repositories_included": False,
            "execution_authorized": authorized,
            "hermes_execution_triggered": False,
            "github_write_actions": False,
            "backlog": [{"repository": self.repo, "number": 2, "state": "dependency_pending",
                         "priority": "unclassified", "url": "https://github.com/paulodepaula/demo/issues/2"}],
        }

    def invoke(self, payload):
        with tempfile.TemporaryDirectory() as home:
            tool = pathlib.Path(home) / "Projetos" / "redeti-brain-core" / "brain_orchestrator.py"
            tool.parent.mkdir(parents=True)
            tool.write_text("# existing local read-only tool")
            process = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=json.dumps(payload), stderr=""
            )
            with patch.object(pathlib.Path, "home", return_value=pathlib.Path(home)):
                with patch.object(bridge.subprocess, "run", return_value=process) as runner:
                    info = bridge.brain_advisory(self.repo, 2)
                    self.assertEqual(runner.call_args.args[0][3:],
                                     ["plan", "--owner", "paulodepaula", "--format", "json"])
                    self.assertFalse(runner.call_args.kwargs.get("shell", False))
            return info

    def test_status_remains_advisory(self):
        item = self.invoke(self.plan())
        self.assertEqual(item["status"], "observed")
        self.assertEqual(item["review_state"], "dependency_pending")
        self.assertFalse(item["execution_authorized"])

    def test_rejects_plan_that_claims_authorization(self):
        self.assertEqual(self.invoke(self.plan(authorized=True))["status"], "unavailable")

    def test_missing_local_brain_is_nonblocking(self):
        with tempfile.TemporaryDirectory() as home:
            with patch.object(pathlib.Path, "home", return_value=pathlib.Path(home)):
                with patch.object(bridge.subprocess, "run") as runner:
                    self.assertEqual(bridge.brain_advisory(self.repo, 2)["status"], "unavailable")
                    runner.assert_not_called()

    def test_next_fetch_only_adds_advice(self):
        item = {"number":2,"title":"[HERMES NEXT] Task","body":"task body",
                "url":"https://github.com/paulodepaula/demo/issues/2",
                "author":{"login":"paulodepaula"}}
        with patch.object(bridge, "run", return_value=json.dumps([item])):
            with patch.object(bridge, "brain_advisory", return_value={
                "status":"not_in_sample","advisory_only":True,"execution_authorized":False}):
                result = bridge.fetch(self.repo)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["issue"], 2)
        self.assertEqual(result["body"], "task body")
        self.assertFalse(result["brain_advisory"]["execution_authorized"])

    def test_no_issue_skips_brain_lookup(self):
        with patch.object(bridge, "run", return_value="[]"):
            with patch.object(bridge, "brain_advisory") as advisor:
                self.assertEqual(bridge.fetch(self.repo)["status"], "empty")
                advisor.assert_not_called()


if __name__ == "__main__":
    unittest.main()
