vercel-labs/agent-browser shipped v0.42.0 on Nov 10 (49k stars).

It gives an AI agent a real browser it drives one shell command at a time.
---
The loop:

agent-browser open example.com
agent-browser snapshot -i   → elements as refs like @e1
agent-browser click @e1
agent-browser get url       → check it worked

The browser stays open between commands, so each step is one short call.
---
The detail I like: a click fails instead of reporting success when the target is hidden, disabled, off-screen or covered by something like a consent banner.

That one rule removes a whole class of silent failures.
---
Also in the box: native Rust binaries for macOS, Linux and Windows, version-matched skills (agent-browser skills get core), and an MCP server (agent-browser mcp).

npm install -g agent-browser
---
REPLY: Repo: https://github.com/vercel-labs/agent-browser
Docs: https://agent-browser.dev
