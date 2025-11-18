# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Logbook is an educational REST API platform designed for computer science students. This project demonstrates core API design and social media functionality through clean, well-documented code that serves as a reference implementation. The codebase prioritizes **clarity over cleverness**, making every design decision favor ease of understanding.

### Brand Identity

Logbook uses purposeful terminology that reflects thoughtful, intentional interaction:

- **Scribe**: A user who documents their journey (not "user")
- **Entry**: A purposeful record in one's chronicle (not "post")
- **Chronicle**: The documented journey over time (not "feed")
- **Enlist**: Join Logbook as a new scribe (not "register")
- **Unlock**: Access your logbook (not "log in")
- **Lock**: Secure your logbook (not "log out")
- **Amend**: Thoughtfully revise your profile (not "update")
- **Retire**: Close your account (not "delete")

This terminology emphasizes depth, purpose, and meaningful engagement over fleeting interaction.

### Educational Goals

- Students with basic knowledge of Python, SQL, JSON, Flask, and Honcho should be able to read through the codebase and grasp how each component works
- Code should be straightforward enough to serve as a learning resource
- Documentation should get students running the project within minutes, not hours
- Treat code quality as you would for a reference implementation that will teach others

### Key Constraints

- **API-only**: JSON request/response format, no HTML templates or frontend
- **Text-based content only**: No images, videos, or other media types
- **Minimal tech stack**: Flask, SQLite, SQLAlchemy, Honcho only
- **Simple feature set**: Scribe management and entries with visibility controls (foundation for future expansion)
- **Basic Authentication**: HTTP Basic Auth for simplicity
- **Complete Honcho management**: All deployment and management through Honcho

### Current Feature Set (v1.0)

- **Scribe Management**: Enlist, unlock, lock, view/amend/retire profile
- **Entries**: Create, update, delete entries with public/private visibility
- **Chronicle**: View scribe's own entries in chronological order

**Future Features** (not yet implemented):
- Track/untrack functionality (follow/unfollow)
- Marks and annotations (likes and comments)
- Chronicle from tracked scribes
- Advanced authentication (JWT tokens)

## Technology Stack

- **Backend**: Flask (Python 3.12)
- **Database**: SQLite (file-based, zero-config)
- **ORM**: SQLAlchemy (database abstraction layer)
- **Flask-SQLAlchemy**: Flask integration for SQLAlchemy
- **Flask-Migrate**: Database migration support
- **Process Manager**: Honcho
- **Authentication**: HTTP Basic Auth (built into Werkzeug)
- **Development Environment**: Python 3.12 devcontainer

## Development Philosophy

When writing code for this project, follow these principles:

### 1. Clarity Over Cleverness
- Write code that is immediately understandable
- Avoid clever tricks, obscure patterns, or overly abstract solutions
- Use straightforward implementations even if they're slightly more verbose
- Favor explicit over implicit

### 2. CLEAN Code Principles
- **Clear naming**: Use descriptive, meaningful names for variables, functions, and classes
- **Small functions**: Each function should do one thing well
- **Minimal dependencies**: Keep components loosely coupled
- **Well-documented**: Include docstrings and comments where needed
- **DRY principle**: Don't Repeat Yourself, but don't over-abstract

### 3. Pragmatic Balance
- Use custom implementations where they provide learning value
- Use third-party packages only where they genuinely simplify development
- Document why you chose custom code vs. a library
- Keep dependencies minimal and well-justified

### 4. Educational Value
- Write code as if students will read it to learn
- Explain the "why" behind design decisions in comments
- Include examples in docstrings
- Document assumptions and trade-offs

## Development Setup

### Complete Setup Process
```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install dependencies (if not already installed)
pip install -r requirements.txt

# 3. Set up environment variables (if not already configured)
cp .env.example .env
# Edit .env and set SECRET_KEY to a strong random value
# Note: FLASK_APP and FLASK_DEBUG are already set in .env.example

# 4. Run the application (database already initialized)
honcho start
```

