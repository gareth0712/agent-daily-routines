# Proposal A — The Pragmatist Builder

## 1. Recommended Approach

Save output as a `.md` file in a GitHub-synced folder, then access it anywhere via GitHub mobile or any browser.

## 2. How It Works

**One command from Claude Code CLI:**

```bash
# Pipe or redirect any Claude output directly
claude -p "your prompt here" > S:/git/13-claude-output/$(date +%Y%m%d-%H%M%S).md

# Or after the fact, save last output
echo "$LAST_OUTPUT" > S:/git/13-claude-output/output-$(date +%Y%m%d).md && git -C S:/git/13-claude-output add . && git -C S:/git/13-claude-output commit -m "output" && git -C S:/git/13-claude-output push
```

Gary already has `S:\git\13-claude-output` — use it. Push to GitHub, then on mobile open GitHub app → repo → file → raw, or copy the raw URL to paste anywhere.

**Alternative (zero git):** Use `gh gist create output.md --public` — returns a URL instantly, open on mobile.

## 3. Tradeoffs / Limitations

| Pro | Con |
|-----|-----|
| Zero new tooling — git already installed | Requires push step (can alias to one command) |
| Works on iOS via GitHub app or browser | Viewing raw markdown on GitHub mobile is decent but not pretty |
| `gh gist` variant is truly one command | Gists are public unless you pay for private |
| `13-claude-output` dir already exists in Gary's workspace | Long outputs still need a terminal command to capture |

**Verdict:** `gh gist create` wins for one-shot sharing. Git repo wins for persistent history.
