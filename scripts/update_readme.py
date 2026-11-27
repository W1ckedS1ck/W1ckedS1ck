#!/usr/bin/env python3
"""Refresh the generated parts of the profile README.

Two kinds of markers are supported:

  <!--n:key-->value<!--/n:key-->   inline counts, replaced in place
  <!-- AUTO:START --> ... <!-- AUTO:END -->   the production-signals table

Only the stdlib is used so the workflow needs no extra installs.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

README = "readme.md"
REPO = "W1ckedS1ck/DreamSeed"
TOKEN = os.environ.get("GITHUB_TOKEN")
START = "<!-- AUTO:START -->"
END = "<!-- AUTO:END -->"

STATUS = {
    "success": "✅ success",
    "failure": "❌ failure",
    "in_progress": "⏳ running",
    "queued": "⏳ queued",
    "cancelled": "⏹ cancelled",
    "skipped": "⏭ skipped",
    "neutral": "➖ neutral",
    "timed_out": "⌛ timed out",
}


def api(path: str) -> object:
    req = urllib.request.Request(
        f"https://api.github.com/{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "dreamseed-profile-readme",
            **(  # only needed for private repos and to lift rate limits
                {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
            ),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def tree(path: str) -> list[dict]:
    return api(f"repos/{REPO}/contents/{path}?per_page=100")  # type: ignore[return-value]


def count(path: str, pattern: str) -> int:
    return sum(1 for item in tree(path) if re.fullmatch(pattern, item["name"]))


def latest_run(workflow: str, branch: str | None = None) -> dict | None:
    query = f"repos/{REPO}/actions/workflows/{workflow}/runs?per_page=1"
    if branch:
        query += f"&branch={branch}"
    runs = api(query)["workflow_runs"]  # type: ignore[index]
    return runs[0] if runs else None


def latest_drill() -> tuple[str, dict | None]:
    """The drill job matters, not the run: publishing the screenshot is separate."""
    run = latest_run("test-restore.yml")
    if not run:
        return "—", None
    jobs = api(f"repos/{REPO}/actions/runs/{run['id']}/jobs?per_page=100")["jobs"]  # type: ignore[index]
    drill = next((j for j in jobs if j["name"].startswith("Restore test")), None)
    if drill:
        return STATUS.get(drill["conclusion"] or drill["status"], drill["conclusion"] or ""), run
    return STATUS.get(run["conclusion"] or run["status"], run["conclusion"] or ""), run


def fmt_date(run: dict | None) -> str:
    if not run:
        return "—"
    stamp = run.get("run_started_at") or run.get("created_at") or ""
    try:
        dt = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return "—"
    return dt.strftime("%d %b %Y")


def row(label: str, result: str, run: dict | None) -> str:
    link = f"[run]({run['html_url']})" if run else "—"
    return f"| {label} | {result} | {fmt_date(run)} · {link} |"


def signals_block() -> str:
    drill_result, drill_run = latest_drill()
    deploy_run = latest_run("deploy.yml", branch="main")
    ci_run = latest_run("ci.yml", branch="main")

    deploy_result = STATUS.get(deploy_run["conclusion"] or deploy_run["status"], "") if deploy_run else "—"
    ci_result = STATUS.get(ci_run["conclusion"] or ci_run["status"], "") if ci_run else "—"

    return "\n".join(
        [
            START,
            "| Signal | Result | Last run |",
            "| --- | --- | --- |",
            row("🧪 DR drill — restore an hourly backup on a fresh server", drill_result, drill_run),
            row("🚀 Production deploy", deploy_result, deploy_run),
            row("✅ CI on `main`", ci_result, ci_run),
            END,
        ]
    )


def rendered(readme: str) -> str:
    counts = {
        "roles": count("ansible-roles", r".+"),
        "playbooks": count("ansible", r"playbook-.*\.yml"),
        "workflows": count(".github/workflows", r".+\.yml"),
        "adrs": count("docs/adr", r"ADR-.*\.md"),
    }
    out = readme
    for key, value in counts.items():
        out, n = re.subn(
            rf"(<!--n:{key}-->).*?(<!--/n:{key}-->)",
            rf"\g<1>{value}\g<2>",
            out,
        )
        if n == 0:
            print(f"warning: no inline marker for {key}", file=sys.stderr)

    block = signals_block()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    if not pattern.search(out):
        raise SystemExit(f"missing {START} / {END} block in {README}")
    out = pattern.sub(block, out)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    out = re.sub(r"<!-- Last updated: .*? -->", f"<!-- Last updated: {stamp} -->", out)
    return out


def main() -> int:
    with open(README, encoding="utf-8") as fh:
        current = fh.read()

    updated = rendered(current)
    if updated == current:
        print("README is already up to date")
        return 0

    if "--write" in sys.argv:
        with open(README, "w", encoding="utf-8") as fh:
            fh.write(updated)
        print("README updated")
    else:
        sys.stdout.write(updated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
