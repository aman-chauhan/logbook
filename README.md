# Logbook

**Document Your World.**

A thoughtful REST API for chronicling your journey.

## Brand Identity

### Core Concept: Documenting the Journey

Life is a journey to be recorded and shared with a trusted circle of intellectual peers.

**Tone**: Thoughtful, Purposeful, and Personal. Encouraging depth over fleeting interaction.

**Aesthetic**: Minimalist, Clean, and Hierarchical. Evoking the feel of a vintage journal, an explorer's log, or an architectural blueprint.

### The Chronicle of the Scribe

In a world of fleeting moments, Logbook is your dedicated space for purposeful record-keeping.

You are a **Scribe**—an individual committed to observing, documenting, and sharing their unique perspective. When you **Enlist**, you are provided with a digital ledger, your personal Logbook. To begin your daily work, you simply **Unlock** your tools.

Your shared history and daily observations form your **Chronicle**. Each new thought is an **Entry**—a purposeful record, not just a casual post.

As you engage with others, you acknowledge their insights with a **Mark**, a deliberate and non-trivial endorsement. Your full appreciation is reserved for those whose work you actively **Track**, integrating their journey with your own Chronicle. When a moment or thought prompts a response, you leave an **Annotation**, adding a layer of scholarly depth to the original Entry.

Logbook is not a river of noise; it is a library of shared experiences. Here, your digital life has depth, your connections have meaning, and every action is a conscious step in the Chronicle of your personal journey. Your profile is not a static page, but a living document you can thoughtfully **Amend** as you grow.

## Project Overview

Logbook is a lightweight REST API built with Flask that demonstrates core social media functionality with a focus on meaningful content. The project serves as an educational reference implementation with clean, well-documented code and straightforward architecture.

### Features (v1.0)

- **Scribe Management**: Enlist, unlock, lock, view/amend/retire profile
- **Entries**: Create, update, delete entries with public/private visibility
- **Chronicle**: View scribe's own entries in chronological order
- **Authentication**: HTTP Basic Auth
- **Simple, clean API architecture**

**Future Features** (not yet implemented):
- Track/untrack functionality (follow/unfollow)
- Marks and annotations (likes and comments)
- Chronicle from tracked scribes
- JWT token authentication

**Note**: This platform focuses on text-based content exclusively - no images, videos, or other media types.

## Technology Stack

- **Backend Framework**: Flask (Python 3.12)
- **Database**: SQLite (file-based, zero-config database)
- **ORM**: SQLAlchemy + Flask-SQLAlchemy
- **Migrations**: Flask-Migrate (Alembic-based)
- **Process Manager**: Honcho (Procfile-based process management)
- **Authentication**: HTTP Basic Auth (Werkzeug)
- **Development Environment**: Python 3.12 with devcontainer support

## Quick Start

### Prerequisites

- Python 3.12 or higher

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd logbook
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and update SECRET_KEY for production use
   ```

5. **Set Flask application**
   ```bash
   export FLASK_APP=run.py
   ```

6. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

7. **Run the application**
   ```bash
   honcho start
   ```

   The API will be available at `http://localhost:5000`

8. **Test the API**
   You can test endpoints using curl, httpie, Postman, or any REST client:
   ```bash
   # Enlist a new scribe
   curl -X POST http://localhost:5000/api/auth/enlist \
     -H "Content-Type: application/json" \
     -d '{"username": "john", "email": "john@example.com", "password": "password123"}'

   # Unlock (verify credentials)
   curl -X POST http://localhost:5000/api/auth/unlock \
     -u john:password123

   # Create an entry
   curl -X POST http://localhost:5000/api/entries \
     -u john:password123 \
     -H "Content-Type: application/json" \
     -d '{"content": "Hello world!", "visibility": "public"}'

   # Get your chronicle
   curl -X GET http://localhost:5000/api/chronicle \
     -u john:password123
   ```

## Project Structure

```
logbook/
├── app/                    # Main application package
│   ├── __init__.py        # Application factory
│   ├── models.py          # Database models (Scribe, Entry)
│   ├── auth.py            # Authentication utilities
│   └── api/               # API endpoints
│       ├── __init__.py    # API blueprint registration
│       ├── auth.py        # Auth endpoints (enlist, unlock, lock)
│       ├── users.py       # Scribe endpoints (CRUD operations)
│       └── posts.py       # Entry endpoints (CRUD + chronicle)
├── migrations/            # Database migration scripts (auto-generated)
├── venv/                  # Virtual environment (not in git)
├── config.py              # Configuration management
├── run.py                 # Application entry point
├── requirements.txt       # Python dependencies
├── Procfile               # Honcho process definition
├── .env.example           # Environment variables template
├── .env                   # Environment variables (not in git)
├── .gitignore             # Git ignore rules
├── CLAUDE.md              # Claude Code project guidance
├── LICENSE                # Apache License 2.0
└── README.md              # This file
```

