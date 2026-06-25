"""Database infrastructure package.

Purpose: expose PostgreSQL infrastructure primitives.
Responsibilities: engine, sessions, transactions, health checks.
Dependencies: SQLAlchemy and application settings.
Extension Notes: keep ORM models in database.models, not this package root.
"""
