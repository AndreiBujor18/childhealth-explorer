"""Serve only the CSR shell: no service or database dependency."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.controllers.api import API_DOCS_URL
from app.services.period_average_service import DEFAULT_FIRST_YEAR, DEFAULT_LAST_YEAR
from app.views import templates

router = APIRouter(include_in_schema=False)


@router.get('/period-averages', response_class=HTMLResponse)
def show_period_averages(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, 'period_averages.html', {
        'first_year': DEFAULT_FIRST_YEAR, 'last_year': DEFAULT_LAST_YEAR,
        'max_countries': 8, 'api_docs_url': API_DOCS_URL,
    })
