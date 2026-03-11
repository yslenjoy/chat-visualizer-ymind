# YMind Graph Schema Reference

## Node Types - Physics of Thought

All human thinking follows a universal pattern:

| Type | Meaning | Examples |
|------|---------|---------|
| `fact` | Context, anchors, established information | Background, status quo, constraints, options mentioned |
| `friction` | Tensions, blockers, unresolved questions | Contradictions, doubts, fears, trade-offs, gaps |
| `spark` | Insights, reframes, breakthroughs | "Aha!" moments, new perspectives, realizations |
| `action` | Concrete next steps, decisions | Commitments, plans, things to do |

### Thinking Flow Pattern

```
fact -> friction -> spark -> action
(context)  (tension)  (insight)  (next step)
```

Not every conversation follows this linearly. Real conversations loop, branch, and revisit.

## Edge Types

| Relation | Direction | Meaning | Example |
|----------|-----------|---------|---------|
| `causes` | Fact -> Friction | This context creates this tension | "Limited budget" causes "Can't hire enough" |
| `opposes` | Node <-> Node | These are in conflict | "Move fast" opposes "Be thorough" |
| `resolves` | Spark/Action -> Friction | This addresses the tension | "Hire contractors" resolves "Can't hire enough" |
| `leads_to` | Spark -> Action | This insight leads to this step | "Realized MVP is enough" leads_to "Ship by Friday" |

### Relation Quality Rule

Only add a relation if it passes the "obviously yes" test:
"If I explained this connection to the user, would they immediately agree?"

Avoid:
- Connecting nodes just because they share a topic
- Forcing relations between every node
- Creating chains that don't reflect actual reasoning

## Reasoning Shift Types

| Type | Meaning | Signal |
|------|---------|--------|
| `reframe` | Perspective changed | "Actually, looking at it differently..." |
| `contradiction` | Counterargument shifted direction | "But that doesn't work because..." |
| `breakthrough` | Sudden clarity | "Oh! That means..." |
| `pivot` | Abandoned one path for another | "Let's try a completely different approach" |
| `decision` | Chose between options | "OK, I'll go with option B" |

## Label Extraction Rules

Labels should be extracted from actual words, not invented abstractions:

| Bad (abstract) | Good (from source) |
|---|---|
| "Monetization Confusion" | "How To Monetize Skills" |
| "Execution Gap" | "Missing Next Steps" |
| "变现困惑" | "怎么变现能力" |

Rules:
- 2-5 words
- English: Title Case
- Chinese: natural phrasing
- Must be recognizable if user sees it

## Output JSON Schema

```json
{
  "meta": {
    "title": "string - short conversation title",
    "total_turns": "number - total conversation turns",
    "language": "string - detected language code (en/zh/etc)"
  },
  "graph": {
    "nodes": [
      {
        "id": "string - unique identifier (n1, n2, ...) ",
        "label": "string - 2-5 words from actual conversation",
        "type": "fact | friction | spark | action",
        "rich_summary": "string - 1-2 sentence self-contained description",
        "source": "user | ai",
        "turn_id": "number - which conversation turn"
      }
    ],
    "edges": [
      {
        "source": "string - source node id",
        "target": "string - target node id",
        "relation_type": "causes | opposes | resolves | leads_to"
      }
    ]
  },
  "reasoning_shifts": [
    {
      "from_node": "string - node id where old thinking was",
      "to_node": "string - node id where new thinking emerged",
      "type": "reframe | contradiction | breakthrough | pivot | decision",
      "description": "string - what changed and why"
    }
  ],
  "actions": [
    {
      "content": "string - specific action item",
      "priority": "high | medium | low",
      "related_nodes": ["string - related node ids"]
    }
  ],
  "summary": "string - 2-3 sentence overview"
}
```
