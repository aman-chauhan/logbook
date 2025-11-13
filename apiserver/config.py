"""
Configuration module for Logbook API.

This module defines configuration classes for different environments
(development, production). Each configuration class sets up database
connections, security settings, and other Flask configuration options.
"""

import os


class Config:
    """Base configuration class with common settings."""

    # Security settings
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///logbook.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JSON settings
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    """Development configuration class."""

    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration class."""

    DEBUG = False
    TESTING = False

    # In production, SECRET_KEY must be set via environment variable
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")


class TestingConfig(Config):
    """Testing configuration class."""

    DEBUG = True
    TESTING = True

    # Use a separate in-memory database for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


configurations = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
