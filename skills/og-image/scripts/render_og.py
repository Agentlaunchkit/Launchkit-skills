#!/usr/bin/env python3
"""Render a 1200x630 Open Graph / social card from repo facts + copy.

Usage: render_og.py facts.json copy.json -o out_dir
copy.json keys:
  headline  (required, <= 48 chars)   the one promise of the project
  subline   (required, <= 110 chars)  how it works / who it's for
  command   (optional)                one install or usage line shown in a terminal strip
  accent    (optional hex, default #ff4d4d)
  theme     (optional: "dark" | "light", default dark)
  style     (optional: "grid" | "terminal" | "poster", default grid)
Writes og.html and og.png (needs Chrome/Chromium on PATH, or set CHROME=/path).
Fonts are bundled (IBM Plex Sans + Mono, SIL OFL 1.1) so the card looks the same on every machine.
"""

import argparse, html, json, os, re, shutil, subprocess, sys, pathlib

STYLES = ("grid", "terminal", "poster")

def chrome():
    for c in [os.environ.get("CHROME"), "google-chrome", "chromium", "chromium-browser", "chrome",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]:
        if c and (shutil.which(c) or os.path.exists(c)):
            return shutil.which(c) or c
    return None

def font_css(html_path=None):
    """@font-face rules. Paths are relative to html_path so the HTML stays portable."""
    root = pathlib.Path(__file__).resolve().parent.parent / "fonts"
    base = pathlib.Path(html_path).resolve().parent if html_path else root
    faces = [
        ("IBM Plex Sans", 400, "IBMPlexSans-Regular.woff2"),
        ("IBM Plex Sans", 600, "IBMPlexSans-SemiBold.woff2"),
        ("IBM Plex Sans", 700, "IBMPlexSans-Bold.woff2"),
        ("IBM Plex Mono", 400, "IBMPlexMono-Regular.woff2"),
    ]
    rules = []
    for fam, weight, name in faces:
        path = root / name
        if path.exists():
            rel = pathlib.Path(os.path.relpath(path, base)).as_posix()
            rules.append(
                f"@font-face{{font-family:'{fam}';src:url('{rel}') format('woff2');"
                f"font-weight:{weight};font-style:normal;font-display:block}}"
            )
    return "\n".join(rules)

def accent_of(c, default="#ff4d4d"):
    a = (c.get("accent") or default).strip()
    return a if re.fullmatch(r"#[0-9A-Fa-f]{3,8}", a) else default

def style_of(c, default="grid"):
    s = (c.get("style") or default).strip().lower()
    if s not in STYLES:
        print(f"warning: unknown style {s!r}; using {default}", file=sys.stderr)
        return default
    return s

def screenshot(ch, html_path, png_path, w, h, scale=1):
    subprocess.run([
        ch, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
        f"--force-device-scale-factor={scale}", f"--window-size={w},{h}",
        "--virtual-time-budget=8000", "--run-all-compositor-stages-before-draw",
        f"--screenshot={png_path.resolve()}", f"file://{html_path.resolve()}",
    ], check=True, capture_output=True, timeout=60)


def colors(dark):
    if dark:
        return dict(bg="#0b0b0f", fg="#f5f5f7", muted="#9a9aa5", panel="#16161d", hair="#1c1c24")
    return dict(bg="#fafafa", fg="#0b0b0f", muted="#5b5b66", panel="#ececf0", hair="#e2e2e8")

