---
name: chat-visualizer-ymind
description: Turn AI chat transcripts into structured YMind thinking maps with reasoning nodes, thinking shifts, and action items — rendered as an interactive D3.js force graph. Use this skill whenever a user shares a ChatGPT, Gemini, or Claude conversation URL and wants to visualize, analyze, or extract insights from it — even if they just say "help me understand this chat", "what was decided here", or "summarize the key takeaways" without explicitly asking for a graph or visualization.
---

# Chat Visualizer - YMind

## Input

The user provides a share URL (ChatGPT / Gemini / Claude). Run fetch to get messages:

```bash
conda run -n ymind bash scripts/run.sh fetch "<url>"
# prints RUN_DIR — read <run_dir>/raw_chat.json, use items[0].messages
```

ChatGPT 403: script auto-retries with Playwright (no cookies saved). If still blocked, ask the user to open the URL in a logged-in browser and copy the conversation text.

## Extract Graph

Read `references/graph-schema.md` for node types, edge types, label rules, and output schema.

Critical rules (non-obvious):
- `turn_id`: assign actual turn number (1-based). Never default all nodes to the same value — this drives horizontal spread in the D3 visualization.
- Extraction volume: 2-5 nodes per turn, judged by **AI response substance**, not user message length. A 2-character "继续" can still produce a rich AI response worth extracting.
- Edges: only add if the connection passes the "obviously yes" test.
- Reasoning shifts: look for moments where thinking fundamentally changed. Capture what changed, from what, to what, and why.
- Chinese strings: use `「」` not curly quotes `""` inside JSON values — curly quotes break JSON parsing.

## Output

1. Write `<run_dir>/graph.json`
2. Render:

```bash
conda run -n ymind bash scripts/run.sh render <run_dir>
# validates JSON, renders graph.html + graph.png screenshot
```

3. Output Markdown summary (format in `references/graph-schema.md`).

Run dir files: `raw_chat.json`, `graph.json`, `graph.html`, `graph.png`, `meta.json`.

## Language Rule

All output (labels, summaries, analysis) must match the conversation language.

## Setup

```bash
# TODO: env strategy TBD for distribution — currently requires conda env ymind
conda run -n ymind pip install -r requirements.txt
conda run -n ymind playwright install chromium
```

## Notes

- Long conversations (20+ turns): focus on most significant nodes, skip low-substance turns.
- Multiple topics: group nodes by topic.
- **Known issue**: `g.co/gemini/share/...` short links not auto-detected. Pass resolved `gemini.google.com/share/...` URL directly.
