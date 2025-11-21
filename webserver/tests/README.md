# Webserver Unit Tests

This directory contains unit tests for the Logbook webserver, built with Vitest.

## Overview

The test suite provides comprehensive coverage for the webserver's TypeScript modules:

- **API Client** (`src/lib/api.ts`): Tests for all API endpoint functions with mocked fetch responses
- **Auth Store** (`src/lib/stores/auth.ts`): Tests for authentication state management and localStorage integration

## Test Coverage

Current coverage statistics:

```
File        | % Stmts | % Branch | % Funcs | % Lines
------------|---------|----------|---------|--------
All files   |   94.73 |    73.91 |     100 |   94.73
 api.ts     |     100 |      100 |     100 |     100
 auth.ts    |    90.9 |    57.14 |     100 |    90.9
```

## Running Tests

```bash
# Run tests in watch mode (interactive)
npm test

# Run tests once (CI mode)
npm run test:run

# Run tests with coverage report
npm run test:coverage

# Run tests with UI interface
npm run test:ui
```

## Test Structure

### API Client Tests (`src/lib/api.test.ts`)

Tests all API endpoint functions using mocked fetch responses:

- **Authentication Endpoints**: `enlist()`, `unlock()`, `lock()`
- **Scribe Endpoints**: `getScribe()`, `amendScribe()`, `retireScribe()`
- **Entry Endpoints**: `createEntry()`, `getEntry()`, `updateEntry()`, `deleteEntry()`, `getChronicle()`
- **Error Handling**: Validates error responses and edge cases
- **Basic Auth**: Verifies proper Authorization header creation

**Key Features:**
- Mocks global `fetch` for isolated testing
- Tests both success and error responses
- Validates JSON:API response format
- Verifies HTTP headers and request bodies

### Auth Store Tests (`src/lib/stores/auth.test.ts`)

Tests authentication state management and persistence:

- **Login/Logout**: State changes and localStorage persistence
- **Update Operations**: `updateScribe()`, `updatePassword()`
- **Credentials Access**: `getCredentials()` method
- **Store Subscriptions**: Reactive state updates
- **Error Handling**: Invalid localStorage data

**Key Features:**
- Mocks browser environment and localStorage
- Tests Svelte store behavior with `get()` and `subscribe()`
- Validates state persistence across operations
- Ensures proper cleanup on logout

## Configuration

Tests are configured in `vite.config.ts`:

```typescript
test: {
  globals: true,
  environment: 'jsdom',
  include: ['src/**/*.{test,spec}.{js,ts}'],
  coverage: {
    provider: 'v8',
    reporter: ['text', 'json', 'html'],
    include: ['src/lib/**/*.{js,ts}'],
    exclude: ['src/lib/index.ts', '**/*.d.ts', '**/*.config.*']
  }
}
```

## Coverage Reports

Coverage reports are generated in multiple formats:

- **Terminal**: Displayed after running `npm run test:coverage`
- **HTML**: Browse detailed coverage at `webserver/coverage/index.html`
- **JSON**: Machine-readable format at `webserver/coverage/coverage-final.json`

## Best Practices

When writing new tests:

1. **Use descriptive test names**: Clearly state what is being tested
2. **Mock external dependencies**: Use `vi.mock()` for browser APIs and modules
3. **Test both success and failure cases**: Include error handling tests
4. **Clear state between tests**: Use `beforeEach()` to reset mocks and state
5. **Follow AAA pattern**: Arrange, Act, Assert

## Adding New Tests

To add tests for a new module:

1. Create `[module-name].test.ts` next to the module file
2. Import test utilities: `import { describe, it, expect, beforeEach, vi } from 'vitest'`
3. Mock any external dependencies (fetch, localStorage, $app/environment, etc.)
4. Write tests following existing patterns
5. Run `npm run test:coverage` to verify coverage

## Dependencies

Testing stack:

- **Vitest**: Fast unit test framework powered by Vite
- **@vitest/ui**: Interactive UI for test results
- **@vitest/coverage-v8**: Code coverage using V8's built-in coverage
- **@testing-library/svelte**: Utilities for testing Svelte components
- **jsdom**: Browser environment simulation
- **happy-dom**: Lightweight DOM implementation (alternative to jsdom)

## Integration with CI/CD

The test suite is designed to integrate with CI/CD pipelines:

```bash
# CI mode (exits with error code on failure)
npm run test:run

# Generate coverage for reporting
npm run test:coverage
```

Coverage reports can be uploaded to services like Codecov or Coveralls for tracking over time.
