"""
Pytest configuration for production backend tests.

Provides a shared SQLite in-memory database fixture that patches SessionLocal
so tests can run without a real PostgreSQL instance.
"""
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

SQLITE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def sqlite_engine():
    from app.database.base import Base
    engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def enable_fk(dbapi_conn, _record):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def sqlite_session_factory(sqlite_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)


@pytest.fixture
def db_session(sqlite_session_factory, monkeypatch):
    """
    Fresh SQLite session per test. Patches SessionLocal module-level so
    services/repositories that call SessionLocal() get the test DB.
    """
    from app.database import database as db_module
    monkeypatch.setattr(db_module, "SessionLocal", sqlite_session_factory)
    session = sqlite_session_factory()
    yield session
    session.rollback()
    session.close()
