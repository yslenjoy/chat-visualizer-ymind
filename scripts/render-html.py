#!/usr/bin/env python3
"""
Render a YMind graph JSON into a self-contained HTML visualization.

Usage:
  python3 render-html.py graph.json
  python3 render-html.py graph.json --out ymindmap-output.html

Input: graph.json produced by SKILL.md (agent mode) or extract-graph.py (script mode).
Output: A single HTML file with the graph data embedded inline.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "templates" / "ymindmap.html"


def slugify(text: str, max_len: int = 40) -> str:
    """Turn a title into a filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:max_len].rstrip("-")


def render(graph_json: dict, template: str) -> str:
    """Inject graph data into the HTML template."""
    title = ""
    if "meta" in graph_json and graph_json["meta"]:
        title = graph_json["meta"].get("title", "")

    html = template.replace("{{TITLE}}", title or "Untitled")
    html = html.replace("{{GRAPH_JSON}}", json.dumps(graph_json, ensure_ascii=False))
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description="Render YMind graph as HTML.")
    parser.add_argument("input", help="Path to graph.json")
    parser.add_argument("--out", "-o", default=None, help="Output HTML path (default: auto-named)")
    parser.add_argument("--template", "-t", default=None, help="Custom template path")
    args = parser.parse_args()

    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        return 1

    with open(input_path, "r", encoding="utf-8") as f:
        graph_data = json.load(f)

    # Read template
    tmpl_path = Path(args.template) if args.template else TEMPLATE_PATH
    if not tmpl_path.exists():
        print(f"Error: template not found at {tmpl_path}", file=sys.stderr)
        return 1

    template = tmpl_path.read_text(encoding="utf-8")

    # Render
    html = render(graph_data, template)

    # Output path
    if args.out:
        out_path = Path(args.out)
    else:
        title = ""
        if "meta" in graph_data and graph_data["meta"]:
            title = graph_data["meta"].get("title", "")
        slug = slugify(title) if title else input_path.stem
        out_path = input_path.parent / f"ymindmap-{slug}.html"

    out_path.write_text(html, encoding="utf-8")
    print(f"Rendered: {out_path}")
    print(f"  Open in browser to view the visualization.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