def page_grid(f, c, pal, acc, cmd, cmd_px, room, chips, prompt, html_path):
    e = html.escape
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{font_css(html_path)}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1200px;height:630px;overflow:hidden}}
body{{background:{pal['bg']};color:{pal['fg']};font-family:'IBM Plex Sans','Helvetica Neue',Arial,sans-serif;position:relative;-webkit-font-smoothing:antialiased}}
.grid{{position:absolute;inset:0;background-image:linear-gradient({pal['panel']} 1px,transparent 1px),linear-gradient(90deg,{pal['panel']} 1px,transparent 1px);background-size:40px 40px;opacity:.9}}
.glow{{position:absolute;right:-180px;top:-180px;width:620px;height:620px;border-radius:50%;background:radial-gradient(circle,{acc}55,transparent 65%)}}
.wrap{{position:absolute;inset:0;padding:64px 72px;display:flex;flex-direction:column}}
.repo{{font-family:'IBM Plex Mono','DejaVu Sans Mono',monospace;font-size:26px;color:{pal['muted']}}}
.repo b{{color:{pal['fg']};font-weight:600}}
h1{{font-size:74px;line-height:1.04;font-weight:700;letter-spacing:-0.03em;margin-top:34px;max-width:1000px;text-wrap:balance}}
h1 span{{color:{acc}}}
p{{font-size:28px;line-height:1.35;color:{pal['muted']};margin-top:22px;max-width:960px}}
.bottom{{margin-top:auto;display:flex;align-items:center;gap:14px}}
.chip{{font-family:'IBM Plex Mono',monospace;font-size:20px;padding:8px 16px;border:2px solid {pal['muted']}55;border-radius:999px;color:{pal['fg']}}}
.cmd{{margin-left:auto;font-family:'IBM Plex Mono',monospace;font-size:{cmd_px}px;background:{pal['panel']};border:2px solid {acc};border-radius:10px;padding:10px 18px;color:{pal['fg']};max-width:{room}px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.cmd i{{color:{acc};font-style:normal}}
</style></head><body><div class="grid"></div><div class="glow"></div><div class="wrap">
<div class="repo">github.com/<b>{e(f['repo'])}</b></div>
<h1>{e(c['headline'])}<span>.</span></h1>
<p>{e(c['subline'])}</p>
<div class="bottom">{''.join(f'<div class="chip">{e(x)}</div>' for x in chips)}
{f'<div class="cmd"><i>{prompt}</i> {e(cmd)}</div>' if cmd else ''}</div>
</div></body></html>"""

def page_terminal(f, c, pal, acc, cmd, chips, prompt, html_path):
    e = html.escape
    # Slightly smaller headline: mono is wider.
    hpx = 52 if len(c['headline']) > 36 else 58
    scan = "rgba(255,255,255,.04)" if pal['bg'] < "#888" else "rgba(0,0,0,.05)"
    meta = "  ·  ".join(chips)
    body_cmd = cmd or ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{font_css(html_path)}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1200px;height:630px;overflow:hidden}}
body{{background:{pal['bg']};color:{pal['fg']};font-family:'IBM Plex Mono','DejaVu Sans Mono',monospace;position:relative;-webkit-font-smoothing:antialiased}}
.scan{{position:absolute;inset:0;background:repeating-linear-gradient({scan} 0 2px,transparent 2px 4px);pointer-events:none;z-index:2}}
.frame{{position:absolute;inset:36px;border:2px solid {acc};border-radius:16px;background:{pal['panel']};display:flex;flex-direction:column;overflow:hidden;box-shadow:0 0 0 1px {pal['hair']},0 20px 80px {acc}22}}
.title{{display:flex;align-items:center;gap:10px;padding:16px 22px;border-bottom:1px solid {pal['hair']};font-size:20px;color:{pal['muted']}}}
.dot{{width:12px;height:12px;border-radius:50%;background:{acc};opacity:.85}}
.dot:nth-child(2){{opacity:.55}}.dot:nth-child(3){{opacity:.3}}
.title b{{color:{pal['fg']};font-weight:400;margin-left:8px}}
.body{{padding:36px 44px 28px;display:flex;flex-direction:column;flex:1}}
.k{{color:{acc};margin-bottom:16px;font-size:20px}}
h1{{font-size:{hpx}px;line-height:1.2;font-weight:400;letter-spacing:-0.02em;max-width:1000px;text-wrap:balance;color:{pal['fg']}}}
p{{font-size:24px;line-height:1.4;color:{pal['muted']};margin-top:20px;max-width:980px}}
.meta{{margin-top:auto;padding-top:28px;font-size:20px;color:{pal['muted']}}}
.cmd{{margin-top:14px;font-size:22px;color:{pal['fg']}}}
.cmd i{{color:{acc};font-style:normal}}
.cursor{{display:inline-block;width:12px;height:22px;background:{acc};margin-left:6px;vertical-align:text-bottom;opacity:.9}}
</style></head><body><div class="frame">
<div class="title"><span class="dot"></span><span class="dot"></span><span class="dot"></span><b>{e(f['repo'])}</b></div>
<div class="body">
<div class="k">{prompt} cat LAUNCH.txt</div>
<h1>{e(c['headline'])}</h1>
<p>{e(c['subline'])}</p>
<div class="meta">{e(meta)}</div>
{f'<div class="cmd"><i>{prompt}</i> {e(body_cmd)}<span class="cursor"></span></div>' if body_cmd else ''}
</div></div><div class="scan"></div></body></html>"""

def page_poster(f, c, pal, acc, cmd, chips, prompt, html_path):
    e = html.escape
    meta = "  ·  ".join(chips)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{font_css(html_path)}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1200px;height:630px;overflow:hidden}}