## Architecture

The application is a REST API structured as a modular monolith:

- **Single API blueprint** with modular route files for different resources
- **Database models** centralized in `models.py` with `to_dict()` serialization methods
- **Configuration** managed through environment variables and config classes
- **Business logic** in models (e.g., password hashing) and utility functions
- **Authentication** via HTTP Basic Auth with decorator-based protection
- **Consistent JSON responses** with `{"success": true/false, "data/error": ...}` format

The codebase follows clean code principles with clear naming, small focused functions, and comprehensive documentation.

## API Endpoints

All endpoints are prefixed with `/api` and return JSON responses in a consistent format:

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message description"
}
```

### Authentication Endpoints

#### Enlist (Register)
- **POST** `/api/auth/enlist`
- **Body**: `{"username": "string", "email": "string", "password": "string", "bio": "string (optional)"}`
- **Response (201)**:
  ```json
  {
    "success": true,
    "data": {
      "id": 1,
      "username": "john",
      "email": "john@example.com",
      "bio": null,
      "created_at": "2025-11-11T22:00:00"
    }
  }
  ```
- **Errors**: 400 (missing fields), 409 (username/email exists)

#### Unlock (Login)
- **POST** `/api/auth/unlock`
- **Auth**: HTTP Basic Auth (username, password)
- **Response (200)**: Same as enlist response
- **Errors**: 401 (invalid credentials)

#### Lock (Logout)
- **POST** `/api/auth/lock`
- **Auth**: HTTP Basic Auth required
- **Response (200)**: `{"success": true, "data": {"message": "Logbook locked successfully"}}`
- **Errors**: 401 (not authenticated)

### Scribe Endpoints

#### Get Scribe Profile
- **GET** `/api/scribes/<scribe_id>`
- **Auth**: Optional (public endpoint)
- **Response (200)**: Scribe object (same format as enlist)
- **Errors**: 404 (scribe not found)

#### Amend Scribe Profile (Update)
- **PUT** `/api/scribes/<scribe_id>`
- **Auth**: HTTP Basic Auth required (must be own profile)
- **Body**: `{"email": "string (optional)", "bio": "string (optional)"}`
- **Response (200)**: Updated scribe object
- **Errors**: 400 (invalid data), 403 (not authorized), 404 (scribe not found), 409 (email in use)

#### Retire Scribe Account (Delete)
- **DELETE** `/api/scribes/<scribe_id>`
- **Auth**: HTTP Basic Auth required (must be own profile)
- **Response (200)**: `{"success": true, "data": {"message": "Scribe retired successfully"}}`
- **Errors**: 403 (not authorized), 404 (scribe not found)
- **Note**: Retiring a scribe also deletes all their entries (cascade delete)

### Entry Endpoints

#### Create Entry
- **POST** `/api/entries`
- **Auth**: HTTP Basic Auth required
- **Body**: `{"content": "string", "visibility": "public|private (default: public)"}`
- **Response (201)**:
  ```json
  {
    "success": true,
    "data": {
      "id": 1,
      "content": "Hello world!",
      "visibility": "public",
      "created_at": "2025-11-11T22:00:00",
      "updated_at": "2025-11-11T22:00:00",
      "scribe_id": 1,
      "scribe": "john"
    }
  }
  ```
- **Errors**: 400 (missing/invalid content), 401 (not authenticated)

#### Get Entry
- **GET** `/api/entries/<entry_id>`
- **Auth**: Optional (required only for viewing private entries)
- **Response (200)**: Entry object (same format as create)
- **Errors**: 403 (unauthorized to view private entry), 404 (entry not found)

#### Update Entry
- **PUT** `/api/entries/<entry_id>`
- **Auth**: HTTP Basic Auth required (must be scribe)
- **Body**: `{"content": "string (optional)", "visibility": "public|private (optional)"}`
- **Response (200)**: Updated entry object
- **Errors**: 400 (invalid data), 403 (not authorized), 404 (entry not found)

#### Delete Entry
- **DELETE** `/api/entries/<entry_id>`
- **Auth**: HTTP Basic Auth required (must be scribe)
- **Response (200)**: `{"success": true, "data": {"message": "Entry deleted successfully"}}`
- **Errors**: 403 (not authorized), 404 (entry not found)

#### Get Chronicle
- **GET** `/api/chronicle`
- **Auth**: HTTP Basic Auth required
- **Description**: Returns all entries created by the authenticated scribe, ordered by creation date (newest first). The chronicle represents the scribe's documented journey.
- **Response (200)**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": 2,
        "content": "Second entry",
        "visibility": "private",
        "created_at": "2025-11-11T22:10:00",
        "updated_at": "2025-11-11T22:10:00",
        "scribe_id": 1,
        "scribe": "john"
      },
      {
        "id": 1,
        "content": "First entry",
        "visibility": "public",
        "created_at": "2025-11-11T22:00:00",
        "updated_at": "2025-11-11T22:00:00",
        "scribe_id": 1,
        "scribe": "john"
      }
    ]
  }
  ```