**Current Status**:
- ✓ Database models created (Scribe, Entry) with salt-based password hashing and explicit `__init__` methods
- ✓ Migrations initialized and applied
- ✓ SQLite database created at `instance/logbook.db`
- ✓ Authentication decorators implemented (@require_auth, @optional_auth)
- ✓ API blueprint setup with authentication endpoints (enlist, unlock, lock)
- TODO: Scribe profile endpoints (GET, PATCH, DELETE)
- TODO: Entry endpoints (POST, GET, PATCH, DELETE, chronicle)

### Code Formatting
The project uses Black formatter for consistent code style:
```bash
# Format all files
black .

# Check without formatting
black --check .
```

## Project Structure

```
logbook/
├── apiserver/            # Main application package
│   ├── __init__.py       # Package initialization ✓
│   ├── extensions.py     # Flask extensions (db, migrate) ✓
│   ├── models.py         # Database models (Scribe, Entry) ✓
│   ├── run.py            # Application entry point with configuration ✓
│   ├── auth.py           # Authentication utilities and decorators ✓
│   └── api/              # API endpoints
│       ├── __init__.py   # API blueprint registration ✓
│       ├── auth.py       # Auth endpoints (enlist, unlock, lock) ✓
│       ├── users.py      # Scribe endpoints (profile CRUD) (TODO)
│       └── posts.py      # Entry endpoints (CRUD, chronicle) (TODO)
├── instance/             # Instance folder (Flask-generated)
│   └── logbook.db        # SQLite database ✓
├── migrations/           # Database migration scripts ✓
│   ├── versions/         # Migration files ✓
│   ├── alembic.ini       # Alembic configuration ✓
│   └── env.py            # Migration environment ✓
├── venv/                 # Virtual environment (not in git)
├── requirements.txt      # Python dependencies
├── Procfile              # Honcho process definition
├── .env.example          # Environment variables template
├── .env                  # Environment variables (not in git)
├── .gitignore            # Git ignore rules
├── CLAUDE.md             # This file - guidance for Claude Code
├── LICENSE               # Apache License 2.0
└── README.md             # Project documentation
```

**Key Files:**
- **[apiserver/run.py](apiserver/run.py)**: Application entry point with configuration ✓
- **[apiserver/extensions.py](apiserver/extensions.py)**: Flask-SQLAlchemy and Flask-Migrate instances ✓
- **[apiserver/models.py](apiserver/models.py)**: Scribe and Entry models with explicit `__init__` methods ✓
- **[apiserver/auth.py](apiserver/auth.py)**: `@require_auth` and `@optional_auth` decorators ✓
- **[apiserver/api/auth.py](apiserver/api/auth.py)**: Authentication endpoints (enlist, unlock, lock) ✓
- **[apiserver/api/users.py](apiserver/api/users.py)**: Scribe profile endpoints (TODO)
- **[apiserver/api/posts.py](apiserver/api/posts.py)**: Entry endpoints (TODO)

## Common Commands

### Running the Application
Use Honcho to manage all processes:
```bash
# Via Honcho (primary method)
honcho start

# Direct Flask development server (alternative)
flask run

# Note: Debug mode is controlled by FLASK_DEBUG in .env
# Set FLASK_DEBUG=1 for development (enables auto-reload, debugger)
# Set FLASK_DEBUG=0 for production
```

### Database Management
```bash
# Initialize migrations
flask db init

# Create migration after model changes
flask db migrate -m "description"

# Apply migrations
flask db upgrade

# Revert migration
flask db downgrade
```

#### Why Flask-Migrate?

Flask-Migrate is intentionally included in this educational project, despite the focus on simplicity. Here's the rationale:

**Problem it Solves:**
Without migrations, students would need to manually manage database schema changes through:
- Writing raw SQL `ALTER TABLE` statements
- Deleting and recreating the database (losing test data)
- Tracking changes across team members manually

**Educational Benefits:**
1. **Industry Standard**: Flask-Migrate (Alembic) is used in virtually all production Flask applications
2. **Readable Code**: Generated migration files are simple Python code that teaches schema evolution
3. **Simple Interface**: Only 3 commands to learn (`migrate`, `upgrade`, `downgrade`)
4. **Safety Net**: Provides rollback capability and prevents common beginner mistakes
5. **Transferable Skill**: Similar patterns exist in Django, Rails, and other frameworks

