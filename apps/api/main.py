"""
Main FastAPI Application Entry Point for Sketch2STEP Enterprise.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.config import settings
from apps.api.database import engine
from apps.api.models.base import Base
from apps.api.routers import (
    health_router,
    auth_router,
    orgs_router,
    jobs_router,
    audit_router,
    billing_router,
    api_keys_router,
    webhooks_router,
    dimension_library_router,
    admin_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables created if development
    if settings.DEBUG:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="Precision 2D Engineering Drawing to Parametric 3D STEP Conversion SaaS",
    lifespan=lifespan,
)

# Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount health checks
app.include_router(health_router)

# Mount API v1 Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(orgs_router, prefix=settings.API_V1_PREFIX)
app.include_router(jobs_router, prefix=settings.API_V1_PREFIX)
app.include_router(audit_router, prefix=settings.API_V1_PREFIX)
app.include_router(billing_router, prefix=settings.API_V1_PREFIX)
app.include_router(api_keys_router, prefix=settings.API_V1_PREFIX)
app.include_router(webhooks_router, prefix=settings.API_V1_PREFIX)
app.include_router(dimension_library_router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "service": "Sketch2STEP Enterprise API",
        "status": "operational",
        "docs_url": "/docs",
        "accuracy_rule": "No dimension reaches STEP without cross-check or human sign-off"
    }
