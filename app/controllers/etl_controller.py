"""POST controllers render service outcomes; no extraction or database code."""
from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.dependencies import get_etl_service
from app.services.etl_service import EtlService
from app.views import templates

router = APIRouter(prefix='/actions')


@router.post('/extract', response_class=HTMLResponse)
def extract(request: Request, service: Annotated[EtlService, Depends(get_etl_service)]):
    return templates.TemplateResponse(request, 'action_result.html', {
        'action': 'Extract', 'description': 'Fresh source files were requested for every study indicator.',
        'result': service.extract_all(), 'is_load': False,
    })


@router.post('/load', response_class=HTMLResponse)
def transform_and_load(request: Request, service: Annotated[EtlService, Depends(get_etl_service)]):
    return templates.TemplateResponse(request, 'action_result.html', {
        'action': 'Transform & load', 'description': 'Saved source files were transformed, cleaned and imported.',
        'result': service.transform_and_load_all(), 'is_load': True,
    })
