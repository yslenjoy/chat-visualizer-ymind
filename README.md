# chat-visualizer-ymind

An OpenClaw skill that turns AI chat conversations into structured thinking maps.

## What it does

Share an AI conversation URL → get a visual thinking graph with:
- **Reasoning nodes** (facts, frictions, sparks, actions)
- **Thinking shift detection** — where did the conversation turn?
- **Action items** — extracted and prioritized
- **HTML visualization** — D3.js force graph, shareable single file

## Install

```bash
clawhub install chat-visualizer-ymind
```

Or from GitHub:

```bash
openclaw skills install github:yslenjoy/chat-visualizer-ymind
```

## Usage

Share a URL:

```
Visualize this: https://chatgpt.com/share/xxx
```

Supported providers: ChatGPT, Gemini, Claude.

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

```bash
pip install -r requirements.txt
playwright install chromium
```

<!-- TODO: 发布前需要解决 Python 环境方案（当前开发用 conda env ymind，用户侧需要替换为 venv 或纯 pip） -->


## License

MIT
