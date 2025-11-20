from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
# Importing all router modules
from .api.routes import auth, documents, emails, erp, health, kyc
from .services import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    await database.init_db()
    
    # Test Odoo connection on startup
    try:
        from .services.erp_service import _odoo_client
        if _odoo_client.authenticate():
            print(f"✅ Connected to Odoo database: {_odoo_client.db}")
        else:
            print("⚠️ Failed to connect to Odoo - ERP features may not work")
    except Exception as e:
        print(f"⚠️ Odoo connection error: {e}")
    
    yield

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="JupiterBrains AI Demo with Odoo ERP Integration",
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

# KYC Complete Workflow (MAIN FEATURE)
app.include_router(kyc.router)         # Complete KYC automation workflow

# Individual KYC Feature Routes (for standalone demos)
app.include_router(emails.router)      # Individual email classification
app.include_router(documents.router)  # Individual document extraction + tamper detection
app.include_router(erp.router)        # ERP integration with Odoo

@app.get("/", tags=["root"])
async def root():
    return {
        "message": f"{settings.app_name} is running",
        "features": ["Email Classification", "Document Processing", "Odoo ERP Integration"],
        "version": "1.0.0"
    }