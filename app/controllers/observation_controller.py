"""Observation page: HTTP parsing and rendering only; no database imports."""
from typing import Annotated
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from app.controllers.form_fields import blank_to_none, to_int_or_none
from app.dependencies import get_observation_service
from app.domain import ObservationCriteria
from app.services.observation_service import ObservationService
from app.views import templates

router = APIRouter()


def observation_criteria(country: str | None = None, indicator: str | None = None,
                         region: str | None = None, year_from: str | None = None,
                         year_to: str | None = None, source: str | None = None) -> ObservationCriteria:
    return ObservationCriteria(country_iso3=blank_to_none(country), indicator_code=blank_to_none(indicator),
                               region=blank_to_none(region), year_from=to_int_or_none(year_from),
                               year_to=to_int_or_none(year_to), source_name=blank_to_none(source))


@router.get('/', response_class=HTMLResponse)
def show_observations(request: Request,
                      criteria: Annotated[ObservationCriteria, Depends(observation_criteria)],
                      service: Annotated[ObservationService, Depends(get_observation_service)],
                      page: Annotated[int, Query(ge=1)] = 1):
    observations = service.get_page(criteria, page)
    return templates.TemplateResponse(request, 'observations.html', {
        'observations': observations, 'criteria': criteria, 'options': service.get_filter_options(),
        'previous_url': str(request.url.include_query_params(page=observations.number - 1))
        if observations.has_previous else None,
        'next_url': str(request.url.include_query_params(page=observations.number + 1))
        if observations.has_next else None,
    })