**Example Migration File:**
```python
# migrations/versions/abc123_add_bio_field.py
def upgrade():
    op.add_column('scribes', sa.Column('bio', sa.String(500)))

def downgrade():
    op.drop_column('scribes', 'bio')
```

Students can read these files to understand how schema changes work under the hood, making it educational rather than "magical."

**Alternative Would Be Worse:**
Instructing students to delete `logbook.db` on every model change would:
- Create bad habits for real-world development
- Cause frustration when test data is lost
- Provide no learning value about database evolution

### Testing
When tests are added:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_file.py

# Run with coverage
pytest --cov=app tests/
```

## Flask API Patterns

### Application Factory Pattern
Use the application factory pattern for better testability:
```python
def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration directly from environment variables
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'SQLALCHEMY_DATABASE_URI', 'sqlite:///logbook.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False

    # Testing mode uses in-memory database
    if os.getenv('TESTING') == 'true':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register API blueprint (future)
    # from app.api import api_bp
    # app.register_blueprint(api_bp, url_prefix='/api')

    return app
```

### Configuration Management
Configuration uses environment variables directly for simplicity and clarity:

**Environment Variables:**
- `FLASK_APP`: Application entry point (for Flask CLI)
- `FLASK_DEBUG`: Debug mode (1=on, 0=off) - controls Flask's debugger and auto-reload
- `SECRET_KEY`: Security key for sessions/tokens
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `TESTING`: Set to "true" to use in-memory SQLite database for tests

**Development (.env file):**
```bash
FLASK_APP=apiserver/run.py
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-me
SQLALCHEMY_DATABASE_URI=sqlite:///logbook.db
```

**Production (platform environment variables):**
```bash
# Set these through your hosting platform, NOT .env files
FLASK_APP=apiserver/run.py
FLASK_DEBUG=0
SECRET_KEY=<strong-random-production-key>
SQLALCHEMY_DATABASE_URI=<production-database-url>
```

**Why Direct Environment Variables?**
This approach prioritizes clarity over abstraction:
- Students see exactly where configuration comes from
- No config class selection logic to understand
- Standard pattern used in modern Flask applications
- Follows the 12-factor app methodology
- Simpler for educational purposes

### Production Deployment

**IMPORTANT:** `.env` files are for **local development only**. Production environments should set environment variables through their hosting platform.

**Required Production Environment Variables:**
```bash
FLASK_APP=apiserver/run.py
FLASK_DEBUG=0                      # CRITICAL: Must be 0 or false
SECRET_KEY=<strong-random-key>     # CRITICAL: Must be changed!
SQLALCHEMY_DATABASE_URI=<production-database-url>
```

**Platform Examples:**

**Heroku:**
```bash
heroku config:set FLASK_DEBUG=0
heroku config:set SECRET_KEY=your-strong-random-key
heroku config:set SQLALCHEMY_DATABASE_URI=postgresql://...
```

**Docker:**
```bash
docker run -e FLASK_DEBUG=0 -e SECRET_KEY=xxx ...
```

**Kubernetes:**
```yaml
env:
  - name: FLASK_DEBUG
    value: "0"
  - name: SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: app-secrets
        key: secret-key
```

**Security Notes:**
- ✅ NEVER commit `.env` to version control
- ✅ NEVER use development `SECRET_KEY` in production
- ✅ ALWAYS set `FLASK_DEBUG=0` in production
- ✅ Use strong, randomly generated `SECRET_KEY` (e.g., `python -c "import secrets; print(secrets.token_hex(32))"`)
- ✅ Use managed database services in production (not SQLite)
- ✅ Use secrets management services (AWS Secrets Manager, Azure Key Vault) for sensitive values

### API Blueprint Organization
All API endpoints are organized under a single `api` blueprint with modular route files:

- **Auth routes** (`apiserver/api/auth.py`): POST /enlist, POST /unlock, POST /lock
- **Scribe routes** (`apiserver/api/users.py`): GET /scribes/:id, PATCH /scribes/:id, DELETE /scribes/:id
- **Entry routes** (`apiserver/api/posts.py`): POST /entries, GET /entries/:id, PATCH /entries/:id, DELETE /entries/:id, GET /chronicle

All endpoints follow the **JSON:API v1.1 specification** for consistent, industry-standard responses:

```python
# Success response (200, 201)
{
    "data": {
        "type": "scribes",
        "id": "123",
        "attributes": {
            "username": "alice",
            "email": "alice@example.com",
            "bio": null,
            "createdAt": "2025-01-15T10:30:00Z"
        }
    }
}

