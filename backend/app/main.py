"""FastAPI 应用入口。"""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from .config import API_PREFIX, APP_NAME, CORS_ORIGINS
from .database import Base, engine
from .api import history, overview, ranking, reports, tasks, varieties, views

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = FastAPI(title=APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (varieties, overview, views, history, ranking, reports, tasks):
    app.include_router(router.router, prefix=API_PREFIX)


@app.on_event("startup")
def on_startup():
    """本地 SQLite 自动建表；MySQL 环境请先执行 sql/01_create_tables.sql。"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("database ready")
    except Exception as exc:  # pragma: no cover
        logger.warning("create_all skipped: %s", exc)


@app.exception_handler(SQLAlchemyError)
async def db_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error("database error: %s", exc)
    return JSONResponse(
        status_code=503,
        content={"code": 503, "msg": "数据库暂时不可用，请稍后重试", "data": None},
    )


@app.get("/health")
def health():
    return {"code": 0, "msg": "ok", "data": {"status": "up"}}
