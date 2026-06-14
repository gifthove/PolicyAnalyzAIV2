import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes.documents import router as documents_router
from app.routes.health import router as health_router
from app.routes.query import router as query_router
from app.routes.user import router as user_router
from app.services import search_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        search_service.ensure_index_exists()
    except Exception as exc:
        logger.warning("Search index setup skipped at startup: %s", exc)
    yield


app = FastAPI(title="PolicyAnalyzAI v2", lifespan=lifespan)
app.include_router(health_router)
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(documents_router)
app.include_router(query_router)