# Error response (400, 401, 403, 404, etc.)
{
    "errors": [{
        "status": "401",
        "title": "Authentication Required",
        "detail": "You must provide valid credentials to access this resource"
    }]
}

# Empty success response for DELETE operations (204 No Content)
# Returns empty body with 204 status code
```

**Why JSON:API?**
- Industry standard specification used by many production APIs
- Teaches students proper REST/HTTP patterns
- Clear separation between data structure and HTTP semantics
- Emphasizes that HTTP status codes communicate success/failure, not the response body

## Database Design with SQLAlchemy

### Model Conventions
```python
from datetime import datetime
from typing import TYPE_CHECKING
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

class Scribe(db.Model):
    """Scribe account model.

    A Scribe is a user who documents their journey in Logbook.
    Stores authentication credentials and profile information.

    Password Security:
    - Uses Werkzeug's pbkdf2:sha256 with 260,000 iterations
    - Each password gets a unique randomly generated salt
    - Salt is embedded in password_hash: pbkdf2:sha256:260000$<salt>$<hash>
    - Salt length: 16 bytes (provides 128 bits of randomness)
    """
    __tablename__ = 'scribes'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    bio = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    entries = db.relationship('Entry', backref='scribe', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, username, email, bio=None):
        """Initialize a new Scribe instance.

        Args:
            username (str): Unique username for the scribe
            email (str): Unique email address for the scribe
            bio (str, optional): Short biography. Defaults to None.

        Note:
            Password must be set separately using set_password() method.
            The id, created_at, and updated_at fields are managed by SQLAlchemy.
        """
        self.username = username
        self.email = email
        self.bio = bio

    def set_password(self, password):
        """Hash and set the scribe's password.

        Uses pbkdf2:sha256 with a randomly generated 16-byte salt.
        The salt is embedded in the hash string stored in password_hash.
        """
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    def check_password(self, password):
        """Verify password against stored hash.

        Extracts the salt from password_hash and verifies the password.
        """
        return check_password_hash(self.password_hash, password)

    def to_jsonapi(self):
        """Return scribe data in JSON:API format."""
        return {
            'type': 'scribes',
            'id': str(self.id),
            'attributes': {
                'username': self.username,
                'email': self.email,
                'bio': self.bio,
                'createdAt': self.created_at.isoformat() + 'Z',
                'updatedAt': self.updated_at.isoformat() + 'Z'
            }
        }

    def __repr__(self):
        return f'<Scribe {self.username}>'


class Entry(db.Model):
    """Entry model.

    An Entry represents a purposeful record in a Scribe's Chronicle.
    Stores content and visibility settings.
    """
    __tablename__ = 'entries'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    visibility = db.Column(db.String(10), nullable=False, default='public')  # 'public' or 'private'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    scribe_id = db.Column(db.Integer, db.ForeignKey('scribes.id'), nullable=False, index=True)

    # Type hint for backref relationship (created by Scribe.entries relationship)
    if TYPE_CHECKING:
        scribe: "Scribe"

    def __init__(self, content, scribe_id, visibility="public"):
        """Initialize a new Entry instance.

        Args:
            content (str): The text content of the entry
            scribe_id (int): The ID of the scribe who created this entry
            visibility (str, optional): Visibility setting ('public' or 'private').
                                       Defaults to 'public'.

        Note:
            The id, created_at, and updated_at fields are managed by SQLAlchemy.
        """
        self.content = content
        self.scribe_id = scribe_id
        self.visibility = visibility

    def to_jsonapi(self):
        """Return entry data in JSON:API format."""
        return {
            'type': 'entries',
            'id': str(self.id),
            'attributes': {
                'content': self.content,
                'visibility': self.visibility,
                'createdAt': self.created_at.isoformat(),
                'updatedAt': self.updated_at.isoformat(),
                'scribeId': self.scribe_id,
                'scribeUsername': self.scribe.username
            }
        }

    def __repr__(self):
        return f'<Entry {self.id} by {self.scribe_id}>'
