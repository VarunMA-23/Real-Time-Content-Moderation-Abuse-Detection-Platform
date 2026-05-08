"""Test configuration and fixtures for integration tests."""
import os
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base_class import Base


@pytest.fixture(scope="session")
def engine():
    """Create a test database engine."""
    # Use SQLite for testing (in-memory)
    test_db_url = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
    return create_engine(
        test_db_url,
        connect_args={"check_same_thread": False} if "sqlite" in test_db_url else {},
        poolclass=StaticPool,
    )


@pytest.fixture(scope="session")
def tables(engine):
    """Create all tables for testing."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_tables(engine, tables):
    """Clean all tables before each test to ensure isolation."""
    with engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()
    yield


@pytest.fixture
def db_session(engine, tables, clean_tables):
    """Create a new database session for each test."""
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def db(db_session):
    """Alias for db_session to match existing code patterns."""
    yield db_session
