#!/bin/bash
# PostToolUse hook: Remind to update CLAUDE.md when architecture/design files change
# Triggers on Write|Edit of files that contain information documented in CLAUDE.md
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')

# Skip if no file path (shouldn't happen for Write|Edit)
if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Skip CLAUDE.md itself
if [[ "$FILE_PATH" == *"CLAUDE.md"* ]]; then
  exit 0
fi

BASENAME=$(basename "$FILE_PATH")

# Design system files - colors, fonts, layout
DESIGN_FILES="base_layout.html style.css"

# Architecture files - stack, middleware, config
ARCH_FILES="app.py config.py requirements.txt docker-compose.yml"

# Check design system files
for F in $DESIGN_FILES; do
  if [[ "$BASENAME" == "$F" ]]; then
    echo "{\"systemMessage\": \"CLAUDE.md sync: '$BASENAME' was modified. If colors, fonts, or design tokens changed, update the Design System section in CLAUDE.md.\"}"
    exit 0
  fi
done

# Check architecture files
for F in $ARCH_FILES; do
  if [[ "$BASENAME" == "$F" ]]; then
    echo "{\"systemMessage\": \"CLAUDE.md sync: '$BASENAME' was modified. If stack, env vars, or architecture patterns changed, update the relevant section in CLAUDE.md.\"}"
    exit 0
  fi
done

# Check for NEW model or route files (Write tool only)
if [[ "$TOOL_NAME" == "Write" ]]; then
  if [[ "$FILE_PATH" == */models/*.py ]] && [[ "$BASENAME" != "__init__.py" ]]; then
    echo "{\"systemMessage\": \"CLAUDE.md sync: New model file '$BASENAME' created. Update the Schema Overview section in CLAUDE.md if this adds a new domain entity.\"}"
    exit 0
  fi
  if [[ "$FILE_PATH" == */routes/*.py ]]; then
    echo "{\"systemMessage\": \"CLAUDE.md sync: New route file '$BASENAME' created. Update the Architecture Fundamentals section in CLAUDE.md if this adds a new blueprint.\"}"
    exit 0
  fi
fi

exit 0
