#!/usr/bin/env python3
"""Render a 1200x630 Open Graph / social card from repo facts + copy.

Usage: render_og.py facts.json copy.json -o out_dir
copy.json keys:
  headline  (required, <= 48 chars)   the one promise of the project
  subline   (required, <= 110 chars)  how it works / who it's for
  command   (optional)                one install or usage line shown in a terminal strip
  accent    (optional hex, default #ff4d4d)
  theme     (optional: "dark" | "light", default dark)
Writes og.html and og.png (needs Chrome/Chromium on PATH, or set CHROME=/path).
"""
import argparse, html, json, os, shutil, subprocess, sys, pathlib

def chrome():
    for c in [os.environ.get("CHROME"), "google-chrome", "chromium", "chromium-browser", "chrome",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]:
        if c and (shutil.which(c) or os.path.exists(c)):
            return shutil.which(c) or c
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("facts"); ap.add_argument("copy"); ap.add_argument("-o", "--out", default=".")
    a = ap.parse_args()
    f = json.load(open(a.facts)); c = json.load(open(a.copy))
    for k, lim in (("headline", 48), ("subline", 110)):
        if not c.get(k):
            sys.exit(f"copy.json missing {k}")
        if len(c[k]) > lim:
            sys.exit(f"{k} is {len(c[k])} chars; limit {lim}. Shorten it.")
    dark = c.get("theme", "dark") != "light"
    bg, fg, muted, panel = ("#0b0b0f", "#f5f5f7", "#9a9aa5", "#16161d") if dark else ("#fafafa", "#0b0b0f", "#5b5b66", "#ececf0")
    acc = c.get("accent", "#ff4d4d")
    chips = [f"★ {f['stars_human']}"]
    if f.get("language"): chips.append(f["language"])
    if f.get("license"): chips.append(f["license"])
    if f.get("latest_release"): chips.append(f["latest_release"])
    e = html.escape
    cmd = c.get("command")
    # Fit the command strip: shrink font for long lines instead of truncating.
    room = 1056 - sum(len(x) * 13 + 50 for x in chips) - 14 * len(chips)
    cmd_px = 22
    if cmd:
        need = (len(cmd) + 2) * 13.2 + 40
        if need > room:
            cmd_px = max(15, int(22 * (room - 40) / (need - 40)))
        if (len(cmd) + 2) * 13.2 * cmd_px / 22 + 40 > room:
            print(f"warning: command may not fit ({len(cmd)} chars); shorten it", file=sys.stderr)
    prompt = ">" if (cmd or "").startswith("/") else "$"  # slash commands run in the agent, not a shell
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1200px;height:630px;overflow:hidden}}
body{{background:{bg};color:{fg};font-family:'IBM Plex Sans','Inter','Helvetica Neue',Arial,sans-serif;position:relative}}
.grid{{position:absolute;inset:0;background-image:linear-gradient({panel} 1px,transparent 1px),linear-gradient(90deg,{panel} 1px,transparent 1px);background-size:40px 40px;opacity:.9}}
.glow{{position:absolute;right:-180px;top:-180px;width:620px;height:620px;border-radius:50%;background:radial-gradient(circle,{acc}55,transparent 65%)}}
.wrap{{position:absolute;inset:0;padding:64px 72px;display:flex;flex-direction:column}}
.repo{{font-family:'IBM Plex Mono','DejaVu Sans Mono',monospace;font-size:28px;color:{muted}}}
.repo b{{color:{fg};font-weight:600}}
h1{{font-size:76px;line-height:1.02;font-weight:700;letter-spacing:-2px;margin-top:34px;max-width:1000px;text-wrap:balance}}
h1 span{{color:{acc}}}
p{{font-size:30px;line-height:1.3;color:{muted};margin-top:22px;max-width:960px}}
.bottom{{margin-top:auto;display:flex;align-items:center;gap:14px}}
.chip{{font-family:'IBM Plex Mono',monospace;font-size:22px;padding:8px 16px;border:2px solid {muted}55;border-radius:999px;color:{fg}}}
.cmd{{margin-left:auto;font-family:'IBM Plex Mono',monospace;font-size:{cmd_px}px;background:{panel};border:2px solid {acc};border-radius:10px;padding:10px 18px;color:{fg};max-width:{room}px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.cmd i{{color:{acc};font-style:normal}}
</style></head><body><div class="grid"></div><div class="glow"></div><div class="wrap">
<div class="repo">github.com/<b>{e(f['repo'])}</b></div>
<h1>{e(c['headline'])}<span>.</span></h1>
<p>{e(c['subline'])}</p>
<div class="bottom">{''.join(f'<div class="chip">{e(x)}</div>' for x in chips)}
{f'<div class="cmd"><i>{prompt}</i> {e(cmd)}</div>' if cmd else ''}</div>
</div></body></html>"""
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "og.html").write_text(doc)
    ch = chrome()
    if not ch:
        print("No Chrome found: open og.html at 1200x630 and screenshot it.", file=sys.stderr); return
    subprocess.run([ch, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--window-size=1200,630",
                    f"--screenshot={(out/'og.png').resolve()}", f"file://{(out/'og.html').resolve()}"],
                   check=True, capture_output=True, timeout=60)
    print(out / "og.png")

if __name__ == "__main__":
    main()
