# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) setup for Logbook.

## Overview

Logbook uses GitHub Actions for automated testing and code coverage reporting. The pipeline is designed to run tests efficiently by only executing relevant test suites when their corresponding code changes.

## Workflow Structure

The CI pipeline is defined in `.github/workflows/test.yml` and consists of two parallel jobs:

### 1. API Server Tests (`apiserver-tests`)

**Purpose:** Run Python/Flask backend tests with pytest

**Triggers when:**
- Files in `apiserver/**` change
- Files in `tests/**` change
- `requirements.txt` changes
- `pytest.ini` changes
- Workflow file itself changes

**Skips when:**
- Only documentation files (`.md`, `LICENSE`) change
- Only webserver files change
- Commit message contains `[skip ci]`

**Steps:**
1. Checkout code
2. Detect changed files using `dorny/paths-filter@v3`
3. Set up Python 3.12 (if needed)
4. Install dependencies from `requirements.txt` (if needed)
5. Run pytest with coverage (`pytest --cov=apiserver --cov-branch`)
6. Upload coverage to Codecov with `apiserver` flag
7. Archive coverage reports as artifacts

**Coverage Target:** 95%

### 2. Web Server Tests (`webserver-tests`)

**Purpose:** Run JavaScript/TypeScript frontend tests with Vitest

**Triggers when:**
- Files in `webserver/**` change
- Workflow file itself changes

**Skips when:**
- Only documentation files change
- Only API server files change
- Commit message contains `[skip ci]`

**Steps:**
1. Checkout code
2. Detect changed files using `dorny/paths-filter@v3`
3. Set up Node.js 20 (if needed)
4. Install dependencies with `npm ci` (if needed)
5. Run Vitest with coverage (`npm run test:coverage`)
6. Upload coverage to Codecov with `webserver` flag
7. Archive coverage reports as artifacts

**Coverage Target:** 90%

## Smart Path Filtering

The workflow uses the `dorny/paths-filter` action to intelligently determine which jobs need to run based on file changes. This approach:

- **Saves CI minutes** by skipping unnecessary test runs
- **Speeds up feedback** by running only relevant tests
- **Prevents false failures** from unrelated changes

### How It Works

Each job has two levels of filtering:

1. **Job-level `if` condition:** Checks for `[skip ci]` in commit messages
2. **Step-level conditions:** Only execute steps if relevant files changed

This allows jobs to appear in the workflow run but skip execution when not needed.

### Path Filter Configuration

**API Server:**
```yaml
apiserver:
  - 'apiserver/**'
  - 'tests/**'
  - 'requirements.txt'
  - 'pytest.ini'
  - '.github/workflows/test.yml'
```

**Web Server:**
```yaml
webserver:
  - 'webserver/**'
  - '.github/workflows/test.yml'
```

## Code Coverage with Codecov

### Configuration

Coverage is configured in `codecov.yml` with separate flags for each component:

**Flags:**
- `apiserver`: Python backend coverage
- `webserver`: JavaScript frontend coverage

**Features:**
- **Carryforward:** Previous coverage is used when code doesn't change
- **Component tracking:** Separate coverage targets per component
- **Combined badge:** Single badge shows overall project coverage

### Coverage Targets

- **API Server:** 95% coverage (Python)
- **Web Server:** 90% coverage (JavaScript)
- **Overall Project:** Auto (combined)

### Codecov Badge

The README includes a codecov badge that shows **combined coverage** from both components:

```markdown
[![codecov](https://codecov.io/gh/aman-chauhan/logbook/branch/main/graph/badge.svg)](https://codecov.io/gh/aman-chauhan/logbook)
```

The badge automatically updates when either coverage report is uploaded. You can view detailed coverage breakdown by clicking the badge or visiting the Codecov dashboard.

### Viewing Coverage by Component

On the Codecov dashboard, you can filter coverage by flag:

- **All Coverage:** Combined view (default)
- **API Server Only:** Filter by `apiserver` flag
- **Web Server Only:** Filter by `webserver` flag

## Artifacts

Both jobs archive their coverage reports as GitHub Actions artifacts:

- **apiserver-coverage-report:** Contains `coverage.xml` and `htmlcov/`
- **webserver-coverage-report:** Contains `webserver/coverage/`

Artifacts are retained for 30 days and can be downloaded from the workflow run page.

## Running Tests Locally

### API Server Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apiserver --cov-report=term-missing --cov-branch

# Run with HTML coverage report
pytest --cov=apiserver --cov-report=html
```

### Web Server Tests

```bash
cd webserver

# Run tests in watch mode
npm test

# Run tests once
npm run test:run

# Run with coverage
npm run test:coverage

# Run with interactive UI
npm run test:ui
```

## Skipping CI

To skip CI runs entirely (e.g., for documentation-only changes), include `[skip ci]` in your commit message:

```bash
git commit -m "Update README [skip ci]"
```

## Environment Variables

### API Server Tests

Set in workflow file:
```yaml
FLASK_APP: apiserver/run.py
FLASK_DEBUG: 0
SECRET_KEY: test-secret-key-for-ci
SQLALCHEMY_DATABASE_URI: sqlite:///test.db
```

### Codecov Upload

Requires secret:
```yaml
CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

This token is configured in repository secrets and allows uploading coverage data to Codecov.

## Adding New Tests

### For API Server

1. Add test files to `tests/unit/` or `tests/integration/`
2. Follow existing patterns (use pytest fixtures, faker for data)
3. Run locally to verify
4. Commit and push - CI will automatically run

### For Web Server

1. Add test files as `*.test.ts` or `*.spec.ts` next to source files
2. Use Vitest's `describe`, `it`, `expect` pattern
3. Mock external dependencies (fetch, localStorage, etc.)
4. Run locally with `npm test`
5. Commit and push - CI will automatically run

## Troubleshooting

### Tests Pass Locally but Fail in CI

1. Check environment variables in workflow file
2. Verify dependencies are properly listed in `requirements.txt` or `package.json`
3. Look for filesystem path differences (Windows vs Linux)
4. Check for timezone or locale-specific issues

### Coverage Upload Fails

1. Verify `CODECOV_TOKEN` secret is set in repository settings
2. Check Codecov service status
3. Review workflow logs for specific error messages
4. Ensure coverage files are generated before upload step

### Path Filter Not Working

1. Verify file paths match filter patterns exactly
2. Check that `dorny/paths-filter@v3` action is running
3. Review the "Check for X changes" step output
4. Ensure `steps.changes.outputs.X == 'true'` conditions are correct

## Best Practices

1. **Write tests first:** Add tests before implementing features
2. **Maintain coverage:** Don't let coverage drop below targets
3. **Fix failing tests immediately:** Don't merge broken code
4. **Review coverage reports:** Look for untested edge cases
5. **Use descriptive test names:** Make failures easy to understand
6. **Keep tests fast:** Slow tests discourage running them
7. **Mock external dependencies:** Tests should be isolated
8. **Test both success and failure cases:** Edge cases matter

## Future Improvements

Potential enhancements to consider:

- **Integration tests in CI:** Test API + webserver together
- **E2E tests:** Playwright or Cypress for full user flows
- **Performance benchmarks:** Track response times over time
- **Security scanning:** SAST/DAST tools for vulnerability detection
- **Deploy previews:** Automatic deployment for pull requests
- **Scheduled tests:** Nightly runs against production-like environment

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Codecov Documentation](https://docs.codecov.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [dorny/paths-filter Action](https://github.com/dorny/paths-filter)
