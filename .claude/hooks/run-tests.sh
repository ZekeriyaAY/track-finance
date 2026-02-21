#!/bin/bash
# PostToolUse hook: Run tests after Python file edits
# Only triggers for .py file changes, runs in Docker container
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only run for Python files
if [[ "$FILE_PATH" != *.py ]]; then
  exit 0
fi

# Skip test runs for non-code files
if [[ "$FILE_PATH" == *__pycache__* ]] || [[ "$FILE_PATH" == *migrations* ]]; then
  exit 0
fi

# Run tests in Docker (quick check)
RESULT=$(docker compose -f docker-compose.yml -f docker-compose.dev.yml exec -T app pytest --tb=line -q 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  SUMMARY=$(echo "$RESULT" | tail -1)
  echo "{\"systemMessage\": \"Tests passed: $SUMMARY\"}"
else
  FAILED=$(echo "$RESULT" | grep "FAILED\|ERROR" | head -5)
  echo "{\"systemMessage\": \"Tests FAILED after editing $(basename "$FILE_PATH"). Failures:\\n$FAILED\"}"
fi

exit 0
