from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.routes import auth, documents, emails, erp, health, responses
from .services import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    await database.init_db()
    yield

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
# ... include other routers ...

@app.get("/", tags=["root"])
async def root():
    return {"message": f"{settings.app_name} is running"}