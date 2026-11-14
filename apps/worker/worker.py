"""
ARQ Worker configuration and lifecycle entry point.
"""

from arq.connections import RedisSettings
from apps.api.config import settings
from apps.worker.tasks import (
    preprocess_drawing_task,
    extract_and_reconcile_task,
    build_cad_geometry_task,
)


async def startup(ctx):
    """Worker process startup initialization."""
    pass


async def shutdown(ctx):
    """Worker process graceful shutdown."""
    pass


class WorkerSettings:
    """ARQ Worker runtime settings."""
    functions = [
        preprocess_drawing_task,
        extract_and_reconcile_task,
        build_cad_geometry_task,
    ]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 10
    job_timeout = 300  # 5 minutes maximum runtime per job
