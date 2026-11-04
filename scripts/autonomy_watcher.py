#!/usr/bin/env python3
"""Read-only, fail-closed GitHub issue poller for the RedeTI Hermes autonomy pilot.

This version NEVER launches Hermes, changes issues or deploys. Simulation is the only
supported mode until the agent runtime and execution gates are validated on Hermes.
"""
import argparse
import fcntl
import json
import pathlib
import re
import subprocess
import sys
from contextlib import contextmanager

import next_bridge as bridge

REPO_PATTERN = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
BRANCH_PATTERN = re.compile(r"[A-Za-z0-9._/-]+\Z")
SHA_PATTERN = re.compile(r"[0-9a-fA-F]{40}\Z")


def config_load(path):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("mode") != "simulate":
        raise ValueError("only mode=simulate is supported; live execution is not implemented")
    if set(data) != {"mode", "projects"}:
        raise ValueError("unexpected configuration keys")
    projects = data.get("projects")
    if not isinstance(projects, list):
        raise ValueError("projects must be a list")
    seen = set()
    for p in projects:
        if not isinstance(p, dict):
            raise ValueError("each project must be an object")
        if set(p) != {"repository", "checkout", "allowed_branches"}:
            raise ValueError("unexpected project configuration keys")
        repo, checkout, branches = p.get("repository"), p.get("checkout"), p.get("allowed_branches")
        if not isinstance(repo, str) or not REPO_PATTERN.fullmatch(repo):
            raise ValueError("repository must be owner/name")
        if repo.lower() in seen:
            raise ValueError("duplicate repository in allowlist")
        seen.add(repo.lower())
        if not isinstance(checkout, str) or not pathlib.Path(checkout).is_absolute():
            raise ValueError(f"{repo}: checkout must be an absolute path")
        if not isinstance(branches, list) or not branches or not all(
            isinstance(b, str) and BRANCH_PATTERN.fullmatch(b) and ".." not in b and not b.startswith("-")
            for b in branches
        ):
            raise ValueError(f"{repo}: allowed_branches must contain safe branch names")
    return data


def issue_metadata(issue, owner, branches):
    if (not isinstance(issue, dict) or not isinstance(issue.get("title"), str)
            or not isinstance(issue.get("author"), dict)):
        return None, "malformed issue metadata"
    if not bridge.issue_ok(issue, owner):
        return None, "issue author or prefix not authorized"
    labels = {label.get("name") for label in issue.get("labels", []) if isinstance(label, dict)}
    if "hermes-ready" not in labels:
        return None, "missing hermes-ready label"
    if "hermes-running" in labels:
        return None, "already claimed"
    body = issue.get("body") or ""
    branch_match = re.search(r"^\*\*Branch:\*\*\s*(\S+)\s*$", body, re.MULTILINE)
    sha_match = re.search(r"^\*\*Commit SHA:\*\*\s*([0-9a-fA-F]{40})\s*$", body, re.MULTILINE)
    if not branch_match or not sha_match:
        return None, "Issue needs exact Branch and 40-character Commit SHA lines"
    branch, sha = branch_match.group(1), sha_match.group(1).lower()
    if branch not in branches or not BRANCH_PATTERN.fullmatch(branch) or ".." in branch:
        return None, "branch not allowlisted"
    if not SHA_PATTERN.fullmatch(sha):
        return None, "invalid SHA"
    return {"branch": branch, "sha": sha}, None


def fetch_issues(repo):
    args = ["gh", "issue", "list", "-R", repo, "--state", "open",
            "--label", "hermes-ready", "--limit", "100", "--json",
            "number,title,body,url,author,labels"]
    result = subprocess.run(args, text=True, capture_output=True, timeout=20, check=False)
    if result.returncode:
        raise RuntimeError(f"gh issue list failed (exit {result.returncode})")
    rows = json.loads(result.stdout)
    if not isinstance(rows, list):
        raise ValueError("GitHub issue query did not return a list")
    return sorted(rows, key=lambda i: i.get("number", 0))


def poll_projects(config):
    events = []
    for p in config["projects"]:
        repo = p["repository"]
        try:
            checkout = pathlib.Path(p["checkout"])
            if not checkout.is_dir():
                raise ValueError("checkout does not exist")
            _, actual_repo = bridge.project(checkout)
            if actual_repo.lower() != repo.lower():
                raise ValueError("checkout origin does not match allowlisted repository")
            issues = fetch_issues(repo)
            for issue in issues:
                info, reason = issue_metadata(issue, repo.split("/")[0], p["allowed_branches"])
                if info:
                    events.append({"event": "would_dispatch", "mode": "simulate", "repo": repo,
                                   "issue": issue["number"], "branch": info["branch"], "sha": info["sha"]})
                    break  # At most one eligible issue per project per scan.
                events.append({"event": "blocked", "repo": repo,
                               "issue": issue.get("number"), "reason": reason})
            if not issues:
                events.append({"event": "empty", "repo": repo})
        except (ValueError, RuntimeError, OSError, json.JSONDecodeError, subprocess.TimeoutExpired, TypeError, KeyError) as exc:
            events.append({"event": "blocked", "repo": repo, "reason": str(exc)[:240]})
    if not config["projects"]:
        events.append({"event": "idle", "reason": "no allowlisted projects configured"})
    return events


@contextmanager
def exclusive_lock(state_dir):
    base = pathlib.Path(state_dir).expanduser()
    base.mkdir(mode=0o700, parents=True, exist_ok=True)
    lockfile = base / "autonomy.lock"
    with lockfile.open("a+", encoding="utf-8") as fd:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Safe 60-second autonomous polling pilot; simulation only")
    ap.add_argument("--config", required=True)
    ap.add_argument("--state-dir", default="~/.local/state/redeti-hermes-autonomy")
    args = ap.parse_args(argv)
    try:
        config = config_load(args.config)
        with exclusive_lock(args.state_dir):
            events = poll_projects(config)
        for event in events:
            print(json.dumps(event, ensure_ascii=False, sort_keys=True))
        return 0 if not any(e["event"] == "blocked" for e in events) else 2
    except (ValueError, OSError, json.JSONDecodeError, BlockingIOError) as exc:
        print(json.dumps({"event": "fatal", "reason": str(exc)[:240]}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
