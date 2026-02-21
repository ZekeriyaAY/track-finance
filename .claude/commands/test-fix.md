## Fix Failing Tests

Debug and fix failing tests for: $ARGUMENTS

### Workflow

1. **Run the failing test(s)** to see the exact error:
   ```
   docker compose -f docker-compose.yml -f docker-compose.dev.yml exec app pytest -k "$ARGUMENTS" -v --tb=long
   ```

2. **Read the test file** to understand what the test expects

3. **Read the source file** being tested to understand actual behavior

4. **Determine root cause**: Is the bug in the test or in the application code?
   - If test is wrong: fix the test to match correct behavior
   - If app code is wrong: fix the app code, then verify the test passes

5. **Run the full test suite** to ensure no regressions:
   ```
   docker compose -f docker-compose.yml -f docker-compose.dev.yml exec app pytest --tb=short -q
   ```

6. **Report results**: Summarize what was wrong and what was fixed

### Rules
- Never skip or delete a test to make it pass
- Always run the full suite after fixing to catch regressions
- If a fix requires changing behavior, explain the impact
