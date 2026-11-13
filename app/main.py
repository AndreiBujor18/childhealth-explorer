"""Create the server-rendered application and register presentation routes."""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from app.controllers import observation_controller
from app.views import templates


def create_app():
    app = FastAPI(title='ChildHealth Explorer', openapi_url=None, docs_url=None, redoc_url=None)
    app.mount('/static', StaticFiles(directory=str(Path(__file__).parent / 'static')), name='static')
    app.include_router(observation_controller.router)

    @app.exception_handler(ValueError)
    async def invalid_filters(request: Request, error: ValueError):
        return templates.TemplateResponse(request, 'error.html', {'message': str(error)}, status_code=400)

    return app


app = create_app()
