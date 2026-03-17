---
name: chat-visualizer-ymind
description: Visualize AI chat transcripts as YMind thinking maps. Use when a user provides a conversation transcript or export and wants reasoning nodes, thinking shifts, action items, JSON-first output, or optional HTML rendering for sharing.
---

# Chat Visualizer - YMind

Turn any AI conversation into a structured thinking map.

## Input

The user provides one of:
- A share URL (ChatGPT / Gemini / Claude)
- Plain text (copy-pasted conversation)
- JSON with a `messages` array (each message has `role` and `content`)

**If input is a URL**, first create the run directory (see File Storage), then run the fetch script:

```bash
python3 scripts/fetch-chat.py "<url>" --out <run_dir>/raw_chat.json
```

Then read `<run_dir>/raw_chat.json` and use `items[0].messages` as the conversation input.

**ChatGPT 403 fallback**: `fetch-chat.py` calls ChatGPT's private `/backend-api/share/...` endpoint. Without auth cookies it returns 403. If this happens, open the share URL in the browser, select-all and copy the full conversation text, then proceed as plain text input below.

**If input is plain text**, parse it into structured turns. Look for patterns like:
- "User:", "Assistant:", "Human:", "AI:", "ChatGPT:", "Claude:" prefixes
- Alternating speaker patterns

## Task

Analyze the entire conversation and extract a thinking graph in two steps.

### Step 1: Extract the Graph (JSON)

For each meaningful point in the conversation, create a node.

Node types (Physics of Thought):
- `fact` - Context, background, established information, anchors
- `friction` - Contradictions, doubts, fears, blockers, unresolved tensions
- `spark` - Insights, reframes, "Aha!" moments, new perspectives
- `action` - Concrete next steps, decisions, commitments

Rules for node extraction:
- Extract labels directly from the speaker's actual words (2-5 words, not abstract summaries)
- English labels: Title Case. Chinese labels: natural phrasing.
- Each node needs a `rich_summary`: a self-contained 1-2 sentence description
- Mark `source` as "user" or "ai" based on who introduced the idea
- Mark `turn_id` to track which conversation turn it came from (integer, starting from 1). This is critical for visualization layout — nodes with different `turn_id` values spread horizontally. Always assign the actual turn number, never default all nodes to the same value.
- Typically extract 2-5 nodes per turn. Whether a turn has substance is judged by the **AI response content**, not the user message length. A 2-character user message like "继续" or "需要" can still produce a substantive AI response worth extracting. Only skip a turn if the AI response itself is off-topic or contains no reasoning content (e.g., a system message about app settings).

Relations between nodes:
- `causes`: Fact -> Friction (this fact creates this problem)
- `opposes`: Node <-> Node (these are in conflict)
- `resolves`: Spark/Action -> Friction (this insight addresses this problem)
- `leads_to`: Spark -> Action (this insight leads to this action)

Quality check: Before adding any relation, ask "Would the user say obviously yes or that's a stretch?" Only add if obviously yes.

Detect reasoning shifts (killer feature):
Look for moments where thinking fundamentally changed:
- A counterargument that shifted direction
- A reframe that changed perspective
- A breakthrough insight
- An abandoned hypothesis
- A decision point

Each shift should capture what changed, from what to what, and why.

### Step 2: Output

Return the result as a JSON code block with this structure. Use the schema in `references/graph-schema.md` and ensure `relation_type` is used for edges.

```json
{
  "meta": {
    "title": "Short conversation title",
    "total_turns": 8,
    "language": "en"
  },
  "graph": {
    "nodes": [
      {
        "id": "n1",
        "label": "Extracted Label",
        "type": "fact|friction|spark|action",
        "rich_summary": "Self-contained description of this point",
        "source": "user|ai",
        "turn_id": 1
      }
    ],
    "edges": [
      {
        "source": "n1",
        "target": "n2",
        "relation_type": "causes|opposes|resolves|leads_to"
      }
    ]
  },
  "reasoning_shifts": [
    {
      "from_node": "n3",
      "to_node": "n5",
      "type": "reframe|contradiction|breakthrough|pivot|decision",
      "description": "User initially thought X, but after AI pointed out Y, shifted to Z"
    }
  ],
  "actions": [
    {
      "content": "Specific action item text",
      "priority": "high|medium|low",
      "related_nodes": ["n7", "n8"]
    }
  ],
  "summary": "2-3 sentence overview of the conversation's thinking journey"
}
```

**After writing graph.json**, validate before proceeding:

```bash
python3 -c "import json; json.load(open('<run_dir>/graph.json'))" && echo "JSON valid"
```

Fix any parse errors before running `render-html.py`. The most common cause is unescaped Chinese curly quotes (`"` `"`) inside string values — use `「」` or `『』` for emphasis instead, or rewrite without quotes.

After the JSON block, provide a Markdown summary for human reading.

Markdown summary format:
```
## Thinking Map: {title}

### Reasoning Timeline
{For each reasoning shift, show the flow with arrows}

Problem/Context
  ->
Hypothesis/Exploration
  ->
Turning Point: {what changed}
  ->
Insight: {key realization}
  ->
Action: {what to do}

### Key Insights
- {spark nodes, ranked by importance}

### Action Items
- [ ] {action 1} (priority)
- [ ] {action 2} (priority)

### Node Summary
| Type | Count | Key Examples |
|------|-------|-------------|
| Fact | N | ... |
| Friction | N | ... |
| Spark | N | ... |
| Action | N | ... |
```

## File Storage

**All output files MUST go into a single run directory.** Do not scatter files across `/tmp`, Downloads, or the skill directory.

Required run directory path:
```
~/workspace/ymind/run_<yyyymmdd-HHMMSS>/
```

Example for a run on 2026-03-17 at 14:30:00:
```
~/workspace/ymind/run_20260317-143000/
  raw_chat.json    ← fetch-chat.py output (input data, keep for reproducibility)
  graph.json       ← LLM-generated graph (the primary artifact)
  graph.html       ← render-html.py output (shareable visualization)
```

Rules:
- Create the run directory before writing any files.
- All files go into the run directory. Do not use `/tmp` at any step.
- After all steps complete, report the full path to the run directory and list its files.
- If `render-html.py` is not run (user only wants JSON), `graph.html` is optional.

## Language Rule

All output (labels, summaries, analysis) must match the language of the conversation. If the conversation is in Chinese, output in Chinese. If in English, output in English.

## Setup

Install Python dependencies before running scripts:

```bash
pip install -r requirements.txt
playwright install chromium   # only needed for Gemini/Claude share URLs
```

`render-html.py` has no external dependencies for basic rendering. It also supports `--screenshot` / `-s` to capture a PNG of the visualization (requires `playwright install chromium`). Note: the script spins up a headless Chromium + waits 3 s for D3 simulation to settle, so it adds ~5 s versus opening the HTML in your browser and screenshotting manually.

## Notes

- For very long conversations (20+ turns), focus on the most significant nodes rather than extracting everything
- If the conversation has multiple distinct topics, group nodes by topic in the graph
- The JSON output is designed to be machine-readable so other tools can consume it for further analysis or HTML visualization
- **Known issue**: `g.co/gemini/share/...` short links are not auto-detected as Gemini URLs. Pass the resolved URL (`gemini.google.com/share/...`) directly to `fetch-chat.py`. TODO: add redirect-following in `_guess_provider()`.
