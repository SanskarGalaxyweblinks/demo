from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.routes import auth, documents, emails, erp, health, responses
from .services import database


database.init_db()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Backend services for the Jupiter AI workflow demo frontend.",
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
app.include_router(emails.router)
app.include_router(documents.router)
app.include_router(responses.router)
app.include_router(erp.router)


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """
    Provide a simple landing route so developers can verify the backend is reachable.
    """

    return {
        "message": f"{settings.app_name} is running",
        "docs": "/docs",
        "status": "ok",
    }


