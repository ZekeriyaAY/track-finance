#!/bin/bash
# PreToolUse hook: Block git commit if tests are failing
# Intercepts Bash tool calls that contain "git commit"
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only intercept git commit commands
if [[ "$COMMAND" != *"git commit"* ]]; then
  exit 0
fi

# Run tests in Docker
RESULT=$(docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T app pytest --tb=line -q 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  SUMMARY=$(echo "$RESULT" | tail -3)
  echo "BLOCKED: Tests must pass before committing. Run 'make test' to see failures." >&2
  echo "$SUMMARY" >&2
  exit 2  # Exit 2 = block the action
fi

exit 0
