---
name: readme-hero
description: Write the top of a GitHub README (hero banner image in dark and light versions, one-line promise, honest badges, quick start, three reasons) so a visitor understands the project in five seconds. Use when the user asks to improve, rewrite, or "make pretty" a README header, add a README banner, or prep a repo for launch.
license: MIT
---

# readme-hero

Turn the first screen of a README into a clear pitch: what it does, how to start, why it's worth it. Use only facts the repo already states.

## When to use
- "Make my README look good / add a banner / rewrite the intro"
- Before a launch, a Show HN, or a skills.sh listing

## Steps
1. **Collect facts**:
   ```bash
   python3 scripts/repo_facts.py owner/repo -o facts.json
   ```
   Then read the full README yourself. You need the install line, the core loop, and the one thing it does better than doing it by hand.
2. **Write `copy.json`**:
   ```json
   {
     "headline": "≤56 chars: the outcome for the reader",
     "subline": "≤120 chars: how it works, in the project's own words",
     "why": ["3 concrete reasons, ≤90 chars each, each traceable to the README"],
     "quickstart": ["exact lines copied from the README"],
     "accent": "#hex", "npm": "package-name-if-any", "docs_url": "https://...",
     "style": "bar"
   }
   ```
   - Lead with the reader's outcome ("A browser your agent drives from the shell"), not the category ("A Rust CLI").
   - `why` items must be checkable: a feature, a number, a supported platform. No "blazing fast" unless the README benchmarks it.
   - Quick start is copied verbatim. Never invent flags.
   - `style` (optional): `bar` (default, accent stripe + dots), `terminal` (mono, window chrome), or `poster` (editorial type, accent rail).
3. **Render**:
   ```bash
   python3 scripts/render_hero.py facts.json copy.json -o out/
   ```
   This produces `hero-dark.png` and `hero-light.png` (2560x800) plus `HERO.md`, a paste-ready header that swaps the banner with the reader's GitHub theme. IBM Plex Sans and Mono are bundled in `fonts/` (SIL OFL 1.1), so the banners look the same on every machine.
4. **Check**: open both PNGs. The headline must be readable at 50% width and nothing may be clipped. Then compare HERO.md against the README line by line: every claim must exist there.
5. **Deliver** HERO.md with the two PNGs. Tell the user to put the PNGs in the repo (e.g. `.github/hero-dark.png`) and fix the `srcset`/`src` paths. Don't commit or push unless the user asked.

## Rules
- Badges come only from live sources (shields.io reading GitHub/npm). No fake "downloads" or "build passing" badges.
- Keep the project's existing license and attribution lines; this skill replaces the header, not the legal text.
- If the repo isn't the user's, label the output as a suggestion (e.g., for a PR), not a replacement.

## Examples
`examples/` has real runs for `anthropics/skills` and `vercel-labs/agent-browser`: facts.json, copy.json, both PNGs, and HERO.md.
