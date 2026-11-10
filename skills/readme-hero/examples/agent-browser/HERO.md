<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./hero-dark.png">
    <img alt="agent-browser: A browser your agent drives from the shell" src="./hero-light.png" width="100%">
  </picture>
</p>

<p align="center"><b>A browser your agent drives from the shell</b><br>Snapshot the page as an accessibility tree, act on a ref like @e1, read again to check. One short command per step.</p>

<p align="center">

[![GitHub stars](https://img.shields.io/github/stars/vercel-labs/agent-browser?style=flat-square)](https://github.com/vercel-labs/agent-browser/stargazers) [![Release](https://img.shields.io/github/v/release/vercel-labs/agent-browser?style=flat-square)](https://github.com/vercel-labs/agent-browser/releases) [![npm](https://img.shields.io/npm/v/agent-browser?style=flat-square)](https://www.npmjs.com/package/agent-browser) [![License](https://img.shields.io/github/license/vercel-labs/agent-browser?style=flat-square)](https://github.com/vercel-labs/agent-browser/blob/HEAD/LICENSE)

</p>

## Quick start

```bash
npm install -g agent-browser
agent-browser install
agent-browser open example.com
agent-browser snapshot -i
```

## Why

- Native Rust CLI with binaries for macOS, Linux (glibc + musl) and Windows
- Clicks fail loudly when the target is hidden, disabled or covered
- Ships version-matched skills (agent-browser skills get core) plus an MCP server

[Docs](https://agent-browser.dev)
