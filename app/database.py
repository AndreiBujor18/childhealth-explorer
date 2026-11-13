"""PostgreSQL connection and database session helpers."""
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parent.parent


@lru_cache
def get_engine():
    load_dotenv(ROOT / '.env')
    url = os.getenv('DATABASE_URL')
    if not url:
        raise RuntimeError('Set DATABASE_URL in .env; see .env.example.')
    return create_engine(url, pool_pre_ping=True)


def get_db():
    with get_session_factory()() as db:
        yield db


def get_session_factory():
    return sessionmaker(bind=get_engine(), autoflush=False)
