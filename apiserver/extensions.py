"""Flask extensions.

This module initializes Flask extensions that are shared across the application.
Extensions are initialized here and then configured in the application factory.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Database ORM
db = SQLAlchemy()

# Database migration manager
migrate = Migrate()
