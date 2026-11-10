#!/usr/bin/env python3
"""Render a README hero banner (dark + light, 1280x400 @2x) and a ready-to-paste README header.

Usage: render_hero.py facts.json copy.json -o out_dir
copy.json keys:
  headline   (required, <= 56 chars)  what the project does for the reader
  subline    (required, <= 120 chars) how it works, in the project's own terms
  why        (required, 3 items, each <= 90 chars) concrete reasons, each traceable to the README
  quickstart (optional list of lines) copied exactly from the README
  accent     (optional hex)
  npm        (optional npm package name, adds a version badge)
  docs_url   (optional)
Writes hero-dark.png, hero-light.png, hero.html and HERO.md.
"""
import argparse, html, json, os, shutil, subprocess, sys, pathlib, urllib.parse

def chrome():
    for c in [os.environ.get("CHROME"), "google-chrome", "chromium", "chromium-browser", "chrome",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]:
        if c and (shutil.which(c) or os.path.exists(c)):
            return shutil.which(c) or c
    return None

def page(f, c, dark):
    bg, fg, muted, line = ("#0b0b0f", "#f5f5f7", "#a0a0ab", "#1c1c24") if dark else ("#ffffff", "#0b0b0f", "#55555f", "#ececf1")
    acc = c.get("accent", "#ff4d4d"); e = html.escape
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1280px;height:400px;overflow:hidden}}
body{{background:{bg};color:{fg};font-family:'IBM Plex Sans','Inter','Helvetica Neue',Arial,sans-serif;position:relative}}
.bar{{position:absolute;left:0;top:0;bottom:0;width:10px;background:{acc}}}
.dots{{position:absolute;right:0;top:0;bottom:0;width:420px;background-image:radial-gradient({line} 2px,transparent 2px);background-size:22px 22px;-webkit-mask-image:linear-gradient(90deg,transparent,#000 60%)}}
.wrap{{position:absolute;inset:0;padding:56px 80px;display:flex;flex-direction:column;justify-content:center}}
.repo{{font-family:'IBM Plex Mono',monospace;font-size:24px;color:{muted}}}
.repo b{{color:{acc};font-weight:600}}
h1{{font-size:64px;line-height:1.05;font-weight:700;letter-spacing:-1.5px;margin-top:18px;max-width:1000px;text-wrap:balance}}
p{{font-size:26px;line-height:1.35;color:{muted};margin-top:18px;max-width:940px}}
</style></head><body><div class="bar"></div><div class="dots"></div><div class="wrap">
<div class="repo">{e(f['owner'])}/<b>{e(f['name'])}</b></div>
<h1>{e(c['headline'])}</h1><p>{e(c['subline'])}</p></div></body></html>"""

def badges(f, c):
    r = f["repo"]; out = []
    out.append(f"[![GitHub stars](https://img.shields.io/github/stars/{r}?style=flat-square)]({f['url']}/stargazers)")
    if f.get("latest_release"):
        out.append(f"[![Release](https://img.shields.io/github/v/release/{r}?style=flat-square)]({f['url']}/releases)")
    if c.get("npm"):
        n = urllib.parse.quote(c["npm"], safe="@/")
        out.append(f"[![npm](https://img.shields.io/npm/v/{n}?style=flat-square)](https://www.npmjs.com/package/{c['npm']})")
    if f.get("license"):
        out.append(f"[![License](https://img.shields.io/github/license/{r}?style=flat-square)]({f['url']}/blob/HEAD/LICENSE)")
    return " ".join(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("facts"); ap.add_argument("copy"); ap.add_argument("-o", "--out", default=".")
    a = ap.parse_args()
    f = json.load(open(a.facts)); c = json.load(open(a.copy))
    for k, lim in (("headline", 56), ("subline", 120)):
        if not c.get(k): sys.exit(f"copy.json missing {k}")
        if len(c[k]) > lim: sys.exit(f"{k} is {len(c[k])} chars; limit {lim}")
    why = c.get("why", [])
    if len(why) != 3 or any(len(w) > 90 for w in why):
        sys.exit("copy.json 'why' must be exactly 3 items, each <= 90 chars")
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    ch = chrome()
    for mode in ("dark", "light"):
        h = out / f"hero-{mode}.html"; h.write_text(page(f, c, mode == "dark"))
        if ch:
            subprocess.run([ch, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                            "--force-device-scale-factor=2", "--window-size=1280,400",
                            f"--screenshot={(out/f'hero-{mode}.png').resolve()}", f"file://{h.resolve()}"],
                           check=True, capture_output=True, timeout=60)
    if not ch:
        print("No Chrome found: screenshot hero-dark.html / hero-light.html at 1280x400.", file=sys.stderr)
    alt = html.escape(f"{f['name']}: {c['headline']}", quote=True)
    md = [
        '<p align="center">',
        '  <picture>',
        '    <source media="(prefers-color-scheme: dark)" srcset="./hero-dark.png">',
        f'    <img alt="{alt}" src="./hero-light.png" width="100%">',
        '  </picture>',
        '</p>', '',
        f'<p align="center"><b>{html.escape(c["headline"])}</b><br>{html.escape(c["subline"])}</p>', '',
        f'<p align="center">', '', badges(f, c), '', '</p>', '',
    ]
    if c.get("quickstart"):
        md += ["## Quick start", "", "```bash", *c["quickstart"], "```", ""]
    md += ["## Why", ""] + [f"- {w}" for w in why] + [""]
    if c.get("docs_url"):
        md += [f"[Docs]({c['docs_url']})", ""]
    (out / "HERO.md").write_text("\n".join(md))
    print(out / "HERO.md")

if __name__ == "__main__":
    main()
