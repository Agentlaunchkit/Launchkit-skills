---
name: og-image
description: Create a 1200x630 Open Graph / social share card (og.png) for a GitHub repo, project, or launch. Use when the user asks for an OG image, social card, link preview image, launch graphic, or "a picture for the tweet/post" about something they built. Facts on the card come from the repo, never invented.
license: MIT
---

# og-image

Make one clean, legible 1200x630 social card for a repo or project, using only verifiable facts.

## When to use
- "Make an OG image / social card / link preview for <repo or project>"
- Before a launch post, Product Hunt listing, or README update that needs a share image

## Steps
1. **Collect facts** (do not guess numbers):
   ```bash
   python3 scripts/repo_facts.py owner/repo -o facts.json
   ```
   For a non-GitHub project, write `facts.json` by hand with at least `repo`, `stars_human` (or remove the star chip), and only facts you can cite.
2. **Read the README** (or `readme_tagline` in facts.json) and decide the ONE promise the project makes. Write `copy.json`:
   ```json
   {"headline": "...", "subline": "...", "command": "...", "accent": "#ff4d4d", "style": "grid", "theme": "dark"}
   ```
   - `headline` ≤ 48 chars: the outcome, in plain words. Not the repo name (it's already shown). No hype words ("revolutionary", "ultimate", "game-changing").
   - `subline` ≤ 110 chars: how it works or who it's for, using the project's own terms.
   - `command`: the real install/usage line from the README (copy it exactly), or omit.
   - `accent`: one brand color if the project has one; otherwise keep the default.
   - `style` (optional): `grid` (default), `terminal` (mono, window chrome, scanlines), or `poster` (editorial type, accent rail).
   - `theme` (optional): `dark` (default) or `light`.
3. **Render**:
   ```bash
   python3 scripts/render_og.py facts.json copy.json -o out/
   ```
   Needs Chrome or Chromium on PATH (or `CHROME=/path`). IBM Plex Sans and Mono are bundled in `fonts/` (SIL OFL 1.1), so the card looks the same on every machine. Without a browser, it still writes `out/og.html`; screenshot it at 1200x630.
4. **Check the PNG before handing it over** (open the image):
   - Text is readable at phone size (~400px wide); nothing is clipped or ellipsized.
   - Every number and name matches facts.json.
   - The headline says what it does, not what it is.
   If anything fails, edit copy.json and re-render. Two passes is normal.
5. Deliver `og.png`, plus the `<meta>` tags if the user has a site:
   ```html
   <meta property="og:image" content="https://<site>/og.png">
   <meta name="twitter:card" content="summary_large_image">
   ```

## Rules
- Facts only from the repo, the README, or the user. Star counts are a snapshot; the card shows the fetch date in facts.json, so tell the user when they were read.
- Don't use the project's logo or trademarks unless the user owns the project or the logo is in the repo for that purpose.
- One message per card. If there are two ideas, make two cards.

## Examples
See `examples/` for real cards made from `anthropics/skills` and `vercel-labs/agent-browser`, each with its facts.json and copy.json. A style comparison (grid, terminal, poster) is in the repo README.
