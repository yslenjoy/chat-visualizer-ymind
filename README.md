# chat-visualizer-ymind

An OpenClaw skill that turns AI chat conversations into structured thinking maps.

## What it does

Paste any AI conversation → get a visual thinking graph with:
- **Reasoning nodes** (facts, frictions, sparks, actions)
- **Thinking shift detection** — where did the conversation turn?
- **Action items** — extracted and prioritized
- **Structured summary** — no more scrolling through long chats

## Install

```bash
clawhub install chat-visualizer-ymind
```

Or from GitHub:

```bash
openclaw skills install github:yslenjoy/chat-visualizer-ymind
```

## Usage

Paste a conversation or share a URL:

```
Visualize this: https://chatgpt.com/share/xxx
```

```
Visualize this conversation:
User: I'm thinking about switching careers...
Assistant: That's a big decision...
```

The skill outputs:
1. **JSON graph** — machine-readable, follows `references/graph-schema.md`
2. **HTML visualization** — D3.js force graph, saved for long-term viewing
3. **Markdown summary** — reasoning timeline + action items

## Technical Pipeline

```
URL / plain text
  │
  ├─ [URL] scripts/fetch-chat.py      fetch share link → messages JSON
  │                                   supports: ChatGPT (JSON API)
  │                                             Gemini  (Playwright)
  │                                             Claude  (Playwright, headed)
  │
  ├─ [LLM] SKILL.md prompt            analyze messages → graph JSON
  │                                   extracts: nodes, edges, reasoning shifts, actions
  │
  ├─ [save] workspace/ymind/<run_id>/ persist raw_chat.json + graph.json
  │
  └─ [script] render-html.py          graph JSON → HTML visualization  (TODO)
               templates/mindmap.html D3.js force graph template        (TODO)
```

**Dependencies** (Python, conda env `ymind`):
- `requests` — ChatGPT fetching
- `playwright` — Gemini / Claude fetching (`playwright install chromium`)

## Part of YMind

This is one skill in the YMind plugin family:

| Skill | Status | Description |
|-------|--------|-------------|
| `chat-visualizer-ymind` | v0.1 | Single conversation visualization |
| `session-analysis-ymind` | planned | Cross-session pattern discovery |
| `capture-idea-ymind` | planned | Quick idea/inspiration capture |

## License

MIT
