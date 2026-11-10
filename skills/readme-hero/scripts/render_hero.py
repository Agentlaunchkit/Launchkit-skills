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
  style      (optional: "bar" | "terminal" | "poster", default bar)
Writes hero-dark.png, hero-light.png, hero-dark.html, hero-light.html and HERO.md.
Fonts are bundled (IBM Plex Sans + Mono, SIL OFL 1.1) so the banner looks the same on every machine.
"""
import argparse, html, json, os, re, shutil, subprocess, sys, pathlib, urllib.parse

STYLES = ("bar", "terminal", "poster")

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

def style_of(c, default="bar"):
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

def palettes(dark):
    if dark:
        return dict(bg="#0b0b0f", fg="#f5f5f7", muted="#a0a0ab", line="#1c1c24")
    return dict(bg="#ffffff", fg="#0b0b0f", muted="#55555f", line="#ececf1")

def page(f, c, dark, style, html_path):
    pal = palettes(dark); acc = accent_of(c); e = html.escape
    if style == "terminal":
        scan = "rgba(255,255,255,.04)" if dark else "rgba(0,0,0,.05)"
        hpx = 48 if len(c['headline']) > 40 else 54
        return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{font_css(html_path)}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1280px;height:400px;overflow:hidden}}
body{{background:{pal['bg']};color:{pal['fg']};font-family:'IBM Plex Mono','DejaVu Sans Mono',monospace;position:relative;-webkit-font-smoothing:antialiased}}
.scan{{position:absolute;inset:0;background:repeating-linear-gradient({scan} 0 2px,transparent 2px 4px);pointer-events:none}}
.frame{{position:absolute;inset:28px;border:2px solid {acc};border-radius:14px;display:flex;flex-direction:column;background:{pal['bg']}}}
.title{{display:flex;align-items:center;gap:8px;padding:12px 22px;border-bottom:1px solid {pal['line']};font-size:18px;color:{pal['muted']}}}
.dot{{width:10px;height:10px;border-radius:50%;background:{acc}}}
.title b{{color:{acc};font-weight:400}}
.wrap{{padding:28px 40px 24px;display:flex;flex-direction:column;justify-content:center;flex:1}}
h1{{font-size:{hpx}px;line-height:1.15;font-weight:400;letter-spacing:-0.02em;max-width:1100px;text-wrap:balance}}
p{{font-size:22px;line-height:1.4;color:{pal['muted']};margin-top:14px;max-width:1000px}}
</style></head><body><div class="frame">
<div class="title"><span class="dot"></span><span class="dot"></span><span class="dot"></span>&nbsp;{e(f['owner'])}/<b>{e(f['name'])}</b></div>
<div class="wrap"><h1>{e(c['headline'])}</h1><p>{e(c['subline'])}</p></div>
</div><div class="scan"></div></body></html>"""
    if style == "poster":
        return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{font_css(html_path)}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1280px;height:400px;overflow:hidden}}
body{{background:{pal['bg']};color:{pal['fg']};font-family:'IBM Plex Sans','Helvetica Neue',Arial,sans-serif;position:relative;-webkit-font-smoothing:antialiased}}
.rail{{position:absolute;left:0;top:0;bottom:0;width:22px;background:{acc}}}
.wrap{{position:absolute;inset:0 0 0 22px;padding:56px 72px;display:flex;flex-direction:column;justify-content:center}}
.repo{{font-family:'IBM Plex Mono',monospace;font-size:20px;color:{pal['muted']};letter-spacing:.06em;text-transform:uppercase}}
.repo b{{color:{pal['fg']};font-weight:600}}
h1{{font-size:66px;line-height:1.02;font-weight:700;letter-spacing:-0.035em;margin-top:16px;max-width:1100px;text-wrap:balance}}
.rule{{width:88px;height:5px;background:{acc};margin:18px 0 0}}
p{{font-size:24px;line-height:1.35;color:{pal['muted']};margin-top:16px;max-width:960px}}
</style></head><body><div class="rail"></div><div class="wrap">
<div class="repo">{e(f['owner'])}/<b>{e(f['name'])}</b></div>
<h1>{e(c['headline'])}</h1><div class="rule"></div><p>{e(c['subline'])}</p>
</div></body></html>"""
    # default: bar
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{font_css(html_path)}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1280px;height:400px;overflow:hidden}}
body{{background:{pal['bg']};color:{pal['fg']};font-family:'IBM Plex Sans','Helvetica Neue',Arial,sans-serif;position:relative;-webkit-font-smoothing:antialiased}}
.bar{{position:absolute;left:0;top:0;bottom:0;width:10px;background:{acc}}}
.dots{{position:absolute;right:0;top:0;bottom:0;width:420px;background-image:radial-gradient({pal['line']} 2px,transparent 2px);background-size:22px 22px;-webkit-mask-image:linear-gradient(90deg,transparent,#000 60%)}}
.wrap{{position:absolute;inset:0;padding:56px 80px;display:flex;flex-direction:column;justify-content:center}}
.repo{{font-family:'IBM Plex Mono',monospace;font-size:22px;color:{pal['muted']}}}
.repo b{{color:{acc};font-weight:600}}
h1{{font-size:64px;line-height:1.05;font-weight:700;letter-spacing:-0.03em;margin-top:16px;max-width:1000px;text-wrap:balance}}
p{{font-size:26px;line-height:1.35;color:{pal['muted']};margin-top:16px;max-width:940px}}
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
    style = style_of(c, "bar")
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    ch = chrome()
    for mode in ("dark", "light"):
        h = out / f"hero-{mode}.html"; h.write_text(page(f, c, mode == "dark", style, h))
        if ch:
            screenshot(ch, h, out / f"hero-{mode}.png", 1280, 400, scale=2)
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
