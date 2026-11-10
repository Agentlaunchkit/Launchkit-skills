#!/usr/bin/env python3
"""Render a preview image of a draft X thread (does not post).

Usage: render_thread.py thread.md -o out.png [--title "optional label"]
Each post is a card with its weighted character count (same rules as check_thread.py).
Needs Chrome or Chromium on PATH (or set CHROME=/path).
"""
import argparse, html, os, shutil, subprocess, sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_thread

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

def body_height(p):
    body = p[len("REPLY:"):].strip() if p.startswith("REPLY:") else p
    lines = body.count("\n") + 1 + max(0, len(body) // 70)
    return lines * 34

def page(posts, title, html_path):
    cards = []
    n = len(posts)
    for i, p in enumerate(posts, 1):
        is_reply = p.startswith("REPLY:")
        body = p[len("REPLY:"):].strip() if is_reply else p
        w = check_thread.weight(body)
        label = "REPLY" if is_reply else f"{i}/{n}"
        ok = "ok" if w <= 280 else "over"
        text = html.escape(body).replace("\n", "<br>")
        cards.append(f"""<div class="card {'reply' if is_reply else ''}">
  <div class="meta"><span class="num">{html.escape(label)}</span><span class="count {ok}">{w}/280</span></div>
  <div class="body">{text}</div>
</div>""")
    height = 130 + sum(56 + body_height(p) for p in posts)
    height = max(400, min(height, 4000))
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>
{font_css(html_path)}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1200px;background:#0b0b0f;color:#f5f5f7;font-family:'IBM Plex Sans','Helvetica Neue',Arial,sans-serif;-webkit-font-smoothing:antialiased}}
body{{padding:48px 56px 56px}}
.kicker{{font-family:'IBM Plex Mono',monospace;font-size:16px;letter-spacing:.12em;text-transform:uppercase;color:#9a9aa5}}
h1{{font-size:36px;font-weight:700;letter-spacing:-0.03em;margin:10px 0 28px}}
.card{{background:#16161d;border:1px solid #2a2a33;border-radius:16px;padding:22px 26px;margin:0 0 14px}}
.card.reply{{border-color:#3dff8a55}}
.meta{{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;font-family:'IBM Plex Mono',monospace;font-size:16px;color:#9a9aa5}}
.num{{color:#f5f5f7}}
.count.ok{{color:#3dff8a}}
.count.over{{color:#ff4d4d}}
.body{{font-size:24px;line-height:1.45;white-space:normal;word-wrap:break-word}}
</style></head><body>
<div class="kicker">draft · not posted</div>
<h1>{html.escape(title)}</h1>
{''.join(cards)}
</body></html>"""
    return height, doc

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("thread")
    ap.add_argument("-o", "--out", required=True, help="output PNG path")
    ap.add_argument("--facts", help="accepted so the same args as check_thread work")
    ap.add_argument("--title", default="Launch thread preview")
    a = ap.parse_args()
    posts = check_thread.split_posts(open(a.thread).read())
    if not posts:
        sys.exit("thread.md is empty")
    out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    html_path = out.with_suffix(".html")
    height, doc = page(posts, a.title, html_path)
    html_path.write_text(doc)
    ch = chrome()
    if not ch:
        sys.exit("No Chrome found: open the .html next to the PNG path and screenshot it.")
    subprocess.run([
        ch, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
        "--force-device-scale-factor=2", f"--window-size=1200,{height}",
        "--virtual-time-budget=8000", "--run-all-compositor-stages-before-draw",
        f"--screenshot={out.resolve()}", f"file://{html_path.resolve()}",
    ], check=True, capture_output=True, timeout=60)
    print(out)

if __name__ == "__main__":
    main()
