# Logbook API Test Suite

Comprehensive test suite for the Logbook API server using pytest.

## Overview

This test suite provides comprehensive coverage of the Logbook API implementation, including:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test multiple components working together (structure ready for future development)
- **Code Coverage**: Track test coverage with pytest-cov
- **Fixtures**: Reusable test data and configuration

## Project Structure

```
tests/
├── __init__.py           # Test package initialization
├── conftest.py           # Shared pytest fixtures
├── README.md             # This file
├── unit/                 # Unit tests
│   ├── __init__.py
│   ├── test_models.py           # Database models tests
│   ├── test_auth.py             # Auth decorators tests
│   ├── test_auth_endpoints.py  # Auth endpoint tests
│   └── test_app.py              # Application factory tests
└── integration/          # Integration tests (ready for future development)
    └── __init__.py
```

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install -r requirements.txt
```

This will install:
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-flask` - Flask testing utilities

### Run All Tests

```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Run with extra verbose output showing all test names
pytest -vv
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests (when implemented)
pytest -m integration

# Run tests in a specific file
pytest tests/unit/test_models.py

# Run a specific test class
pytest tests/unit/test_models.py::TestScribeModel

# Run a specific test function
pytest tests/unit/test_models.py::TestScribeModel::test_scribe_creation
```

### Coverage Reports

```bash
# Generate coverage report in terminal
pytest --cov=apiserver --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=apiserver --cov-report=html

# View HTML report (opens in browser)
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Test Organization

### Unit Tests

Unit tests focus on testing individual components in isolation:

#### `test_models.py` - Database Models
- Scribe model creation and validation
- Entry model creation and validation
- Password hashing and verification
- JSON:API serialization
- Model relationships and cascading deletes
- Database constraints

#### `test_auth.py` - Authentication Decorators
- `@require_auth` decorator behavior
- `@optional_auth` decorator behavior
- HTTP Basic Auth handling
- Error response formats
- Function metadata preservation

#### `test_auth_endpoints.py` - Authentication Endpoints
- `POST /api/auth/enlist` (registration)
- `POST /api/auth/unlock` (login)
- `POST /api/auth/lock` (logout)
- Input validation
- Error handling
- JSON:API response format

#### `test_app.py` - Application Factory
- Application creation and configuration
- Extension initialization
- Blueprint registration
- Root endpoints (`/`, `/health`)
- Shell context processor
- Database initialization

### Integration Tests

The `tests/integration/` directory is ready for future integration tests that will test:
- End-to-end API flows
- Complex authentication scenarios
- Database transaction handling
- Multi-user interactions
- Performance testing

## Shared Fixtures

Located in `tests/conftest.py`, these fixtures are available to all tests:

### Application Fixtures

- **`app`**: Flask application instance configured for testing
  - Uses in-memory SQLite database
  - Fresh instance for each test
  - Automatic cleanup after test

- **`client`**: Flask test client for making HTTP requests
  - Pre-configured with test app
  - Supports all HTTP methods

- **`db`**: SQLAlchemy database instance
  - Connected to test database
  - Automatic table creation/cleanup

### Data Fixtures

- **`sample_scribe`**: Pre-created test user
  - Username: `testuser`
  - Email: `test@example.com`
  - Password: `testpass123`

- **`sample_entry`**: Pre-created test entry
  - Content: Randomly generated text (using Faker)
  - Visibility: public
  - Belongs to `sample_scribe`

- **`auth_headers`**: HTTP Basic Auth headers for `sample_scribe`
  - Ready to use in request headers

### Using Fixtures

```python
def test_example(client, sample_scribe):
    """Example test using fixtures."""
    response = client.get(f"/api/scribes/{sample_scribe.id}")
    assert response.status_code == 200
```

## Writing New Tests

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Test Markers

Mark tests with appropriate markers:

```python
@pytest.mark.unit
def test_something():
    """Unit test example."""
    pass

@pytest.mark.integration
def test_something_integrated():
    """Integration test example."""
    pass

@pytest.mark.slow
def test_something_slow():
    """Slow test that takes time."""
    pass
```

### Example Unit Test

```python
import pytest
from apiserver.models import Scribe

class TestNewFeature:
    """Test suite for new feature."""

    @pytest.mark.unit
    def test_feature_success(self, client, db):
        """Test successful feature usage."""
        # Arrange
        scribe = Scribe(username="test", email="test@example.com")
        scribe.set_password("pass123")
        db.session.add(scribe)
        db.session.commit()

        # Act
        response = client.get("/api/new-feature")

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    @pytest.mark.unit
    def test_feature_validation_error(self, client):
        """Test feature with invalid input."""
        response = client.post("/api/new-feature", json={})
        assert response.status_code == 400
