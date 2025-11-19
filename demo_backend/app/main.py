from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
# Importing all router modules
from .api.routes import auth, documents, emails, erp, health
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

# --- Registering Routes ---
# Core System Routes
app.include_router(health.router)
app.include_router(auth.router)

# KYC Feature Routes
app.include_router(emails.router)      # KYC email classification
app.include_router(documents.router)  # Document extraction + tamper detection
app.include_router(erp.router)        # Customer records management

@app.get("/", tags=["root"])
async def root():
    return {"message": f"{settings.app_name} is running"}