"""Create the HTML application and its documented read-only JSON API."""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from app.controllers import observation_controller, etl_controller
from app.controllers.api import API_DOCS_URL, reference_data_api
from app.views import templates


def create_app():
    app = FastAPI(title='ChildHealth Explorer', openapi_url='/api/openapi.json',
                  docs_url=API_DOCS_URL, redoc_url=None)
    app.mount('/static', StaticFiles(directory=str(Path(__file__).parent / 'static')), name='static')
    app.include_router(observation_controller.router)
    app.include_router(etl_controller.router)
    app.include_router(reference_data_api.router)

    @app.exception_handler(ValueError)
    async def invalid_filters(request: Request, error: ValueError):
        return templates.TemplateResponse(request, 'error.html', {'message': str(error)}, status_code=400)

    return app


app = create_app()
