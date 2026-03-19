#!/usr/bin/env bash
# run.sh — YMind pipeline helper
#
# Usage:
#   run.sh fetch "<url>"        Create run dir, fetch chat → prints RUN_DIR
#   run.sh render <run_dir>     Validate graph.json, render HTML + screenshot
#
# Output directory: $YMIND_DIR (default: ~/ymind)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
YMIND_DIR="${YMIND_DIR:-$HOME/ymind}"

usage() {
    echo "Usage:"
    echo "  run.sh fetch \"<url>\"       Create run dir, fetch chat"
    echo "  run.sh render <run_dir>    Validate graph.json, render HTML + screenshot"
    exit 1
}

_detect_provider() {
    case "$1" in
      *chatgpt.com*)        echo "chatgpt" ;;
      *gemini.google.com*)  echo "gemini" ;;
      *claude.ai*)          echo "claude" ;;
      *)                    echo "chat" ;;
    esac
}

cmd="${1:-}"

case "$cmd" in
  fetch)
    URL="${2:?run.sh fetch requires a URL}"
    PROVIDER="$(_detect_provider "$URL")"
    TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
    RUN_DIR="$YMIND_DIR/${TIMESTAMP}_${PROVIDER}"
    mkdir -p "$RUN_DIR"
    echo "Run dir: $RUN_DIR"

    # Write initial meta.json (title added later by render)
    PROVIDER="$PROVIDER" URL="$URL" RUN_DIR="$RUN_DIR" \
    CREATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)" python3 - <<'PYEOF'
import json, os
data = {
    "provider": os.environ["PROVIDER"],
    "url": os.environ["URL"],
    "created_at": os.environ["CREATED_AT"],
}
with open(os.path.join(os.environ["RUN_DIR"], "meta.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("meta.json: written")
PYEOF

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

    # Update meta.json with title extracted from graph.json
    RUN_DIR="$RUN_DIR" python3 - <<'PYEOF'
import json, os
run_dir = os.environ["RUN_DIR"]
meta_path = os.path.join(run_dir, "meta.json")
graph_path = os.path.join(run_dir, "graph.json")
meta = {}
if os.path.exists(meta_path):
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)
if os.path.exists(graph_path):
    with open(graph_path, encoding="utf-8") as f:
        graph = json.load(f)
    meta["title"] = graph.get("meta", {}).get("title", "")
with open(meta_path, "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
print("meta.json: updated")
PYEOF

    echo ""
    echo "Done: $RUN_DIR"
    ls -1 "$RUN_DIR"
    ;;

  *)
    usage
    ;;
esac
