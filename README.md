# chat-visualizer-ymind

An OpenClaw skill that turns AI chat conversations into structured thinking maps.

## What it does

Share an AI conversation URL → get a visual thinking graph with:
- **Reasoning nodes** (facts, frictions, sparks, actions)
- **Thinking shift detection** — where did the conversation turn?
- **Action items** — extracted and prioritized
- **HTML visualization** — D3.js force graph, shareable single file

## Install

This skill is **not published on ClawHub yet**.
So `clawhub install chat-visualizer-ymind` is not available right now.

### Manual Install

#### OpenClaw

```bash
git clone https://github.com/yslenjoy/chat-visualizer-ymind.git ~/.openclaw/skills/chat-visualizer-ymind
```

#### Claude Code

```bash
git clone https://github.com/yslenjoy/chat-visualizer-ymind.git ~/.claude/skills/chat-visualizer-ymind
```

#### Codex

```bash
git clone https://github.com/yslenjoy/chat-visualizer-ymind.git ~/.codex/skills/chat-visualizer-ymind
```

## Usage

Share a URL:

```
Visualize this: https://chatgpt.com/share/xxx
```

Supported providers: ChatGPT, Gemini, Claude, Deepseek.

## Output

Results are saved to `~/ymind-ws/` by default (override with `YMIND_DIR`). All runs share this folder — it's your personal thinking map library.

```
~/ymind-ws/
  index.json                    ← all runs, auto-updated after each render
  20260319-143021_chatgpt/
    raw_chat.json               ← fetched conversation
    graph.json                  ← extracted thinking graph
    graph.html                  ← D3.js visualization
    graph.png                   ← screenshot
    meta.json                   ← provider, url, title, created_at
```

## Pipeline

```
Share URL
  │
  ├─ scripts/run.sh fetch    → fetch-chat.py → raw_chat.json
  ├─ [LLM] SKILL.md          → analyze → graph.json
  └─ scripts/run.sh render   → render-html.py → graph.html + graph.png
```

## Dependencies

Requires Python 3.10+.

**Minimal** (paste text only — no extra install needed):
`render-html.py` uses stdlib only; the paste path skips `fetch-chat.py` entirely.

**Full** (auto-fetch URLs + screenshot):
```bash
pip install requests playwright && playwright install chromium
```


## License

MIT