```

### Example Integration Test

```python
@pytest.mark.integration
def test_complete_workflow(client, db):
    """Test complete user workflow."""
    # Register
    response = client.post("/api/auth/enlist", json={
        "username": "workflow",
        "email": "workflow@example.com",
        "password": "pass123"
    })
    assert response.status_code == 201

    # Login
    import base64
    creds = base64.b64encode(b"workflow:pass123").decode("utf-8")
    response = client.post("/api/auth/unlock",
        headers={"Authorization": f"Basic {creds}"})
    assert response.status_code == 200

    # Create entry (future endpoint)
    # response = client.post("/api/entries", ...)
```

## Configuration

Test configuration is in `pytest.ini`:

```ini
[pytest]
# Test discovery patterns
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Test paths
testpaths = tests

# Output and coverage options
addopts =
    -v                      # Verbose output
    --strict-markers        # Ensure markers are defined
    --tb=short             # Short traceback format
    --cov=apiserver        # Coverage for apiserver package
    --cov-report=term-missing  # Show missing lines
    --cov-report=html      # Generate HTML report
    --cov-branch           # Branch coverage

# Test markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

## Best Practices

### 1. Test Isolation

Each test should be independent and not rely on other tests:

```python
# Good: Each test is independent
def test_create_scribe(db):
    scribe = Scribe(username="test", email="test@example.com")
    db.session.add(scribe)
    db.session.commit()
    assert scribe.id is not None

def test_scribe_password(db):
    scribe = Scribe(username="test2", email="test2@example.com")
    scribe.set_password("pass")
    assert scribe.check_password("pass")

# Bad: Second test depends on first test
def test_create_scribe(db):
    scribe = Scribe(username="shared", email="shared@example.com")
    db.session.add(scribe)
    db.session.commit()

def test_scribe_exists(db):
    scribe = Scribe.query.filter_by(username="shared").first()
    assert scribe is not None  # Depends on previous test!
```

### 2. Use Fixtures for Setup

Use fixtures instead of setup/teardown:

```python
# Good: Use fixtures
@pytest.fixture
def authenticated_user(client, db):
    scribe = Scribe(username="auth", email="auth@example.com")
    scribe.set_password("pass")
    db.session.add(scribe)
    db.session.commit()
    return scribe

def test_with_auth_user(authenticated_user):
    assert authenticated_user.username == "auth"
```

### 3. Test Both Success and Failure Cases

```python
def test_login_success(client, sample_scribe):
    """Test successful login."""
    # Test success case
    pass

def test_login_invalid_password(client, sample_scribe):
    """Test login with wrong password."""
    # Test failure case
    pass

def test_login_missing_credentials(client):
    """Test login without credentials."""
    # Test edge case
    pass
```

### 4. Use Descriptive Test Names

```python
# Good: Descriptive names
def test_scribe_creation_with_valid_data(db):
    pass

def test_scribe_creation_fails_with_duplicate_username(db):
    pass

# Bad: Vague names
def test_scribe(db):
    pass

def test_error(db):
    pass
```

### 5. Follow AAA Pattern

Structure tests with Arrange, Act, Assert:

```python
def test_password_hashing(db):
    # Arrange
    scribe = Scribe(username="test", email="test@example.com")
    password = "securepass123"

    # Act
    scribe.set_password(password)

    # Assert
    assert scribe.password_hash is not None
    assert scribe.password_hash != password
    assert scribe.check_password(password)
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --cov=apiserver --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Tests fail with "No module named 'apiserver'"

Make sure you're running pytest from the project root:

```bash
cd /path/to/logbook
pytest
```

### Database errors in tests

The test suite uses an in-memory SQLite database. If you see database errors:

1. Check that fixtures are being used correctly
2. Ensure `TESTING=true` environment is set (done automatically by fixtures)
3. Verify database schema matches models

### Import errors

If you get import errors, ensure:

1. All `__init__.py` files exist
2. You're in the correct virtual environment
3. Dependencies are installed: `pip install -r requirements.txt`

## Coverage Goals

Current coverage targets:

- **Overall**: 90%+ coverage
- **Models**: 95%+ coverage
- **API endpoints**: 90%+ coverage
- **Authentication**: 95%+ coverage

View current coverage:

```bash
pytest --cov=apiserver --cov-report=term-missing
```

## Future Enhancements

The test infrastructure is ready for:

1. **Integration Tests**: Full workflow testing
2. **Performance Tests**: Load and stress testing
3. **API Contract Tests**: JSON:API specification compliance
4. **Security Tests**: Authentication and authorization edge cases
5. **Database Tests**: Migration testing, data integrity

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass: `pytest`
3. Maintain coverage above 90%: `pytest --cov`
4. Add integration tests for complex features
5. Update this README if adding new test categories

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-flask documentation](https://pytest-flask.readthedocs.io/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [JSON:API specification](https://jsonapi.org/)
