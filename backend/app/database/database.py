"""
Database Configuration

Creates SQLAlchemy engine and session.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)