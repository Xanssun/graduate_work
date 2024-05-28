import uvicorn
from api.v1 import room
from core.config import settings
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(
    title='API кино вместе',
    docs_url='/kino_api/openapi',
    openapi_url='/kino_api/openapi.json',
    default_response_class=HTMLResponse,
)


app.include_router(room.router, prefix='/kino_api/v1/cinema', tags=['cinema'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.kino_api_host,
        port=settings.kino_api_port,
        reload=True,
    )
