#!/usr/bin/env bash
# run.sh — YMind pipeline helper
#
# Usage:
#   run.sh fetch "<url>"        Create run dir, fetch chat → prints RUN_DIR
#   run.sh render <run_dir>     Validate graph.json, render HTML + screenshot

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
    echo "Usage:"
    echo "  run.sh fetch \"<url>\"       Create run dir, fetch chat"
    echo "  run.sh render <run_dir>    Validate graph.json, render HTML + screenshot"
    exit 1
}

cmd="${1:-}"

case "$cmd" in
  fetch)
    URL="${2:?run.sh fetch requires a URL}"
    RUN_DIR="$HOME/workspace/ymind/run_$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$RUN_DIR"
    echo "Run dir: $RUN_DIR"
    python3 "$SCRIPT_DIR/fetch-chat.py" "$URL" --out "$RUN_DIR/raw_chat.json"
    echo ""
    echo "RUN_DIR=$RUN_DIR"
    ;;

  render)
    RUN_DIR="${2:?run.sh render requires a run_dir path}"
    GRAPH="$RUN_DIR/graph.json"
    if [ ! -f "$GRAPH" ]; then
        echo "Error: $GRAPH not found" >&2
        exit 1
    fi
    python3 -c "import json; json.load(open('$GRAPH'))" && echo "graph.json: valid"
    python3 "$SCRIPT_DIR/render-html.py" "$GRAPH" --out "$RUN_DIR/graph.html" --screenshot
    echo ""
    echo "Done: $RUN_DIR"
    ls -1 "$RUN_DIR"
    ;;

  *)
    usage
    ;;
esac
