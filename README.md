# Logbook

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

## Tech Stack

- **Backend**: Flask 3.x (Python 3.12)
- **Database**: SQLite with SQLAlchemy ORM
- **Migrations**: Flask-Migrate
- **Auth**: HTTP Basic Auth (Werkzeug)
- **Process Manager**: Honcho

## Quick Start

**Prerequisites**: Python 3.12+

```bash
# 1. Clone and navigate to directory
git clone <repository-url>
cd logbook

# 2. Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and set SECRET_KEY to a strong random value
# Note: FLASK_APP is already configured in .env.example

# 5. Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 6. Start the server
honcho start
```

The API will be available at `http://localhost:5000`

### Quick Test

```bash
# Register a user
curl -X POST http://localhost:5000/api/auth/enlist \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "pass123"}'

# Create an entry
curl -X POST http://localhost:5000/api/entries \
  -u john:pass123 \
  -H "Content-Type: application/json" \
  -d '{"content": "My first entry"}'
```

## Project Structure

```
logbook/
├── apiserver/             # Application package (future)
│   ├── __init__.py        # Application factory
│   ├── models.py          # Database models
│   ├── auth.py            # Auth decorators
│   ├── api/               # API endpoints
│   │   ├── auth.py        # Registration/login
│   │   ├── users.py       # User management
│   │   └── posts.py       # Entry management
│   └── run.py             # Entry point with configuration
├── migrations/            # Database migrations
└── requirements.txt       # Dependencies
```

## API Documentation

All endpoints return JSON with format: `{"success": true/false, "data": {...}}` or `{"success": false, "error": "message"}`

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
  -d '{"username": "john", "email": "john@example.com", "password": "pass123"}'
```

### Users (Scribes)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/scribes/:id` | None | Get user profile |
| PUT | `/api/scribes/:id` | Basic | Update own profile |
| DELETE | `/api/scribes/:id` | Basic | Delete own account |

### Entries (Posts)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/entries` | Basic | Create entry |
| GET | `/api/entries/:id` | Optional* | Get single entry |
| PUT | `/api/entries/:id` | Basic | Update own entry |
| DELETE | `/api/entries/:id` | Basic | Delete own entry |
| GET | `/api/chronicle` | Basic | Get user's entries |

*Auth required to view private entries

**Create Entry:**
```bash
curl -X POST http://localhost:5000/api/entries \
  -u john:pass123 \
  -H "Content-Type: application/json" \
  -d '{"content": "My entry", "visibility": "public"}'
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

### Code Formatting

```bash
black .              # Format all files
black --check .      # Check without formatting
```

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
