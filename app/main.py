from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.user import router as user_router
from app.routes.documents import router as documents_router

app = FastAPI(title="PolicyAnalyzAI v2")
app.include_router(health_router)
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(documents_router)    