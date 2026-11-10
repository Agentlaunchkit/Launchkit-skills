---
name: x-launch-thread
description: Draft a short, factual X (Twitter) thread that launches or showcases a GitHub repo or tool, plus a reply carrying the link, then lint it for length, spam patterns and invented numbers. Use when the user asks for a launch thread, a tweet about a repo, "post about this tool", or a Show-and-tell for something they or someone else built. Drafts only; a human posts.
license: MIT
---

# x-launch-thread

Write a thread people finish: one hook, how it works, one concrete detail, how to try it. Every number is sourced. The skill never posts.

## When to use
- "Write a launch thread / tweet for <repo>"
- Turning a new release, a repo you found, or your own project into a post

## Steps
1. **Collect facts**:
   ```bash
   python3 scripts/repo_facts.py owner/repo -o facts.json
   ```
   Then read the README and, if there is one, the latest release notes. Pick:
   - the **hook**: the one thing it lets you do, stated plainly;
   - the **loop**: the 3–5 real commands or steps, copied exactly;
   - one **detail** that shows taste or care (a design decision, a failure it prevents);
   - the **try it** line: the real install command.
2. **Write `thread.md`**: 3–5 posts separated by `---`, then a `REPLY:` post with the link.
   - Post 1 stands alone: repo name, what it does, one fresh fact (release, stars). No "🧵👇", no "A thread:".
   - One idea per post. Code lines on their own lines. Plain words.
   - Opinions are labeled as opinions ("The detail I like"). Never claim personal experience on the user's behalf that they haven't told you about.
   - At most one hashtag in the whole thread; usually zero.
   - The link goes in the REPLY.
   - Write in the account owner's voice (first person if the user posts as themselves).
3. **Lint**:
   ```bash
   python3 scripts/check_thread.py thread.md --facts facts.json
   ```
   Fix every ERROR. For each WARN about a number, confirm it in facts.json or the README, or cut it. Use `--long-posts` only if the user has X Premium and wants long posts.
4. **Deliver** the thread as text with each post's character count, the fetch time of the facts (star counts go stale), and any image to attach (pair with the `og-image` skill).

## Rules (X automation and spam rules plus basic honesty)
- **Draft only.** Do not post, schedule, reply to strangers, or DM through any tool unless the user explicitly asks for that exact post.
- No engagement bait ("RT if", "follow for more"), no trend-hijacking, and no tagging big accounts to farm reach.
- Don't post near-duplicate threads across accounts or days. Each one needs a new angle.
- If it's someone else's project, credit them by handle or link and don't imply you built it.
- Numbers come from facts.json or the README, with the date they were read.

## Examples
`examples/` has real drafts for `anthropics/skills` and `vercel-labs/agent-browser`, each with facts.json, thread.md and the lint report.
