import uvicorn
from core.config import settings
from db.postgres import async_session
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

app = FastAPI(
    title='API кино вместе',
    docs_url='/kino_api/openapi',
    openapi_url='/kino_api/openapi.json',
    default_response_class=JSONResponse,
)

@app.get("/")
async def read_root():
    """Проверка соеденения, тестовая функция"""
    async with async_session() as session:
        try:
            await session.execute(text("SELECT 1"))
            return {"Соединение с базой данных установлено!"}
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": f"Ошибка подключения к базе данных: {str(e)}"})


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.kino_api_host,
        port=settings.kino_api_port,
        reload=True,
    )
