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

Just paste a conversation to the agent:

```
Visualize this conversation:

User: I'm thinking about switching careers...
Assistant: That's a big decision...
...
```

The skill outputs:
1. **JSON graph** (machine-readable, for further processing)
2. **Markdown summary** (human-readable, with reasoning timeline + action items)

## Part of YMind

This is one skill in the YMind plugin family:

| Skill | Status | Description |
|-------|--------|-------------|
| `chat-visualizer-ymind` | v0.1 | Single conversation visualization |
| `session-analysis-ymind` | planned | Cross-session pattern discovery |
| `capture-idea-ymind` | planned | Quick idea/inspiration capture |

## License

MIT
