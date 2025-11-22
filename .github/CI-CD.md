# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) setup for Logbook.

## Overview

Logbook uses GitHub Actions for automated testing and code coverage reporting. The pipeline is designed to ensure comprehensive quality checks by running both API server and web server test suites on all pull requests, serving as the qualifying condition for merging to main.

## Workflow Structure

The CI pipeline is defined in `.github/workflows/test.yml` and consists of two parallel jobs that run on every push to `main` and every pull request to `main` or `develop`.

### 1. API Server Tests (`apiserver-tests`)

**Purpose:** Run Python/Flask backend tests with pytest

**Runs on:**
- Every push to `main` branch
- Every non-draft pull request to `main` or `develop`

**Skips when:**
- Pull request is in draft state
- Only documentation files (`.md`, `LICENSE`, `docs/**`) change (workflow-level filter)

**Steps:**
1. Checkout code
2. Set up Python 3.12 with pip cache
3. Install dependencies from `requirements.txt`
4. Run pytest with coverage
5. Upload coverage to Codecov with `apiserver` flag
6. Archive coverage reports as artifacts (retention: 30 days)

**Coverage Target:** 95%

### 2. Web Server Tests (`webserver-tests`)

**Purpose:** Run JavaScript/TypeScript frontend tests with Vitest

**Runs on:**
- Every push to `main` branch
- Every non-draft pull request to `main` or `develop`

**Skips when:**
- Pull request is in draft state
- Only documentation files (`.md`, `LICENSE`, `docs/**`) change (workflow-level filter)

**Steps:**
1. Checkout code
2. Set up Node.js 20
3. Install dependencies with `npm install`
4. Run Vitest with coverage
5. Upload coverage to Codecov with `webserver` flag
6. Archive coverage reports as artifacts (retention: 30 days)

**Coverage Target:** 90%

## Test Execution Strategy

The workflow uses a comprehensive testing approach with smart filtering to balance thoroughness and efficiency:

### Comprehensive Testing
- **Both test suites always run** regardless of which files changed
- This ensures all PRs undergo full validation before merge
- Prevents surprises from component interactions or shared dependencies

### Draft PR Detection
- Tests **automatically skip** when a pull request is in draft state
- Allows work-in-progress without wasting CI resources
- When PR is marked "Ready for review", tests run automatically

### Documentation Changes
- Workflow-level `paths-ignore` filter skips tests for documentation-only changes
- Applies to: `**/*.md`, `LICENSE`, `docs/**`
- This is the only path-based filtering in the pipeline

### How It Works

**Trigger Logic:**
```yaml
on:
  push:
    branches: [ main ]
    paths-ignore: ['**/*.md', 'LICENSE', 'docs/**']
  pull_request:
    types: [ opened, synchronize, reopened, ready_for_review ]
    branches: [ main, develop ]
    paths-ignore: ['**/*.md', 'LICENSE', 'docs/**']
```

**Pull Request Event Types:**
- `opened`: When a PR is first created
- `synchronize`: When new commits are pushed to the PR
- `reopened`: When a closed PR is reopened
- `ready_for_review`: When a draft PR is marked as ready (triggers tests automatically)

**Job-Level Condition:**
```yaml
if: github.event_name != 'pull_request' || github.event.pull_request.draft == false
```

This ensures:
- ✅ All pushes to `main` run tests
- ✅ Non-draft PRs run both test suites completely
- ❌ Draft PRs skip tests (saves CI minutes)
- ❌ Documentation-only changes skip tests (workflow doesn't trigger)

## Working with Draft Pull Requests

Draft PRs provide a way to share work-in-progress without triggering expensive CI runs.

### Creating a Draft PR

**Via GitHub UI:**
1. Click "Create pull request" dropdown
2. Select "Create draft pull request"

**Via GitHub CLI:**
```bash
gh pr create --draft --title "WIP: Feature name" --body "Description"
```

### When Tests Run

| PR State | Tests Run? | Why |
|----------|-----------|-----|
| Draft | ❌ No | Saves CI minutes during development |
| Ready for review | ✅ Yes | Full validation before merge |
| Converted draft → ready | ✅ Yes | Automatic on status change |
| Converted ready → draft | ❌ No | Stops future test runs |

### Best Practices

1. **Use drafts for WIP:** Start with draft PRs when code isn't ready for review
2. **Mark ready when complete:** Convert to "Ready for review" when tests should run
3. **Test locally first:** Run `pytest` and `npm test` before marking ready
4. **Check CI status:** Ensure both jobs pass before requesting review

### Converting Between States

**Draft → Ready for Review:**
- GitHub UI: Click "Ready for review" button
- GitHub CLI: `gh pr ready <number>`
- **Effect:** Tests will run automatically

**Ready → Draft:**
- GitHub UI: Click "Convert to draft" in sidebar
- GitHub CLI: `gh pr ready <number> --undo`
- **Effect:** Future commits won't trigger tests

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
4. Commit and push - CI will run **both** API and web server tests

### For Web Server

1. Add test files as `*.test.ts` or `*.spec.ts` next to source files
2. Use Vitest's `describe`, `it`, `expect` pattern
3. Mock external dependencies (fetch, localStorage, etc.)
4. Run locally with `npm test`
5. Commit and push - CI will run **both** API and web server tests

**Note:** Both test suites always run on PRs, regardless of which files changed. This ensures comprehensive validation before merge.

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

### Tests Not Running on PR

1. Check if PR is in draft state - tests skip for drafts
2. Verify PR targets `main` or `develop` branch
3. Check if only documentation files changed (workflow won't trigger)
4. Review workflow logs for job-level condition evaluation

## Best Practices

1. **Write tests first:** Add tests before implementing features
2. **Maintain coverage:** Don't let coverage drop below targets
3. **Fix failing tests immediately:** Don't merge broken code
4. **Review coverage reports:** Look for untested edge cases
5. **Use descriptive test names:** Make failures easy to understand
6. **Keep tests fast:** Slow tests discourage running them
7. **Mock external dependencies:** Tests should be isolated
8. **Test both success and failure cases:** Edge cases matter
9. **Use draft PRs during development:** Save CI minutes while code is work-in-progress
10. **Test locally before marking ready:** Run both test suites locally before converting draft to ready
11. **Expect both test suites to run:** PRs always run full validation regardless of changed files
12. **Don't rely on path filtering:** Code changes can have cross-component impacts

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
- [GitHub Actions Contexts](https://docs.github.com/en/actions/learn-github-actions/contexts) (for draft PR detection)
- [Codecov Documentation](https://docs.codecov.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
