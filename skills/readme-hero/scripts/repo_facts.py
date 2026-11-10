#!/usr/bin/env python3
"""Collect verifiable facts about a public GitHub repo as JSON.

Usage: repo_facts.py owner/repo [-o facts.json]
Uses the public GitHub REST API. Set GITHUB_TOKEN to raise the rate limit (optional).
Every field comes from the API or the README; nothing is invented.
"""
import argparse, base64, json, os, re, sys, urllib.request, datetime

API = "https://api.github.com"

def get(path):
    req = urllib.request.Request(API + path, headers={"Accept": "application/vnd.github+json", "User-Agent": "launchkit-skills"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

def first_code_block(md, langs=("bash", "sh", "shell", "console", "")):
    for m in re.finditer(r"```([a-zA-Z]*)\n(.*?)```", md, re.S):
        if m.group(1).lower() in langs:
            lines = [l.split("#")[0].rstrip() if not l.strip().startswith("#") else "" for l in m.group(2).splitlines()]
            lines = [l for l in lines if l.strip()]
            if lines:
                return lines
    return []

def tagline(md):
    for line in md.splitlines():
        s = line.strip()
        if not s or s.startswith(("#", "<", "[", "!", ">", "|", "```", "-", "*")):
            continue
        return re.sub(r"[`*_]", "", s)
    return ""

def human(n):
    return f"{n/1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)

def human_date(iso):
    """UTC calendar date, e.g. 'Nov 10, 2026'. Use this in copy instead of 'last night'."""
    if not iso:
        return None
    dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(datetime.timezone.utc)
    return dt.strftime("%b %d, %Y").replace(" 0", " ")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    d = get(f"/repos/{a.repo}")
    if not d:
        sys.exit(f"repo not found: {a.repo}")
    rel = get(f"/repos/{a.repo}/releases/latest") or {}
    rd = get(f"/repos/{a.repo}/readme") or {}
    md = base64.b64decode(rd.get("content", "")).decode("utf-8", "replace") if rd else ""
    lic = (d.get("license") or {}).get("spdx_id")
    facts = {
        "repo": d["full_name"],
        "url": d["html_url"],
        "owner": d["owner"]["login"],
        "name": d["name"],
        "description": d.get("description") or "",
        "readme_tagline": tagline(md),
        "stars": d["stargazers_count"],
        "stars_human": human(d["stargazers_count"]),
        "forks": d["forks_count"],
        "language": d.get("language"),
        "license": lic if lic and lic != "NOASSERTION" else None,
        "homepage": d.get("homepage") or None,
        "topics": d.get("topics", []),
        "latest_release": rel.get("tag_name"),
        "latest_release_at": rel.get("published_at"),
        "latest_release_date": human_date(rel.get("published_at")),
        "pushed_at": d.get("pushed_at"),
        "install_lines": first_code_block(md)[:3],
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "fetched_on": human_date(datetime.datetime.now(datetime.timezone.utc).isoformat()),
    }
    out = json.dumps(facts, indent=2)
    if a.out:
        open(a.out, "w").write(out + "\n")
    print(out)

if __name__ == "__main__":
    main()
