"""Parse JSON requests and translate domain errors without accessing the database."""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from app.controllers.api.schemas import PeriodAveragesResponse
from app.dependencies import get_period_average_service
from app.domain import PeriodAverageQuery
from app.services.period_average_service import (DEFAULT_FIRST_YEAR, DEFAULT_LAST_YEAR, DEFAULT_PERIOD_YEARS,
                                                InvalidQueryError, PeriodAverageService, UnknownIndicatorError)

router = APIRouter(prefix='/api', tags=['period averages'])


def period_average_query(indicator_code: str,
                         country: Annotated[list[str] | None, Query(description='Repeat for each ISO3 code')] = None,
                         first_year: int = DEFAULT_FIRST_YEAR, last_year: int = DEFAULT_LAST_YEAR,
                         period_years: Annotated[int, Query(ge=1)] = DEFAULT_PERIOD_YEARS) -> PeriodAverageQuery:
    return PeriodAverageQuery(indicator_code, tuple(dict.fromkeys(country or ())),
                              first_year, last_year, period_years)


@router.get('/indicators/{indicator_code}/period-averages',
            responses={404: {'description': 'The indicator code does not exist.'}})
def get_period_averages(query: Annotated[PeriodAverageQuery, Depends(period_average_query)],
                        service: Annotated[PeriodAverageService, Depends(get_period_average_service)]
                        ) -> PeriodAveragesResponse:
    """Mean of available BTSX annual values, rounded half up to two decimals.

    Repeat country to select up to 20 distinct uppercase ISO3 codes. Omit it for
    an empty series list. Years must be ordered within 1900-2100. Known countries
    with missing periods retain nulls; invalid queries return JSON 422.
    """
    try:
        report = service.get_report(query)
    except UnknownIndicatorError as error:
        raise HTTPException(404, str(error)) from error
    except InvalidQueryError as error:
        raise HTTPException(422, str(error)) from error
    return PeriodAveragesResponse.from_domain(report)
