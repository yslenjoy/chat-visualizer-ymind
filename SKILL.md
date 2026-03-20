---
name: chat-visualizer-ymind
description: Turn AI chat transcripts into structured YMind thinking maps with reasoning nodes, thinking shifts, and action items — rendered as an interactive D3.js force graph. Use this skill whenever a user shares a ChatGPT, Gemini, or Claude conversation URL and wants to visualize, analyze, or extract insights from it — even if they just say "help me understand this chat", "what was decided here", or "summarize the key takeaways" without explicitly asking for a graph or visualization.
---

# Chat Visualizer - YMind

## Input

Two ways to get conversation data:

### Way 1: Share URL (auto-fetch)

Requires Playwright. Check first:
```bash
python3 -c "import playwright" 2>/dev/null && echo "OK" || echo "NOT INSTALLED"
```
If not installed, ask: "Playwright 可以自动抓取对话内容，要装吗？（`pip install playwright && playwright install chromium`，一次性操作）" If they decline, use Way 2.

If available, fetch:
```bash
conda run -n ymind bash scripts/run.sh fetch "<url>"
# prints RUN_DIR — read <run_dir>/raw_chat.json, use items[0].messages
```

ChatGPT 403: script retries with Playwright headed mode. If still fails, fall back to Way 2.

### Way 2: Paste text (universal fallback)

User opens the conversation in browser → Ctrl+A → Ctrl+C → pastes into chat. No share link needed — any conversation page works.

When handling pasted text:
1. Create run_dir manually:
   ```bash
   YMIND_DIR="${YMIND_DIR:-$HOME/ymind-ws}"
   RUN_DIR="$YMIND_DIR/$(date +%Y%m%d-%H%M%S)_paste"
   mkdir -p "$RUN_DIR"
   ```
2. Parse the pasted text into messages (identify user vs AI turns by context), then write `raw_chat.json` in the same format as fetch produces:
   ```json
   {
     "fetched_at": "...",
     "items": [{
       "url": null,
       "provider": "paste",
       "title": "...",
       "messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...],
       "message_count": N
     }]
   }
   ```
3. Write `meta.json`: `{"provider": "paste", "url": null, "created_at": "..."}`
4. Proceed to Extract Graph using the parsed messages.

### Share Link Guide (Way 1 only)

Users often give the wrong link type. Correct them if needed:

| Platform | Share link ✓ | Wrong link ✗ |
|----------|-------------|-------------|
| ChatGPT | `chatgpt.com/share/xxx` | `chatgpt.com/c/xxx` (private chat URL) |
| Claude | `claude.ai/share/xxx` | `claude.ai/chat/xxx` (private chat URL) |
| Gemini | `gemini.google.com/share/xxx` | `gemini.google.com/app/xxx` (app URL) |

Note: `g.co/gemini/share/...` short links work — script auto-resolves them.

## Extract Graph

Read `references/graph-schema.md` for node types, edge types, label rules, and output schema.

Critical rules (non-obvious):
- `turn_id`: assign actual turn number (1-based). Never default all nodes to the same value — this drives horizontal spread in the D3 visualization.
- Extraction density: scale with the substance of each turn. Brief or routine turns may yield 1-2 nodes; rich, multi-point turns can yield more. Let the content guide the count — the goal is to capture the meaningful thinking, not to hit a fixed number.
- Edges: only add if the connection passes the "obviously yes" test.
- Reasoning shifts: look for moments where thinking fundamentally changed. Capture what changed, from what, to what, and why.
- Chinese strings: use `「」` not curly quotes `""` inside JSON values — curly quotes break JSON parsing.

## Output

1. Write `<run_dir>/graph.json`
2. Render:

```bash
conda run -n ymind bash scripts/run.sh render <run_dir>
# validates JSON, renders graph.html + graph.png (screenshot, requires Playwright)
```

3. Output Markdown summary (format in `references/graph-schema.md`).

Run dir files: `raw_chat.json`, `graph.json`, `graph.html`, `graph.png` (requires Playwright), `meta.json`.

## Language Rule

All output (labels, summaries, analysis) must match the conversation language.

## Setup

**Minimal (paste text only — zero dependencies):**

No pip install needed. `render-html.py` is stdlib-only, and the paste path skips `fetch-chat.py` entirely.

**Full (auto-fetch URLs + screenshot):**
```bash
pip install requests playwright && playwright install chromium
```

Without Playwright: paste works fully, render produces `graph.html` but skips `graph.png` screenshot.

## Notes

- Long conversations (20+ turns): focus on most significant nodes, skip low-substance turns.
- Multiple topics: group nodes by topic.
