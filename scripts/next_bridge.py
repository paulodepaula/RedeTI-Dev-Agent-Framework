#!/usr/bin/env python3
"""RedeTI NEXT: GitHub queue and verified deployment reporting; never executes AI."""
import argparse
import json
import pathlib
import re
import subprocess
import sys

PREFIX = "[HERMES NEXT]"
LABEL = "hermes-ready"


def run(argv, cwd=None):
    p = subprocess.run(argv, cwd=cwd, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(f"{argv[0]} command failed (exit {p.returncode}): {p.stderr.strip()[:400]}")
    return p.stdout.strip()


def project(path):
    root = run(["git", "-C", str(path), "rev-parse", "--show-toplevel"])
    url = run(["git", "-C", root, "remote", "get-url", "origin"])
    m = re.search(r"(?:github\.com[:/])([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$", url)
    if not m:
        raise ValueError("origin must be a GitHub repository URL")
    return pathlib.Path(root), m.group(1) + "/" + m.group(2)


def issue_ok(i, owner):
    return (i["title"].startswith(PREFIX)
            and i.get("author", {}).get("login", "").casefold() == owner.casefold())


def fetch(repo):
    owner = repo.split("/")[0]
    issues = json.loads(run(["gh", "issue", "list", "-R", repo, "--state", "open",
                             "--label", LABEL, "--limit", "100",
                             "--json", "number,title,body,url,author"]))
    eligible = sorted((i for i in issues if issue_ok(i, owner)), key=lambda x: x["number"])
    if not eligible:
        return {"status": "empty", "repo": repo}
    i = eligible[0]
    return {"status": "ready", "repo": repo, "issue": i["number"], "title": i["title"],
            "body": i["body"], "url": i["url"]}


def verified_sha(root, branch, expected):
    if not re.fullmatch(r"[0-9a-fA-F]{40}", expected or ""):
        raise ValueError("success requires a complete 40-character commit SHA")
    head = run(["git", "-C", str(root), "rev-parse", "HEAD"])
    current_branch = run(["git", "-C", str(root), "branch", "--show-current"])
    if current_branch != branch or head.lower() != expected.lower():
        raise RuntimeError("local branch/HEAD does not match expected deployment")
    remote = run(["git", "-C", str(root), "ls-remote", "origin", f"refs/heads/{branch}"])
    if not remote or remote.split()[0].lower() != expected.lower():
        raise RuntimeError("remote SHA does not match local HEAD; delivery not verified")
    if run(["git", "-C", str(root), "status", "--porcelain"]):
        raise RuntimeError("working tree is not clean; inspect before reporting success")
    return head


def report(root, repo, number, status, branch, commit, summary):
    owner = repo.split("/")[0]
    issue = json.loads(run(["gh", "issue", "view", str(number), "-R", repo,
                            "--json", "title,state,author,labels"]))
    if (issue["state"] != "OPEN" or not issue_ok(issue, owner)
            or LABEL not in [label["name"] for label in issue["labels"]]):
        raise ValueError("issue is not eligible")
    path = pathlib.Path(summary)
    if not path.is_file() or path.stat().st_size > 12000:
        raise ValueError("summary must be an existing UTF-8 file <= 12KB")
    body = path.read_text(encoding="utf8").strip()
    if not body:
        raise ValueError("summary is empty")
    sha = verified_sha(root, branch, commit) if status == "success" else "unverified"
    msg = (f"### RedeTI NEXT - Hermes deployment\n"
           f"**Result:** {status}\n**Branch:** {branch}\n"
           f"**Verified remote SHA:** {sha}\n\n{body}")
    run(["gh", "issue", "comment", str(number), "-R", repo, "--body", msg])
    if status == "success":
        run(["gh", "issue", "close", str(number), "-R", repo, "--reason", "completed"])
    return {"status": "reported", "repo": repo, "issue": number, "result": status, "sha": sha}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--project", default=".", help="Local checkout directory")
    sub = p.add_subparsers(dest="action", required=True)
    sub.add_parser("fetch")
    r = sub.add_parser("report")
    r.add_argument("--issue", type=int, required=True)
    r.add_argument("--status", choices=["success", "failed"], required=True)
    r.add_argument("--branch", default="dev/ai-shared")
    r.add_argument("--commit")
    r.add_argument("--summary", required=True)
    a = p.parse_args()
    try:
        root, repo = project(a.project)
        output = fetch(repo) if a.action == "fetch" else report(
            root, repo, a.issue, a.status, a.branch, a.commit, a.summary)
        print(json.dumps(output, ensure_ascii=False, indent=2))
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError, UnicodeError) as e:
        print(f"NEXT ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