```

### Key Principles:
- Use clear, descriptive table and column names
- Add indexes on frequently queried columns (scribe_id, username, email)
- Include `created_at` and `updated_at` timestamps on all models
- Use appropriate SQLAlchemy types
- Define relationships explicitly with cascade rules
- **Add explicit `__init__` methods**: Define constructor methods that accept model fields as parameters. This makes the API clear to students, fixes IDE type warnings, and documents what parameters are expected. SQLAlchemy auto-generates constructors, but explicit ones improve clarity and maintainability.
- **Use TYPE_CHECKING for backref type hints**: Add type hints for SQLAlchemy backref relationships inside `if TYPE_CHECKING:` blocks to prevent IDE circular dependency warnings without runtime overhead
- Add `to_jsonapi()` methods that return JSON:API resource objects with `type`, `id`, and `attributes`
- Use camelCase for JSON attribute names (JSON:API convention) even though Python uses snake_case
- Add 'Z' suffix to ISO timestamps to indicate UTC timezone
- Add helpful `__repr__` methods
- Include business logic methods (set_password, check_password) in models
- Use salt-based password hashing with explicit configuration (pbkdf2:sha256, 16-byte salt)

## Security Considerations

Always implement these security practices for the API:

- **Password Hashing**: ✓ Implemented using `werkzeug.security.generate_password_hash()` with pbkdf2:sha256, 260,000 iterations, and 16-byte salt
- **Salt Storage**: ✓ Salt is embedded in password_hash (format: `pbkdf2:sha256:260000$<salt>$<hash>`)
- **Secret Key**: Set a strong `SECRET_KEY` via environment variable (currently using dev default)
- **Input Validation**: Validate and sanitize all user inputs before processing (TODO)
- **SQL Injection**: Always use parameterized queries (SQLAlchemy handles this automatically)
- **Authentication**: Use HTTP Basic Auth with secure password handling (TODO)
- **Authorization**: Verify scribe ownership before allowing updates/deletes (TODO)
- **Rate Limiting**: Consider adding rate limiting for production (future enhancement)
- **HTTPS**: Always use HTTPS in production to protect credentials in transit

## Code Quality Standards

### Documentation
- Include module docstrings at the top of each file
- Add docstrings to all classes and functions
- Document parameters, return values, and exceptions
- Explain complex algorithms or business logic

### Error Handling
- Use try-except blocks for operations that might fail
- Provide meaningful error messages
- Log errors appropriately
- Return user-friendly error responses

### Testing
- Write tests for all new features
- Test both success and failure cases
- Use meaningful test names that describe what's being tested
- Keep tests simple and focused

## Dependencies

Core dependencies (from requirements.txt):
- Flask: Web framework
- SQLAlchemy: ORM for database operations
- Flask-SQLAlchemy: Flask integration for SQLAlchemy
- Flask-Migrate: Database migration support
- Werkzeug: WSGI utilities and security helpers (password hashing, Basic Auth)
- Click: CLI creation
- Honcho: Procfile-based process management
- Blinker: Signal support for Flask

## When Adding New Features

1. **Plan the feature**: Think through the data model, API endpoints, and request/response formats
2. **Update models**: Add or modify SQLAlchemy models in `models.py`
3. **Create migration**: Run `flask db migrate -m "description"` and `flask db upgrade`
4. **Implement routes**: Add API endpoint functions to appropriate file in `apiserver/api/`
5. **Add validation**: Validate input data and return appropriate error responses
6. **Write tests**: Add tests for the new functionality (future)
7. **Update documentation**: Update README with new endpoints and add docstrings
8. **Format code**: Run `black .` before committing

## Common API Patterns

### Basic Authentication Decorator
```python
# apiserver/auth.py
from functools import wraps
from flask import request, jsonify
from .models import Scribe

