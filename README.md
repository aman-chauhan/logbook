# Logbook

[![Tests](https://github.com/aman-chauhan/logbook/actions/workflows/test.yml/badge.svg)](https://github.com/aman-chauhan/logbook/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/aman-chauhan/logbook/branch/main/graph/badge.svg)](https://codecov.io/gh/aman-chauhan/logbook)

A lightweight REST API for social journaling built with Flask and SQLite. Logbook provides a clean, educational codebase demonstrating core API design patterns and CRUD operations.

## Overview

Logbook is an educational platform that implements essential social media features through a simple REST API. Users (called "Scribes") can create accounts, write entries, and manage their content with public/private visibility controls.

This project prioritizes code clarity and serves as a reference implementation for learning Flask, SQLAlchemy, and REST API design.

## Features

- User management (registration, authentication, profile updates)
- Create, read, update, delete text entries
- Public/private visibility controls
- Chronological entry feeds
- HTTP Basic Authentication
- UUID-based resource IDs for better security and scalability

## Tech Stack

- **Backend**: Flask 3.x (Python 3.12)
- **Database**: SQLite with SQLAlchemy ORM
- **Migrations**: Flask-Migrate
- **Auth**: HTTP Basic Auth (Werkzeug)
- **Frontend**: SvelteKit 2.x with TypeScript
- **Process Manager**: Honcho

## Web Client

Logbook includes a SvelteKit-based web interface that provides a user-friendly UI for all API features.

### Features

- **Enlist**: Register as a new Scribe
- **Unlock/Lock**: Authenticate and secure your logbook
- **Profile Management**: View, amend, and retire your account
- **Entry Management**: Create, read, update, and delete entries
- **Chronicle**: View your documented journey

### Prerequisites

- Node.js 18+
- Logbook API server running on port 5000

### Running the Web Client

The web client is started automatically with Honcho alongside the API server:

```bash
honcho start
```

This starts:
- **api**: Flask API server on port 5000
- **web**: SvelteKit dev server on port 5173

Access the web interface at `http://localhost:5173`

### Running Separately

To run the web client independently:

```bash
cd webserver
npm install
npm run dev
```

### Building for Production

```bash
cd webserver
npm run build
npm run preview
```

For production deployment, configure an appropriate [SvelteKit adapter](https://svelte.dev/docs/kit/adapters).

See [webserver/README.md](webserver/README.md) for detailed web client documentation.

## Quick Start

**Prerequisites**: Python 3.12+, Node.js 18+ (for web client)

```bash
# 1. Clone and navigate to directory
git clone <repository-url>
cd logbook

# 2. Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
cd webserver && npm install && cd ..

# 4. Configure environment
cp .env.example .env
# Edit .env and set SECRET_KEY to a strong random value
# Note: FLASK_APP is already configured in .env.example

# 5. Start both servers (database already initialized)
honcho start
```

- **API**: `http://localhost:5000`
- **Web Client**: `http://localhost:5173`

**Note**: Database models and migrations are already set up. The database will be created automatically when you first start the server.

### Quick Test

```bash
# Check API health
curl http://localhost:5000/health
# Returns: {"data": {"type": "health-status", "id": "1", "attributes": {"status": "healthy"}}}

# Check API info
curl http://localhost:5000/
# Returns: {"data": {"type": "api-info", "id": "1", "attributes": {"message": "Logbook API", "version": "1.0.0", "endpoints": "/api"}}}
```

**Note**: All core features are implemented! Authentication, user profile, and entry endpoints are fully functional.

## Project Structure

```
logbook/
├── apiserver/             # Flask API server
│   ├── __init__.py        # Package initialization ✓
│   ├── extensions.py      # Flask extensions (db, migrate) ✓
│   ├── models.py          # Database models (Scribe, Entry) ✓
│   ├── run.py             # Application entry point ✓
│   ├── auth.py            # Auth decorators (@require_auth, @optional_auth) ✓
│   └── api/               # API endpoints
│       ├── __init__.py    # API blueprint registration ✓
│       ├── auth.py        # Registration/login ✓
│       ├── users.py       # User management ✓
│       └── posts.py       # Entry management ✓
├── webserver/             # SvelteKit web client ✓
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api.ts     # API client for backend ✓
│   │   │   └── stores/    # Svelte stores ✓
│   │   └── routes/        # Page components ✓
│   ├── package.json       # Node.js dependencies ✓
│   └── vite.config.ts     # Vite configuration ✓
├── tests/                 # Test suite ✓
│   ├── conftest.py        # Shared fixtures ✓
│   ├── unit/              # Unit tests ✓
│   ├── integration/       # Integration tests ✓
│   └── README.md          # Test documentation ✓
├── instance/              # Instance folder
│   └── logbook.db         # SQLite database ✓
├── migrations/            # Database migrations ✓
│   └── versions/          # Migration scripts ✓
├── venv/                  # Virtual environment
├── requirements.txt       # Python dependencies ✓
├── pytest.ini             # Pytest configuration ✓
├── Procfile               # Honcho configuration ✓
├── .env                   # Environment variables ✓
└── README.md              # This file
```

**Current Status**:
- ✓ Database models created with UUID primary keys and salt-based password hashing
- ✓ Explicit `__init__` methods for improved clarity and IDE compatibility
- ✓ Database initialized with migrations applied
- ✓ Basic Flask application with health check endpoints
- ✓ Authentication decorators implemented (@require_auth, @optional_auth)
- ✓ Authentication endpoints (POST /api/auth/enlist, /unlock, /lock)
- ✓ User profile endpoints (GET, PATCH, DELETE /api/scribes/:id)
- ✓ Entry endpoints (POST, GET, PATCH, DELETE /api/entries, GET /api/chronicle)
- ✓ SvelteKit web client with full UI implementation
- ✓ Comprehensive test suite with unit and integration tests (97% coverage)

## API Documentation

All endpoints are fully implemented and tested.

All endpoints follow the **JSON:API v1.1 specification**:
- Success responses (200, 201): `{"data": {"type": "...", "id": "...", "attributes": {...}}}`
- Error responses (4xx, 5xx): `{"errors": [{"status": "...", "title": "...", "detail": "..."}]}`
- Delete operations (204): Empty response body
- **HTTP status codes indicate success/failure** - always check the status code first!

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/enlist` | None | Register new user |
| POST | `/api/auth/unlock` | Basic | Verify credentials |
| POST | `/api/auth/lock` | Basic | Logout |

**Register Example:**
```bash
curl -X POST http://localhost:5000/api/auth/enlist \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.api+json" \
  -d '{"username": "john", "email": "john@example.com", "password": "pass123"}'

# Response (201 Created):
# {
#   "data": {
#     "type": "scribes",
#     "id": "1",
#     "attributes": {
#       "username": "john",
#       "email": "john@example.com",
#       "bio": null,
#       "createdAt": "2025-01-15T10:30:00Z"
#     }
#   }
# }
```

### Users (Scribes)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/scribes/:id` | None | Get user profile |
| PATCH | `/api/scribes/:id` | Basic | Update own profile |
| DELETE | `/api/scribes/:id` | Basic | Delete own account |

### Entries (Posts)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/entries` | Basic | Create entry |
| GET | `/api/entries/:id` | Optional* | Get single entry |
| PATCH | `/api/entries/:id` | Basic | Update own entry |
| DELETE | `/api/entries/:id` | Basic | Delete own entry |
| GET | `/api/chronicle` | Basic | Get user's entries |

*Auth required to view private entries

**Note:** PATCH is used for partial updates following JSON:API convention

**Create Entry:**
```bash
curl -X POST http://localhost:5000/api/entries \
  -u john:pass123 \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.api+json" \
  -d '{"content": "My first entry", "visibility": "public"}'

# Response (201 Created):
# {
#   "data": {
#     "type": "entries",
#     "id": "1",
#     "attributes": {
#       "content": "My first entry",
#       "visibility": "public",
#       "createdAt": "2025-01-15T10:30:00Z",
#       "updatedAt": "2025-01-15T10:30:00Z",
#       "scribeId": 1,
#       "scribeUsername": "john"
#     }
#   }
# }
```

## Development

### Running the Server

```bash
honcho start          # Recommended method
flask run            # Alternative (uses FLASK_DEBUG from .env)
```

Debug mode is controlled by the `FLASK_DEBUG` environment variable in `.env`:
- `FLASK_DEBUG=1` enables auto-reload, debugger, and detailed errors
- `FLASK_DEBUG=0` disables debug features (use in production)

### Database Migrations

```bash
flask db migrate -m "description"    # Create migration
flask db upgrade                     # Apply migrations
flask db downgrade                   # Revert migration
```

**Note**: Models use UUID primary keys for better security and scalability. They also include explicit `__init__` methods for clarity and IDE compatibility, plus `TYPE_CHECKING` for backref type hints to prevent circular dependency warnings. See [models.py](apiserver/models.py) for implementation details.

### Code Formatting

```bash
black .              # Format all files
black --check .      # Check without formatting
```

### Testing

The project includes a comprehensive test suite with unit and integration tests achieving **97% code coverage**.

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=apiserver --cov-report=term-missing

# Run specific test categories
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests only
pytest tests/unit/test_models.py  # Specific test file
```

**Test Features:**
- ✓ Unit tests for models, authentication, and API endpoints
- ✓ Integration tests for complete user workflows
- ✓ Faker library for realistic test data generation
- ✓ SQLite foreign key constraints enforced in tests
- ✓ Factory fixtures for easy test data creation

For detailed testing documentation, test writing guidelines, and best practices, see **[tests/README.md](tests/README.md)**.

## Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and configure these variables:

```bash
# Flask CLI and debug mode
FLASK_APP=apiserver/run.py
FLASK_DEBUG=1                              # Set to 0 in production

# Security (CHANGE THIS!)
SECRET_KEY=your-secret-key-change-this

# Database
SQLALCHEMY_DATABASE_URI=sqlite:///logbook.db

# Testing (optional)
# TESTING=true
```

**Important:**
- Change `SECRET_KEY` to a strong random value
- `.env` is for development only - never commit to git
- Production environments should set these via hosting platform

### Production Deployment

**Do not use `.env` files in production.** Instead, set environment variables through your hosting platform:

```bash
# Heroku example
heroku config:set FLASK_DEBUG=0
heroku config:set SECRET_KEY=<strong-random-key>

# Docker example
docker run -e FLASK_DEBUG=0 -e SECRET_KEY=xxx ...
```

See [CLAUDE.md](CLAUDE.md#production-deployment) for detailed production deployment guidance.

## Contributing

Contributions welcome! Please:

- Follow existing code style (use Black formatter)
- Write clear commit messages
- Update documentation for API changes
- Add docstrings to new functions

## Terminology

Logbook uses intentional terminology:

- **Scribe** = User
- **Enlist** = Register
- **Entry** = Post
- **Chronicle** = Feed
- **Unlock/Lock** = Login/Logout

## License

Apache License 2.0
