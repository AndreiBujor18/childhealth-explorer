"""Composition root: wire sessions, repositories and services through Depends."""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.observation_repository import ObservationRepository
from app.services.observation_service import ObservationService
from app.services.etl_service import EtlService
from app.database import get_session_factory
from etl.jobs import extraction_jobs, import_jobs
from threading import Lock

PIPELINE_LOCK = Lock()


def get_observation_service(session: Annotated[Session, Depends(get_db)]) -> ObservationService:
    return ObservationService(ObservationRepository(session))


def get_etl_service() -> EtlService:
    return EtlService(extraction_jobs(), import_jobs(get_session_factory()), lock=PIPELINE_LOCK)