def require_auth(f):
    """Decorator to require HTTP Basic Authentication.

    Returns JSON:API error responses for authentication failures.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return jsonify({
                'errors': [{
                    'status': '401',
                    'title': 'Authentication Required',
                    'detail': 'You must provide valid credentials to access this resource'
                }]
            }), 401

        scribe = Scribe.query.filter_by(username=auth.username).first()
        if not scribe or not scribe.check_password(auth.password):
            return jsonify({
                'errors': [{
                    'status': '401',
                    'title': 'Invalid Credentials',
                    'detail': 'The username or password provided is incorrect'
                }]
            }), 401

        # Pass authenticated scribe to the route function
        return f(scribe, *args, **kwargs)

    return decorated_function
```

### API Endpoint Pattern
```python
from flask import request, jsonify
from . import api_bp
from ..auth import require_auth
from ..models import Entry
from ..extensions import db

@api_bp.route('/entries', methods=['POST'])
@require_auth
def create_entry(current_scribe):
    """Create a new entry for the authenticated scribe.

    Returns JSON:API formatted response with 201 status on success.
    """
    data = request.get_json()

    # Validate input
    if not data or 'content' not in data:
        return jsonify({
            'errors': [{
                'status': '400',
                'title': 'Missing Required Field',
                'detail': 'The content field is required'
            }]
        }), 400

    # Create entry
    entry = Entry(
        content=data['content'],
        visibility=data.get('visibility', 'public'),
        scribe_id=current_scribe.id
    )

    db.session.add(entry)
    db.session.commit()

    # Return JSON:API formatted resource
    return jsonify({'data': entry.to_jsonapi()}), 201
```

### Database Queries
```python
# Get scribe's entries in chronological order
entries = Entry.query.filter_by(scribe_id=scribe_id).order_by(Entry.created_at.desc()).all()

# Convert to JSON:API formatted list
entries_data = [entry.to_jsonapi() for entry in entries]

# Return as JSON:API response
return jsonify({'data': entries_data}), 200
```

## Quick Reference

### API Endpoints Summary

**Authentication:**
- `POST /api/auth/enlist` - Enlist new scribe
- `POST /api/auth/unlock` - Verify credentials (Basic Auth)
- `POST /api/auth/lock` - Lock logbook (Basic Auth)

**Scribes:**
- `GET /api/scribes/<id>` - Get scribe profile (public)
- `PATCH /api/scribes/<id>` - Amend own profile (Basic Auth)
- `DELETE /api/scribes/<id>` - Retire own account (Basic Auth)

**Entries:**
- `POST /api/entries` - Create entry (Basic Auth)
- `GET /api/entries/<id>` - Get entry (Auth for private entries)
- `PATCH /api/entries/<id>` - Update own entry (Basic Auth)
- `DELETE /api/entries/<id>` - Delete own entry (Basic Auth)
- `GET /api/chronicle` - Get own chronicle (Basic Auth)

**Note:** PATCH is used for partial updates (JSON:API convention) instead of PUT which requires full resource replacement.

### Response Format

All responses follow the **JSON:API v1.1 specification**:

**Single Resource (GET, POST, PATCH):**
```json
{
  "data": {
    "type": "scribes",
    "id": "123",
    "attributes": {
      "username": "alice",
      "email": "alice@example.com",
      "bio": "Learning to code!",
      "createdAt": "2025-01-15T10:30:00Z"
    }
  }
}
```

**Collection of Resources (GET):**
```json
{
  "data": [
    {
      "type": "entries",
      "id": "1",
      "attributes": {
        "content": "My first entry!",
        "visibility": "public",
        "createdAt": "2025-01-15T10:30:00Z",
        "updatedAt": "2025-01-15T10:30:00Z",
        "scribeId": 123,
        "scribeUsername": "alice"
      }
    }
  ]
}
```

**Error Response (4xx, 5xx):**
```json
{
  "errors": [
    {
      "status": "401",
      "title": "Authentication Required",
      "detail": "You must provide valid credentials to access this resource"
    }
  ]
}
```

**Empty Success (DELETE):**
- Returns 204 No Content with empty body

**Key Points:**
- HTTP status codes indicate success/failure, NOT the response body
- All resource objects have `type`, `id`, and `attributes` fields
- ID is always a string (JSON:API requirement)
- Use camelCase for attribute names (JSON:API convention)
- Errors is always an array (can have multiple errors)
- Error objects include `status` (as string), `title`, and `detail` fields

### HTTP Status Codes

Understanding HTTP status codes is essential for API design. The status code **is** the success/failure indicator - the response body provides details.

**2xx Success:**
- `200 OK` - Successful GET or PATCH request, returns resource in response body
- `201 Created` - Successful POST request, returns created resource in response body
- `204 No Content` - Successful DELETE request, returns empty response body

**4xx Client Errors:**
- `400 Bad Request` - Invalid input data (missing required fields, invalid format, etc.)
- `401 Unauthorized` - Authentication required or credentials are invalid
- `403 Forbidden` - Authenticated but not authorized to access/modify this resource
- `404 Not Found` - Requested resource does not exist
- `409 Conflict` - Request conflicts with current state (e.g., username already exists)

**5xx Server Errors:**
- `500 Internal Server Error` - Unexpected server error (database connection failed, unhandled exception, etc.)

**Educational Notes:**
- **401 vs 403**: Use 401 when credentials are missing/invalid. Use 403 when credentials are valid but the user lacks permission.
- **404 vs 403**: Use 404 for non-existent resources. Some APIs use 403 to hide resource existence, but for educational clarity we use 404.
- **PUT vs PATCH**: JSON:API uses PATCH for partial updates. PUT would require sending the entire resource.
- Students should **always check the status code first** before parsing the response body.

### Testing with curl

```bash
# Enlist a new scribe (returns 201 Created)
curl -X POST http://localhost:5000/api/auth/enlist \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.api+json" \
  -d '{"username": "test", "email": "test@example.com", "password": "pass123"}'

# Expected Response (201):
# {
#   "data": {
#     "type": "scribes",
#     "id": "1",
#     "attributes": {
#       "username": "test",
#       "email": "test@example.com",
#       "bio": null,
#       "createdAt": "2025-01-15T10:30:00Z"
#     }
#   }
# }

# Create entry with Basic Auth (returns 201 Created)
curl -X POST http://localhost:5000/api/entries \
  -u test:pass123 \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.api+json" \
  -d '{"content": "Hello from Logbook!", "visibility": "public"}'

# Expected Response (201):
# {
#   "data": {
#     "type": "entries",
#     "id": "1",
#     "attributes": {
#       "content": "Hello from Logbook!",
#       "visibility": "public",
#       "createdAt": "2025-01-15T10:30:00Z",
#       "updatedAt": "2025-01-15T10:30:00Z",
#       "scribeId": 1,
#       "scribeUsername": "test"
#     }
#   }
# }

# Get chronicle (returns 200 OK with array of entries)
curl -X GET http://localhost:5000/api/chronicle \
  -u test:pass123 \
  -H "Accept: application/vnd.api+json"

# Expected Response (200):
# {
#   "data": [
#     {
#       "type": "entries",
#       "id": "1",
#       "attributes": { ... }
#     }
#   ]
# }

# Delete an entry (returns 204 No Content with empty body)
curl -X DELETE http://localhost:5000/api/entries/1 \
  -u test:pass123 \
  -i  # -i flag shows headers including 204 status

# Testing error responses (returns 401 Unauthorized)
curl -X GET http://localhost:5000/api/chronicle \
  -H "Accept: application/vnd.api+json"

# Expected Response (401):
# {
#   "errors": [{
#     "status": "401",
#     "title": "Authentication Required",
#     "detail": "You must provide valid credentials to access this resource"
#   }]
# }

# Pro tip: Add -i flag to see HTTP status codes in curl responses
# Example: curl -i http://localhost:5000/health
```

## License

Apache License 2.0
