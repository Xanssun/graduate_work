from datetime import datetime as dt
from http import HTTPStatus
from logging import config as logging_config

import core.tracer as tracer
import uvicorn
from api.v1 import auth, oauth, roles, user_role
from core.logger import LOGGING
from core.settings import settings
from db import redis
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis

app = FastAPI(
    title='API авторизаций',
    docs_url='/auth_api/openapi',
    openapi_url='/auth_api/openapi.json',
    default_response_class=JSONResponse,
)

if settings.with_jaeger:
    tracer.configure_tracer()
    FastAPIInstrumentor.instrument_app(app)

app.include_router(auth.router, prefix='/auth_api/v1/auth', tags=['auth'])
app.include_router(oauth.router, prefix='/auth_api/v1/oauth', tags=['oauth'])

app.include_router(roles.router, prefix='/auth_api/v1/roles', tags=['roles'])
app.include_router(
    user_role.router, prefix='/auth_api/v1/users_roles', tags=['users_roles']
)


@app.middleware('http')
async def rate_limit_middleware(request: Request, call_next):
    pipe = redis.redis.pipeline()
    now = dt.now()
    remote_addr = request.headers.get('X-Real-IP')
    request_id = request.headers.get('X-Request-Id')

    if not request_id and settings.with_jaeger:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={'detail': 'X-Request-Id is required'},
        )

    if not request_id == 'pytest':
        key = f'{remote_addr}:{now.minute}'
        pipe.incr(key, 1)
        pipe.expire(key, 59)
        result = await pipe.execute()
        request_number = result[0]

        if request_number > settings.max_requests_per_minute:
            return JSONResponse(
                status_code=HTTPStatus.TOO_MANY_REQUESTS,
                content={'detail': 'User Rate Limit Exceeded'},
                headers={
                    'Retry-After': f'{60 - now.second}',
                    'X-Rate-Limit': f'{settings.max_requests_per_minute}',
                },
            )

    return await call_next(request)


if __name__ == '__main__':
    # Применяем настройки логирования
    logging_config.dictConfig(LOGGING)

    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    uvicorn.run(
        'main:app',
        host=settings.auth_api_host,
        port=settings.auth_api_port,
        log_config=LOGGING,
        log_level=settings.log_level,
    )
