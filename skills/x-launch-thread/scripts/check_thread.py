#!/usr/bin/env python3
"""Lint an X thread draft before a human posts it.

Usage: check_thread.py thread.md [--facts facts.json] [--long-posts]
thread.md format: posts separated by a line containing only '---'.
A post starting with 'REPLY:' is the first reply (where the link goes).

Checks:
- length per post using X's weighting (URLs = 23, most CJK/emoji = 2, else 1); limit 280
  (--long-posts lifts the limit for Premium accounts but still warns past 280)
- at most 1 hashtag per post, no @-mention lists, no engagement bait phrases
- links only in the REPLY post (keeps the main posts readable; your choice to override)
- every number in the thread appears in facts.json (catches invented stats)
Exit code 1 if any ERROR.
"""
import argparse, json, re, sys, unicodedata

URL = re.compile(r"https?://\S+|\b[\w-]+\.(?:com|dev|io|ai|sh|app|org|net)\b(?:/\S*)?")
BAIT = ["rt if", "retweet if", "like if", "follow for", "follow me", "drop a", "comment below",
        "who else", "smash", "don't miss", "you won't believe", "game changer", "game-changer", "🧵👇"]

def weight(text):
    t = URL.sub("x" * 23, text)
    n = 0
    for ch in t:
        cp = ord(ch)
        if cp <= 0x10FF or 0x2000 <= cp <= 0x200D or 0x2010 <= cp <= 0x201F or 0x2032 <= cp <= 0x2037:
            n += 1
        else:
            n += 2
    return n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("thread"); ap.add_argument("--facts"); ap.add_argument("--long-posts", action="store_true")
    a = ap.parse_args()
    posts = [p.strip() for p in re.split(r"^\s*---\s*$", open(a.thread).read(), flags=re.M) if p.strip()]
    facts = open(a.facts).read() if a.facts else None
    errs = warns = 0
    for i, p in enumerate(posts, 1):
        is_reply = p.startswith("REPLY:")
        body = p[len("REPLY:"):].strip() if is_reply else p
        w = weight(body); tag = "reply" if is_reply else f"post {i}"
        msgs = []
        if w > 280:
            if a.long_posts: msgs.append(("WARN", f"{w} chars (over 280, OK only on Premium)"))
            else: msgs.append(("ERROR", f"{w} chars > 280"))
        if len(re.findall(r"(?<!\w)#\w+", body)) > 1: msgs.append(("ERROR", "more than 1 hashtag"))
        if len(re.findall(r"(?<!\w)@\w+", body)) > 2: msgs.append(("WARN", "3+ @mentions reads as spam"))
        low = body.lower()
        for b in BAIT:
            if b in low: msgs.append(("ERROR", f"engagement bait: '{b}'"))
        if URL.search(body) and not is_reply: msgs.append(("WARN", "link in a main post; consider moving it to the REPLY"))
        if facts:
            for num in re.findall(r"\b\d[\d,.]*k?\b", body):
                core = num.rstrip(".,")
                if len(core) >= 2 and core not in facts and core.replace(",", "") not in facts:
                    msgs.append(("WARN", f"number '{core}' not found in facts.json; verify or remove"))
        print(f"[{tag}] {w}/280" + ("" if msgs else "  ok"))
        for lvl, m in msgs:
            print(f"   {lvl}: {m}")
            errs += lvl == "ERROR"; warns += lvl == "WARN"
    print(f"\n{len(posts)} posts, {errs} errors, {warns} warnings")
    sys.exit(1 if errs else 0)

if __name__ == "__main__":
    main()
