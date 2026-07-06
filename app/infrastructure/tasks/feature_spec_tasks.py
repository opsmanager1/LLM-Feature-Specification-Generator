import httpx
from celery.exceptions import MaxRetriesExceededError

from app.core.database import SessionLocal
from app.core.settings import settings
from app.infrastructure.celery_app import celery_app
from app.modules.feature_spec.orchestrator import execute_feature_spec_run, mark_run_error


def _ensure_auth_models_loaded() -> None:
    from app.modules.auth import models as auth_models

    _ = auth_models.User


@celery_app.task(bind=True, name="feature_spec.generate")
def generate_feature_spec_task(self, run_id: int, feature_idea: str, user_id: int) -> dict:
    _ensure_auth_models_loaded()
    db = SessionLocal()
    try:
        return execute_feature_spec_run(run_id, feature_idea, db)
    except (
        httpx.TimeoutException,
        httpx.RequestError,
        httpx.HTTPStatusError,
    ) as exc:
        retry_number = int(self.request.retries) + 1
        if retry_number <= settings.CELERY_TASK_MAX_RETRIES:
            delay_seconds = settings.CELERY_TASK_RETRY_BASE_SECONDS**retry_number
            try:
                raise self.retry(exc=exc, countdown=delay_seconds)
            except MaxRetriesExceededError:
                pass

        db.rollback()
        mark_run_error(db, run_id, "LLM provider request failed")
        raise RuntimeError("LLM task failed after retries") from exc
    except Exception as exc:
        db.rollback()
        mark_run_error(db, run_id, "Failed to process feature specification")
        raise RuntimeError("Feature specification task failed") from exc
    finally:
        db.close()
