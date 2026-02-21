## Run Tests

Run the project test suite and analyze results.

### Steps

1. Run tests with HTML report:
   ```
   docker compose -f docker-compose.yml -f docker-compose.dev.yml exec app pytest --html=tests/report.html --self-contained-html -v
   ```

2. If tests fail, analyze failures and provide:
   - Which tests failed and why
   - Suggested fixes for each failure
   - Whether the failure is in test code or application code

3. If `$ARGUMENTS` is provided, run only matching tests:
   ```
   docker compose -f docker-compose.yml -f docker-compose.dev.yml exec app pytest -k "$ARGUMENTS" -v
   ```

### Test Categories
- `make test` - All tests
- `make test-report` - All tests + HTML report
- `make test-cov` - All tests + coverage report
- `make test-security` - Security tests only
