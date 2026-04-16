from celery import Celery

from app.core.settings import settings


celery_app = Celery(
    "specification_generator",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.infrastructure.tasks.feature_spec_tasks"],
)

celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