body{{background:{pal['bg']};color:{pal['fg']};font-family:'IBM Plex Sans','Helvetica Neue',Arial,sans-serif;position:relative;-webkit-font-smoothing:antialiased}}
.rail{{position:absolute;left:0;top:0;bottom:0;width:28px;background:{acc}}}
.wrap{{position:absolute;inset:0 0 0 28px;padding:56px 72px 48px;display:flex;flex-direction:column}}
.top{{display:flex;align-items:baseline;justify-content:space-between;gap:24px}}
.repo{{font-family:'IBM Plex Mono',monospace;font-size:22px;color:{pal['muted']};letter-spacing:.04em;text-transform:uppercase}}
.repo b{{color:{pal['fg']};font-weight:600}}
.meta{{font-family:'IBM Plex Mono',monospace;font-size:18px;color:{pal['muted']};white-space:nowrap}}
h1{{font-size:80px;line-height:0.98;font-weight:700;letter-spacing:-0.04em;margin-top:48px;max-width:1040px;text-wrap:balance}}
.rule{{width:120px;height:6px;background:{acc};margin:32px 0 0}}
p{{font-size:28px;line-height:1.35;color:{pal['muted']};margin-top:28px;max-width:900px}}
.cmd{{margin-top:auto;font-family:'IBM Plex Mono',monospace;font-size:24px;color:{pal['fg']}}}
.cmd i{{color:{acc};font-style:normal}}
</style></head><body><div class="rail"></div><div class="wrap">
<div class="top"><div class="repo">github.com/<b>{e(f['repo'])}</b></div><div class="meta">{e(meta)}</div></div>
<h1>{e(c['headline'])}</h1>
<div class="rule"></div>
<p>{e(c['subline'])}</p>
{f'<div class="cmd"><i>{prompt}</i> {e(cmd)}</div>' if cmd else ''}
</div></body></html>"""

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
    pal = colors(dark)
    acc = accent_of(c)
    style = style_of(c, "grid")
    chips = [f"★ {f['stars_human']}"]
    if f.get("language"): chips.append(f["language"])
    if f.get("license"): chips.append(f["license"])
    if f.get("latest_release"): chips.append(f["latest_release"])
    cmd = c.get("command")
    room = 1056 - sum(len(x) * 13 + 50 for x in chips) - 14 * len(chips)
    cmd_px = 22
    if cmd:
        need = (len(cmd) + 2) * 13.2 + 40
        if need > room:
            cmd_px = max(15, int(22 * (room - 40) / (need - 40)))
        if (len(cmd) + 2) * 13.2 * cmd_px / 22 + 40 > room:
            print(f"warning: command may not fit ({len(cmd)} chars); shorten it", file=sys.stderr)
    prompt = ">" if (cmd or "").startswith("/") else "$"
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if style == "terminal":
        doc = page_terminal(f, c, pal, acc, cmd, chips, prompt, out / 'og.html')
    elif style == "poster":
        doc = page_poster(f, c, pal, acc, cmd, chips, prompt, out / 'og.html')
    else:
        doc = page_grid(f, c, pal, acc, cmd, cmd_px, room, chips, prompt, out / 'og.html')
    (out / "og.html").write_text(doc)
    ch = chrome()
    if not ch:
        print("No Chrome found: open og.html at 1200x630 and screenshot it.", file=sys.stderr); return
    screenshot(ch, out / "og.html", out / "og.png", 1200, 630)
    print(out / "og.png")

if __name__ == "__main__":
    main()