- **Errors**: 401 (not authenticated)

## Common Commands

### Running the Application

```bash
# Start all processes via Honcho (recommended)
honcho start

# Run Flask development server directly
flask run

# Run with debug mode enabled
flask --debug run
```

### Code Formatting

The project uses Black formatter for consistent code style:

```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .
```

### Database Management

```bash
# Initialize database migrations (first time only)
flask db init

# Create a new migration after model changes
flask db migrate -m "description of changes"

# Apply migrations to database
flask db upgrade

# Revert last migration (if needed)
flask db downgrade
```

> **Note**: This project uses Flask-Migrate to manage database schema changes safely. When you modify models in [models.py](app/models.py), create a migration to update the database structure without losing data.

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage report
pytest --cov=app tests/

# Run tests with verbose output
pytest -v
```

## Configuration

The application uses environment variables for configuration. A template is provided in [.env.example](.env.example).

### Environment Variables

Create a `.env` file in the project root (never commit this file):

```bash
# Flask configuration
FLASK_APP=run.py
FLASK_ENV=development

# Security - CHANGE THIS IN PRODUCTION
SECRET_KEY=your-secret-key-here

# Database
SQLALCHEMY_DATABASE_URI=sqlite:///logbook.db
```

### Configuration Classes

Configuration classes are defined in [config.py](config.py):

- **DevelopmentConfig**: Debug mode enabled, uses SQLite
- **ProductionConfig**: Debug mode disabled, requires SECRET_KEY environment variable
- **TestingConfig**: In-memory SQLite database for testing

Set the environment by changing `FLASK_ENV` or by passing the config name to `create_app()`.

## Security Considerations

This project demonstrates secure API coding practices:

- **Password hashing** using `werkzeug.security` (bcrypt-based)
- **HTTP Basic Auth** for simplicity (always use HTTPS in production)
- **Input validation** on all endpoints with proper error responses
- **SQL injection prevention** through SQLAlchemy's parameterized queries
- **Authorization checks** ensuring scribes can only modify their own resources
- **Environment-based secrets management** via `.env` file

**Production Recommendations:**
- Use HTTPS to protect credentials in transit
- Consider JWT tokens for stateless authentication
- Implement rate limiting to prevent abuse
- Add logging and monitoring
- Use a production database (PostgreSQL recommended)

## Development Workflow

### Adding New Features

1. **Plan the feature**: Consider data models, API endpoints, and request/response formats
2. **Update models** in [app/models.py](app/models.py) if database changes are needed
3. **Create migration**:
   ```bash
   flask db migrate -m "Add feature X"
   flask db upgrade
   ```
4. **Implement API endpoints** in the appropriate file in `app/api/`
5. **Test manually** using curl or Postman
6. **Format code**: `black .`
7. **Update documentation**: Update this README with new endpoints

### Using the Flask Shell

The Flask shell provides an interactive Python environment with database access:

```bash
flask shell

>>> # Access database and models
>>> Scribe.query.all()
[<Scribe john>, <Scribe jane>]

>>> # Create a scribe
>>> scribe = Scribe(username='test', email='test@example.com')
>>> scribe.set_password('password')
>>> db.session.add(scribe)
>>> db.session.commit()
```

## Terminology Reference

Logbook uses purposeful terminology to reflect the thoughtful nature of the platform:

| Common Term | Logbook Term | Description |
|------------|--------------|-------------|
| User | **Scribe** | An individual who documents their journey |
| Register | **Enlist** | Join Logbook as a new scribe |
| Log In | **Unlock** | Access your logbook |
| Log Out | **Lock** | Secure your logbook |
| Post | **Entry** | A purposeful record in your chronicle |
| Feed | **Chronicle** | Your documented journey over time |
| Update Profile | **Amend** | Thoughtfully revise your scribe profile |
| Delete Account | **Retire** | Close your logbook |
| Like | **Mark** | A deliberate endorsement (future) |
| Unlike | **Unmark** | Remove an endorsement (future) |
| Comment | **Annotation** | Scholarly response to an entry (future) |
| Follow | **Track** | Integrate another's journey with yours (future) |
| Unfollow | **Untrack** | Stop tracking another scribe (future) |

## Contributing

Contributions are welcome! Please ensure:

- Code is well-documented with clear docstrings
- New features include appropriate tests (when test framework is added)
- Documentation is updated when adding features or changing APIs
- Code follows the existing style (use Black formatter)
- Commit messages are clear and descriptive
- New features align with the thoughtful, purposeful brand identity

## License

Apache License 2.0
