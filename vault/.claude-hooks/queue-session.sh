#!/usr/bin/env bash
# SessionEnd hook: copies the session JSONL to vault/raw/sessions/ and queues it for ingest.
# Called automatically by Claude Code when a session ends.

VAULT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SESSIONS_DIR="$VAULT_DIR/raw/sessions"
QUEUE_FILE="$VAULT_DIR/.ingest-queue.jsonl"
MANIFEST_FILE="$VAULT_DIR/.ingested-manifest.json"
DEBUG_LOG="$VAULT_DIR/.sessionend-debug.log"

# Read hook input from stdin (JSON with transcript_path, session_id, etc.)
INPUT=$(cat)

{
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] SessionEnd hook fired"
  echo "Raw input: $INPUT"
  echo "CLAUDE_PROJECT_DIR: ${CLAUDE_PROJECT_DIR:-unset}"

  # Extract transcript_path and session_id from hook input
  TRANSCRIPT_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('transcript_path',''))" 2>&1) || TRANSCRIPT_PATH=""
  SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id',''))" 2>&1) || SESSION_ID=""

  echo "Parsed transcript_path: $TRANSCRIPT_PATH"
  echo "Parsed session_id: $SESSION_ID"

  # Validate we have what we need
  if [ -z "$TRANSCRIPT_PATH" ] || [ -z "$SESSION_ID" ]; then
    echo "SKIP: missing transcript_path or session_id"
    exit 0
  fi

  if [ ! -f "$TRANSCRIPT_PATH" ]; then
    echo "SKIP: transcript file not found: $TRANSCRIPT_PATH"
    exit 0
  fi

  # Check if already in manifest
  if [ -f "$MANIFEST_FILE" ]; then
    ALREADY=$(python3 -c "
import json
with open('$MANIFEST_FILE') as f:
    data = json.load(f)
found = any(e['session_id'] == '$SESSION_ID' for e in data.get('ingested', []))
print('yes' if found else 'no')
" 2>/dev/null) || ALREADY="no"
    if [ "$ALREADY" = "yes" ]; then
      echo "SKIP: already ingested"
      exit 0
    fi
  fi

  # Copy JSONL to vault/raw/sessions/
  DEST="$SESSIONS_DIR/${SESSION_ID}.jsonl"
  if cp "$TRANSCRIPT_PATH" "$DEST" 2>&1; then
    echo "Copied to: $DEST"
  else
    echo "ERROR: cp failed"
    exit 0
  fi

  # Append to ingest queue
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "{\"session_id\": \"$SESSION_ID\", \"jsonl_path\": \"raw/sessions/${SESSION_ID}.jsonl\", \"queued_at\": \"$TIMESTAMP\", \"status\": \"pending\"}" >> "$QUEUE_FILE"
  echo "Queued successfully"
  echo "---"

} >> "$DEBUG_LOG" 2>&1
