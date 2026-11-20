"""Read-only lookup routes; all data access goes through the observation service."""
from typing import Annotated
from fastapi import APIRouter, Depends
from app.controllers.api.schemas import CountryResponse, IndicatorResponse
from app.dependencies import get_observation_service
from app.services.observation_service import ObservationService

router = APIRouter(prefix='/api', tags=['reference data'])
Service = Annotated[ObservationService, Depends(get_observation_service)]


@router.get('/regions')
def list_regions(service: Service) -> list[str]:
    return [option.value for option in service.list_regions()]


@router.get('/countries')
def list_countries(service: Service, region: str | None = None) -> list[CountryResponse]:
    return [CountryResponse.from_option(option) for option in service.list_countries(region)]


@router.get('/indicators')
def list_indicators(service: Service) -> list[IndicatorResponse]:
    return [IndicatorResponse.from_option(option) for option in service.list_indicators()]
