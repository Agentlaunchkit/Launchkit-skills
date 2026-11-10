anthropics/skills is at 192k stars as of Nov 10, and the core idea is almost boring:

a skill is a folder with a SKILL.md. Name and description up top, instructions below. The agent loads it only when a task matches.
---
What's in the repo:

• docx, pdf, pptx, xlsx: the skills behind Claude's document features
• creative: algorithmic-art, canvas-design, slack-gif-creator
• dev: mcp-builder, webapp-testing, frontend-design
• skill-creator, which helps you write new ones
---
Try it in Claude Code:

/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills

Then just ask: "use the PDF skill to pull the form fields from this file."
---
The part I like: the format is published as an open standard (agentskills.io), so a skill is a plain folder you can read, edit and version, not a black box.
---
REPLY: Repo: https://github.com/anthropics/skills
