<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/hero-dark.png">
    <img alt="launchkit-skills: Launch assets for whatever your agent just built" src="./assets/hero-light.png" width="100%">
  </picture>
</p>

<p align="center"><b>Launch assets for whatever your agent just built.</b><br>Agent skills that turn a repo into a social card, a README header and an X thread, using only facts from the repo.</p>

## Skills

| Skill | What it makes | Styles | Example |
|---|---|---|---|
| [`og-image`](skills/og-image/SKILL.md) | A 1200×630 social / link-preview card (`og.png`) | `grid`, `terminal`, `poster` | [agent-browser](skills/og-image/examples/agent-browser/og.png) · [anthropics/skills](skills/og-image/examples/anthropics-skills/og.png) |
| [`readme-hero`](skills/readme-hero/SKILL.md) | Dark + light README banners and a paste-ready header (`HERO.md`) | `bar`, `terminal`, `poster` | [agent-browser](skills/readme-hero/examples/agent-browser/HERO.md) · [anthropics/skills](skills/readme-hero/examples/anthropics-skills/HERO.md) |
| [`x-launch-thread`](skills/x-launch-thread/SKILL.md) | A 3–5 post X thread plus a link reply, linted for X's weighted length, spam patterns and invented numbers | — | [agent-browser](skills/x-launch-thread/examples/agent-browser/thread.md) · [anthropics/skills](skills/x-launch-thread/examples/anthropics-skills/thread.md) |

Every example was made by running the skill on a real public repo (`vercel-labs/agent-browser`, `anthropics/skills`). Facts were read from the GitHub API on Nov 10, 2026; star counts go stale.

## Demos

**og-image** — three styles (`grid`, `terminal`, `poster`) from the same `vercel-labs/agent-browser` facts:

![og-image styles: grid, terminal, poster](assets/demos/og-image.gif)

Still of all three: [og-image.png](assets/demos/og-image.png).

**readme-hero** — three styles (`bar`, `terminal`, `poster`), dark theme:

![readme-hero styles: bar, terminal, poster](assets/demos/readme-hero.png)

**x-launch-thread** — a draft-only preview of the linted thread (this skill never posts):

![x-launch-thread preview for vercel-labs/agent-browser](assets/demos/x-launch-thread.png)

## Install

Each skill is a folder with a `SKILL.md` ([Agent Skills format](https://agentskills.io)), so any agent that reads skills can use it.

**skills.sh (Claude Code, Codex, Cursor and others):**
```bash
npx skills add Agentlaunchkit/Launchkit-skills
```

**Claude Code plugin marketplace:**
```
/plugin marketplace add Agentlaunchkit/Launchkit-skills
/plugin install launchkit@launchkit-skills
```

**Manual:** copy `skills/<name>/` into your agent's skills folder (e.g. `~/.claude/skills/`, `.codex/skills/`, `.cursor/skills/`).

Then ask your agent: *"Make an OG image for vercel-labs/agent-browser"* or *"Draft a launch thread for this repo."*

## Requirements

- Python 3.8+ (standard library only)
- Chrome or Chromium on `PATH` for PNG rendering (or set `CHROME=/path/to/chrome`). Without it, the skills still write HTML you can screenshot.
- Network access to `api.github.com`. Set `GITHUB_TOKEN` to raise the rate limit (optional).

IBM Plex Sans and IBM Plex Mono are bundled in each visual skill's `fonts/` folder so cards look the same on every machine.

## Principles

- **Facts, not vibes.** Numbers come from the repo, with the date they were read. `x-launch-thread` flags any number it can't find in the facts, and uses calendar dates (`Nov 10, 2026`) instead of "last night."
- **Drafts only.** Nothing is posted, pushed or committed unless you ask.
- **No spam patterns.** No engagement bait, hashtag stacks or tag-farming.
- **Honest length.** The thread linter counts the way X does: each URL is 23 characters, each emoji cluster is 2, CJK is 2, limit 280.

## License

MIT. Example outputs describe third-party projects (Apache-2.0 `vercel-labs/agent-browser`, `anthropics/skills`) and contain no code from them; names and trademarks belong to their owners.

The bundled IBM Plex Sans and IBM Plex Mono fonts are Copyright © 2017 IBM Corp. with Reserved Font Name "Plex", licensed under the [SIL Open Font License 1.1](skills/og-image/fonts/LICENSE.txt).
